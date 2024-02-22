import os
import json
from pathlib import Path

from jsonschema import validate, Draft202012Validator
from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource


json_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.com/sales.schema.json",
    "title": "Sales",
    "description": "",
    "type" : "object",
    "allOf": [
        # version 2022-01-01 の場合
        {
            "if": {
                "properties": {
                    "version": { "const": "2022-01-01" }
                }
            },
            "then": {
                "properties" : {
                    "product": { "$ref": "product.schema.json"},
                    "customer_name" : {
                        "type" : "string",
                        "description": "名前",
                    },
                },
                "required": ["product", "customer_name"]
            },
        },
        # version 2024-01-01 の場合
        {
            "if": {
                "properties": {
                    "version": { "const": "2024-01-01" }
                }
            },
            "then": {
                "properties" : {
                    "product": { "$ref": "product.schema.json"},
                    "customer_name" : {
                        "type" : "string",
                        "description": "名前",
                    },
                    "customer_age" : {
                        "type" : "number",
                        "description": "年齢",
                    },
                },
                "required": ["product", "customer_name", "customer_age"]
            },
        }
    ]
}


def retrieve_schema_from_filesystem(uri: str) -> (None | Resource):
    """依存するスキーマを解決します

    Args:
        (str)uri: 解決したいスキーマのURI
    Returns:
        (None | Resource) スキーマ
    """
    self_location = 'https://example.com/'
    if uri.startswith(self_location):
        path = Path(os.getcwd()) / Path(uri.removeprefix(self_location))
        contents = json.loads(path.read_text())
        return Resource.from_contents(contents)
    return None

def build_validator():
    registry = Registry(retrieve=retrieve_schema_from_filesystem)
    return Draft202012Validator(
        json_schema,
        registry=registry
    )

def main():
    validator = build_validator()
    # Version 2022-01-01
    validator.validate(instance={
        "version": "2022-01-01",
        "customer_name" : "John",
        "product": {
            "name": "egg",
            "price": "10.11"
        }
    })
    # Version 2024-01-01
    validator.validate(instance={
        "version": "2024-01-01",
        "customer_name" : "John",
        "customer_age" : 21,
        "product": {
            "name": "egg",
            "price": "10.11"
        }
    })



if __name__ == "__main__":
    main()

