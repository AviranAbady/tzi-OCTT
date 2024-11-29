import json
import os
import jsonschema
import base64
from dataclasses import asdict
import humps
import logging

logging.basicConfig(level=logging.INFO)

def get_basic_auth_headers(username, password):
    auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_string}"
    }

    return headers


def validate_schema(data, schema_file_name):
    current_directory = os.getcwd()
    schema_file_name = os.path.join(current_directory, 'schema', schema_file_name)
    with open(schema_file_name) as schema_file:
        schema = json.load(schema_file)
        data = humps.camelize(asdict(data))
        data = _remove_nones(data)
        try:
            is_valid, errors = validate_json_draft06(instance=data, schema=schema)
            if not is_valid:
                logging.info(errors)

            return is_valid
        except jsonschema.exceptions.ValidationError as err:
            logging.info(err.message)
            return False


def validate_json_draft06(instance, schema):
    validator = jsonschema.Draft6Validator(schema)

    errors = []
    for error in sorted(validator.iter_errors(instance), key=str):
        # Format error message with path
        path = ' -> '.join(str(p) for p in error.path) if error.path else 'root'
        errors.append(f"{path}: {error.message}")

    return len(errors) == 0, errors


def _remove_nones(data, depth=0):
    if depth > 5:
        return data

    if isinstance(data, dict):
        return {
            k: _remove_nones(v, depth + 1)
            for k, v in data.items()
            if v is not None and _remove_nones(v, depth + 1) is not None
        }
    elif isinstance(data, (list, tuple)):
        cleaned = [_remove_nones(x, depth + 1) for x in data if x is not None]
        return type(data)(cleaned)

    return data

