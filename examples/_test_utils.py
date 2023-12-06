import json
import sys
from pathlib import Path


def load_app_keystore(filename: str = "mixin-app-keystore.json"):
    keystore_file = Path(__file__).parent.parent.parent / filename
    if not keystore_file.exists():
        msg = f"✗ keystore file not found: {keystore_file}"
        msg += "\nYou can get mixin app keystore value from https://developers.mixin.one/dashboard"
        print(msg)
        sys.exit(0)
    try:
        with open(keystore_file, "rt") as f:
            keystore = json.loads(f.read())
    except Exception as e:
        print(f"✗ Load keystore file error: {e}")
        sys.exit(0)

    return keystore


def load_parameters(filename="test-parameters.json"):
    parameters_file = Path(__file__).parent.parent.parent / filename
    if not parameters_file.exists():
        msg = f"✗ Parameters file not found: {parameters_file}"
        print(msg)
        sys.exit(0)

    try:
        with open(parameters_file, "rt") as f:
            parameters = json.loads(f.read())
    except Exception as e:
        msg = "✗ Parameters file structure reference examples/_parameters-example.json"
        msg += f"\nload parameters file error: {e}"
        print(msg)
        sys.exit(0)

    return parameters
