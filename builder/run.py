import argparse
import copy
import logging
import os
import subprocess
import textwrap

from utils import (
    iterate_yaml_files,
    load_raw_file,
    load_yaml_file,
    save_output_json,
    trim_basedir,
    build_edit_link,
    build_item_schema_link,
)


class DataBuilder:
    def __init__(self, args):
        self._input_dir = args.input
        self._item_schema = args.item_schema
        self._output_file = args.output
        self._comment_output_file = args.comment_output

    def run(self):
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
            logging.error("Validation error in %s file(s) - quitting", len(validation_errors))
            failing_filenames = ", ".join([trim_basedir(error[0], self._input_dir) for error in validation_errors])
            print(
                f"The following file(s) failed to validate - please fix them to match the schema: {failing_filenames}"
            )
            self._save_validation_errors(validation_errors)
            raise SystemExit(1)

    def load_files_and_build_composed_data(self):
        composed_data = {}
        filenames = list(iterate_yaml_files(self._input_dir))
        for filename in filenames:
            item_data = load_yaml_file(filename)

            # trim away .yml suffix
            raw_item_key = os.path.basename(filename)[:-4]

            # expand item variants if they exist in data
            if "variants" in item_data:
                for variant_name, variant_data in item_data["variants"].items():
                    composed_data[f"{raw_item_key} ({variant_name})"] = self._enrich_item_data(filename, variant_data)
            else:
                composed_data[raw_item_key] = self._enrich_item_data(filename, item_data)

        logging.info(
            "Built composed data for %s total item entries (including variants) from %s item files",
            len(composed_data),
            len(filenames),
        )

        return composed_data

    def _enrich_item_data(self, filename, item_data):
        enriched_data = copy.deepcopy(item_data)
        enriched_data["editLink"] = build_edit_link(filename)

        return enriched_data

    def _save_validation_errors(self, validation_errors):
        lines = [
            "❌",
            "",
            "Some file(s) changed/added in this PR don't adhere to the [item data schema]"
            + f"({build_item_schema_link(self._item_schema)}). Please fix the errors detailed below for each file:",
            "",
        ]

        for filename, ajv_stderr in validation_errors:

            # trim out first line a-la "../items/belts/Headhunter.yml invalid"
            ajv_errors = "\n".join(ajv_stderr.strip().split("\n")[1:]).split(", ")
            formatted_errors = "\n".join(["Errors:"] + [f"• {err}" for err in ajv_errors])

            lines.extend(
                [
                    f"- `{trim_basedir(filename, self._input_dir)}`:",
                    textwrap.indent(f"```yaml\n{load_raw_file(filename).strip()}\n```", "  "),
                    textwrap.indent(f"```\n{formatted_errors}\n```", "  "),
                ]
            )

        self._write_comment_output("\n".join(lines))

    def _write_comment_output(self, text):
        with open(self._comment_output_file, "w", encoding="utf-8") as f:
            f.write(text)
            logging.info(
                "Written pull request comment output to %s (%d lines in total)",
                self._comment_output_file,
                len(text.split("\n")),
            )


def main(args):
    logging.basicConfig(level=logging.DEBUG)
    data_builder = DataBuilder(args)

    data_builder.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="poeladder item info composer")
    parser.add_argument("-i", "--input", help="input directory containing YAML files", required=True)
    parser.add_argument("-is", "--item-schema", help="path to single item schema file", required=True)
    parser.add_argument("-o", "--output", help="output JSON file", required=True)
    parser.add_argument("-co", "--comment-output", help="output file for pull request comments", required=True)

    main(parser.parse_args())
