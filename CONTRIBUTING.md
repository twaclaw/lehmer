# Thank you!

I am glad you are reading this!

We welcome suggestions, criticism, and, of course, code contributions!

If you find bugs or have ideas for improvements please consider filing a GitHub issue or creating a PR.

## Steps for creating a PR

- Fork [this repository](https://github.com/twaclaw/lehmer.git)
- Clone your fork
- Add [this repository](https://github.com/twaclaw/lehmer.git) as an upstream
- Create a local environment, for instance

```bash
uv venv --python=3.13
uv pip install -e ".[dev]"
```

- Create a branch and add your changes, possibly including additional tests
- Run the tests and validate:

```bash
hatch test --cover --all
pre-commit run hatch-fmt --verbose
```

- Commit your changes
- Create a PR
