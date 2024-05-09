import json
import logging
import os
import urllib
from glob import iglob
import urllib.parse

import yaml

from constants import Constants


def load_yaml_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_raw_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def save_output_json(item_data, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(item_data, f)

    logging.info("Written output to %s", output_file)


def iterate_yaml_files(base_dir):
    for filename in iglob(f"{base_dir}/**/*.yml", recursive=True):
        yield filename


def trim_basedir(filename, input_dir):
    return filename[len(input_dir) + 1 :]


def build_edit_link(filename):
    # e.g. https://github.com/omriharel/poeladder-item-info/edit/master/items/belts/Mageblood.yml
    return f"{Constants.base_repo_url}/edit/{Constants.base_branch}/{urllib.parse.quote(filename)}"


def build_item_schema_link(item_schema):
    # e.g. https://github.com/omriharel/poeladder-item-info/blob/master/schemas/single-item.schema.json
    return f"{Constants.base_repo_url}/blob/{Constants.base_branch}/{urllib.parse.quote(item_schema)}"
