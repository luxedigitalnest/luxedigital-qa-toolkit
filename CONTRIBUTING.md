# Contributing

Thanks for helping improve LuxeDigital QA Toolkit.

## Development setup

```bash
git clone https://github.com/luxedigitalnest/luxedigital-qa-toolkit.git
cd luxedigital-qa-toolkit
python -m venv .venv
pip install -e ".[dev]"
pytest
```

## Contribution workflow

1. Open an issue for substantial changes.
2. Fork the repository.
3. Create a focused branch.
4. Add or update tests.
5. Run `pytest`.
6. Open a pull request explaining the user problem and proposed solution.

## Good first contributions

Documentation, tests, new QA rules, report improvements, PDF validation, SVG validation, and small delivery checks are ideal first contributions.

## Principles

- Keep seller files local by default.
- Prefer explainable checks over opaque scoring.
- Avoid marketplace claims that cannot be verified.
- Every warning should tell the user what to do next.
- Add tests for bug fixes and new rules.
