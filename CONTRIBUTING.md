# How to contribute

We'd love to accept your patches and contributions to this project. There are just a few small guidelines you need to follow.

## Guidelines

> Install dependencies for development environment.
`pip install -r requirements-dev.txt`

1. Write your code

2. Test your code

    (If required) Add a test case for your code in `tests/` folder, and make sure it passes.

    Use `pytest tests` to run all tests automatically.

3. Formatting code `isort mixinsdk;black -l 88 -t py39 -t py310 mixinsdk`

4. Update CHANGELOG.md (If need be)

5. Bump the version number([semantic versioning](https://semver.org/)), and update the changelog.

    Use `bumpversion major|minor|patch`

6. Push your code to the repository.

    Use `git push origin main --tags` to push your code to the repository.
