# How to contribute

We'd love to accept your patches and contributions to this project. There are just a few small guidelines.

## Guidelines

1. Clone this repository or download it.

2. Prepare your environment

    > Runtime support: Python 3.9+

    Set up and activate virtual environment, like this:

    ```bash
    cd mixin-sdk-python-main
    python3 -m venv .env

    # for linux or mac
    . .env/bin/activate

    # for windows
    # .\.env\Scripts\activate
    ```

3. Install dependencies:

    `pip install -r requirements.txt`

    Install dependencies for development.

    `pip install -r requirements-dev.txt`

4. Than see "examples" folder, and run to test.

5. Write your code


7. Formatting code `isort . && black .`

    Rules are defined in `pyproject.toml`

1. Update CHANGELOG.md (If need be)

2. Bump the version number([semantic versioning](https://semver.org/)), and update the changelog.

    Use `bumpversion major|minor|patch`

3. Push your code to the repository.

    Use `git push origin main --tags` to push your code to the repository.
