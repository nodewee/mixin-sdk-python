# How to contribute

We'd love to accept your patches and contributions to this project. There are just a few small guidelines you need to follow.

## Guidelines

1. Write your patch
2. (If requied) Add a test case to your patch in `examples/` folder, and run it.
3. Formatting code `isort .;black -l 88 -t py39 -t py310 .`
4. Bump the version number([semantic versioning](https://semver.org/)), and update the changelog.
    > Files involved: `mixinsdk/__init__.py`, `CHANGELOG.md`

5. Send your patch as a PR
