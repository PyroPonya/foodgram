# flake8: noqa
import json


def import_data_from_json(file_path, model):
    with open(file_path, encoding='utf-8') as f:
        model.objects.bulk_create(
            (model(**data) for data in json.load(f)),
            ignore_conflicts=True
        )
