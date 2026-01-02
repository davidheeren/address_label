#!/usr/bin/env -S uv run --script

from argparse import Namespace
from main import get_args
from label_generator_app import LabelGeneratorApp
from pathlib import Path
import json
import platformdirs

CONFIG_PATH = platformdirs.user_data_path("address_label_generator", ensure_exists=True) / "config.json"


def args_or_default(args: Namespace) -> Namespace:
    default_args = get_args(True)
    if args is None:
        return default_args
    merged_vars = {**vars(default_args), **vars(args)}
    return Namespace(**merged_vars)


def load_args_from_config() -> Namespace:
    path = Path(CONFIG_PATH)
    args = None
    # if path.is_file():
    if path.is_file():
        with open(CONFIG_PATH, 'r') as f:
            try:
                data = json.load(f)
            except Exception:
                # not valid json
                data = {}
            args = Namespace(**data)
    return args_or_default(args)


def save_config(args: Namespace):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(vars(args), f, indent=4)


# TODO: refactor to not one giant function
#       have better names like run and state
# NOTE: this is my using this library or any python gui lol
# NAMING: args -> underlying data structure, config -> config file, options -> gui values

def main():
    args = load_args_from_config()
    app = LabelGeneratorApp(args, save_config)
    app.mainloop()


if __name__ == "__main__":
    main()
