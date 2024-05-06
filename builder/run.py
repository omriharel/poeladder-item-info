import argparse
import json
import logging
import os
import subprocess
from glob import iglob

import yaml


def load_yaml_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_output_json(item_data, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(item_data, f)

    logging.info("Written output to %s", output_file)


def iterate_yaml_files(base_dir):
    for filename in iglob(f"{base_dir}/**/*.yml", recursive=True):
        yield filename


def validate_item_files(input_dir, item_schema, error_output_file):
    validation_errors = []

    for filename in iterate_yaml_files(input_dir):
        logging.info("Running ajv for %s...", filename)
        ajv_command = ["ajv", "-s", item_schema, "-d", filename, "--spec=draft2020"]

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
        failing_filenames = ", ".join([error[0][len(input_dir) + 1 :] for error in validation_errors])
        print(f"The following file(s) failed to validate - please fix them to match the schema: {failing_filenames}")
        save_validation_errors(validation_errors, error_output_file)
        raise SystemExit(1)


def save_validation_errors(validation_errors, error_output_file):
    lines = [
        "Some file(s) changed/added in this PR don't adhere to the data schema. Please fix the errors detailed below for each file:",
        "",
    ]

    for filename, ajv_stderr in validation_errors:
        lines.extend([f"- `{filename}`:", "```", "\n".join(ajv_stderr.split("\n")[1:]), "```"])

    with open(error_output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        logging.info("Written error output to %s (%d lines)", error_output_file, len(lines))


def load_item_files(input_dir):
    item_data = {}
    filenames = list(iterate_yaml_files(input_dir))
    for filename in filenames:
        file_data = load_yaml_file(filename)
        raw_item_key = os.path.basename(filename)[:-4]

        if "variants" in file_data:
            for variant_name, variant_data in file_data["variants"].items():
                item_data[f"{raw_item_key} ({variant_name})"] = variant_data
        else:
            item_data[raw_item_key] = file_data

    logging.info(
        "Loaded item data for %s total entries (including variants) from %s files", len(item_data), len(filenames)
    )

    return item_data


def main(input_dir, item_schema, output_file, error_output_file):
    validate_item_files(input_dir, item_schema, error_output_file)
    item_data = load_item_files(input_dir)
    save_output_json(item_data, output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="poeladder item info composer")
    parser.add_argument("-i", "--input", help="input directory containing YAML files", required=True)
    parser.add_argument("-is", "--item-schema", help="path to single item schema file", required=True)
    parser.add_argument("-o", "--output", help="output JSON file", required=True)
    parser.add_argument("-eo", "--error-output", help="output file for errors", required=True)
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    main(args.input, args.item_schema, args.output, args.error_output)
