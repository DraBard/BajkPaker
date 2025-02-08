import os
import yaml
from pathlib import Path


def load_config():
    config_path = Path(__file__).resolve().parent / "config.yaml"
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    for env in ["local", "deployment"]:
        for db in ["database_dev", "database_prod"]:
            config[env][db]["url"] = config[env][db]["url"].replace(
                "${DB_PASSWORD}", os.getenv("DB_PASSWORD")
            )

    return config


config = load_config()
