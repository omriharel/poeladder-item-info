import argparse
import copy
import logging
import os
import subprocess

from utils import iterate_yaml_files, load_yaml_file, save_output_json, build_edit_link, trim_basedir
from constants import Constants
from reporting import ErrorReporter


class DataBuilder:
    def __init__(self, args):
        self._input_dir = args.input
        self._consumables_dir = args.consumables
        self._item_schema = args.item_schema
        self._common_schemas_glob = args.common_schemas_glob
        self._output_file = args.output
        self._error_reporter = ErrorReporter(args.comment_output)

        self._loaded_consumables = None

    def run(self):
        self.load_consumable_files()
        self.validate_item_files()
        composed_data = self.load_files_and_build_composed_data()
        save_output_json(composed_data, self._output_file)

    def validate_item_files(self):
        validation_errors = []

        for filename in iterate_yaml_files(self._input_dir):
            logging.info("Running ajv for %s...", filename)
            ajv_command = [
                "ajv",
                "-s",
                self._item_schema,
                "-r",
                self._common_schemas_glob,
                "-d",
                filename,
                "--spec=draft2020",
                "--errors=text",
            ]

            logging.debug("Running command: %s", " ".join(ajv_command))
            with subprocess.Popen(ajv_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:

                stdout, stderr = process.communicate()
                process.wait()

                stdout = stdout.decode("utf-8")
                stderr = stderr.decode("utf-8")

                if process.returncode not in [0, 1]:
                    logging.error("Error running ajv (args: %s)", ajv_command)
                    logging.debug("stdout: %s", stdout)
                    logging.debug("stderr: %s", stderr)
                    raise SystemExit(1)

                if stderr:
                    logging.warning("Validation error in %s! Details:\n%s", filename, stderr)
                    validation_errors.append((filename, stderr))

        if validation_errors:
            self._error_reporter.report_ajv_errors(validation_errors, self._input_dir, self._item_schema)

    def load_consumable_files(self):
        self._loaded_consumables = {}

        for filename in iterate_yaml_files(self._consumables_dir):
            file_consumables = load_yaml_file(filename)

            for consumable_key, consumable_data in file_consumables.items():
                self._loaded_consumables[consumable_key] = consumable_data

        if self._loaded_consumables:
            logging.info("Loaded %d consumable data entries", len(self._loaded_consumables))
        else:
            logging.info("No consumable data found")

    def load_files_and_build_composed_data(self):
        composed_data = {}
        filenames = list(iterate_yaml_files(self._input_dir))
        for filename in filenames:
            item_data = load_yaml_file(filename)

            # expand item variants if they exist in data
            if "variants" in item_data:
                for variant_name, variant_data in item_data["variants"].items():
                    composed_data[self._build_item_name_key(filename, variant_name)] = self._enrich_item_data(
                        filename, variant_data
                    )
            else:
                composed_data[self._build_item_name_key(filename)] = self._enrich_item_data(filename, item_data)

        logging.info(
            "Built composed data for %d total item entries (including variants) from %d item files",
            len(composed_data),
            len(filenames),
        )

        return composed_data

    @staticmethod
    def _build_item_name_key(filename, variant_name=None):

        # filename is usually structured like <input_dir>/<class>/<item_name>.yml
        # trim away dirname and extension, for example: items/belts/Mageblood.yml -> Mageblood
        base_item_name = os.path.basename(filename)[:-4]

        # some special items must be mapped to a different item key than their original filename,
        # due to some filenames being illegal on some platforms
        if base_item_name in Constants.all_unique_contracts:
            base_item_name = f"Contract: {base_item_name}"

        # variants follow a slightly different naming structure. e.g. "Combat Focus (Fire)"
        if variant_name is not None:
            return f"{base_item_name} ({variant_name})"

        return base_item_name

    def _enrich_item_data(self, filename, item_data):
        enriched_data = copy.deepcopy(item_data)

        for acquisition_method in enriched_data["acquisitionMethods"]:
            consumable = acquisition_method.get("consumable")
            needs_resolution = consumable and consumable.get("id") is not None

            if needs_resolution:
                acquisition_method["consumable"] = self._resolve_consumable_reference(consumable, filename)

        enriched_data["editLink"] = build_edit_link(filename)

        return enriched_data

    def _resolve_consumable_reference(self, consumable, filename):
        consumable_id = consumable["id"]
        consumable_data = self._loaded_consumables.get(consumable_id)

        if not consumable_data:
            logging.warning("Consumable reference '%s' not found for filename %s", consumable_id, filename)

            error_message = (
                f"File `{trim_basedir(filename, self._input_dir)}` references a named consumable"
                + f" (`{consumable_id}`) which doesn't exist. Please ensure you're using the correct"
                + " internal ID or put your consumable data inline."
            )
            self._error_reporter.report_general_error(error_message)

        logging.debug("Resolved consumable with ID '%s' for filename %s", consumable_id, filename)

        return consumable_data


def main(args):
    logging.basicConfig(level=logging.DEBUG)
    data_builder = DataBuilder(args)

    data_builder.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="poeladder item info composer")
    parser.add_argument("-i", "--input", help="input directory of item data YAML files", required=True)
    parser.add_argument("-c", "--consumables", help="input directory of consumable data YAML files", required=True)
    parser.add_argument("-is", "--item-schema", help="path to single item schema file", required=True)
    parser.add_argument("-csg", "--common-schemas-glob", help="glob for referenced common schemas", required=True)
    parser.add_argument("-o", "--output", help="output JSON file", required=True)
    parser.add_argument("-co", "--comment-output", help="output file for pull request comments", required=True)

    main(parser.parse_args())
