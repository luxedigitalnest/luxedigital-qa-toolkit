# LuxeDigital QA Toolkit

Open-source quality assurance tools for Etsy and other digital-product sellers.

**LuxeDigital QA Toolkit** scans a digital delivery folder or ZIP before publication and flags common customer-experience problems: confusing filenames, missing files, oversized packages, weak image resolution, suspicious empty files, PDF problems, SVG scaling issues, and delivery-readiness risks.

The goal is simple: **catch preventable mistakes before the customer downloads them.**

## Why this exists

Digital sellers often assemble PNGs, PDFs, SVGs, ZIP archives, template instructions, and bonus files manually. A single broken export, encrypted PDF, missing SVG viewBox, low-resolution image, or poorly structured ZIP can create support messages, refunds, and bad reviews.

This project provides a transparent, local-first QA layer that anyone can use or improve.

## Features

- Scan a folder or ZIP file
- Inventory all delivery files
- Detect zero-byte and suspiciously tiny files
- Check filename quality and duplicate content
- Flag deeply nested folders
- Inspect PNG/JPG/WebP dimensions with Pillow
- Estimate raster print size at 300 DPI
- Validate PDFs, page counts, page dimensions, and encryption state
- Parse SVGs safely and validate viewBox values
- Warn when SVG files contain raster imagery
- Detect unusually large individual files and packages
- Generate Markdown and JSON QA reports
- Exit with a non-zero status when errors are found
- Runs locally; customer files are not uploaded anywhere

## Install

From source:

```bash
git clone https://github.com/luxedigitalnest/luxedigital-qa-toolkit.git
cd luxedigital-qa-toolkit
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e .
```

Once published to PyPI, installation will be:

```bash
pip install luxedigital-qa-toolkit
```

## Usage

```bash
ldqa scan ./your-product-folder
```

Or scan a ZIP and save reports:

```bash
ldqa scan ./delivery.zip --report qa-report.md --json-report qa-report.json
```

## What it checks

| Check | Purpose |
|---|---|
| Empty/tiny files | Catch failed exports |
| Filename quality | Reduce buyer confusion |
| Duplicate names/content | Prevent ambiguous or redundant files |
| Nested folders | Keep packages easy to navigate |
| Raster dimensions | Catch low-resolution exports |
| 300-DPI estimate | Show realistic print dimensions |
| PDF readability | Catch corrupt deliverables |
| PDF page metadata | Verify pages and dimensions |
| PDF encryption | Flag unexpected buyer access friction |
| SVG parsing | Catch malformed vector files |
| SVG viewBox | Improve predictable scaling |
| Embedded raster in SVG | Flag vectors that may lose sharpness |
| File/package size | Surface download friction |

## Development

```bash
pip install -e ".[dev]"
pytest
python -m build
```

GitHub Actions runs the test suite on supported Python versions for pushes and pull requests.

## Optional Browser Use integration

The isolated [Browser Use setup](docs/browser-use.md) adds an agentic browser option for the LDN Sales Channel OS workflow without changing this package or replacing deterministic Playwright automation. It includes a pinned Python 3.12/`uv` environment, Windows bootstrap and MCP launcher, secret-safe health check, and read-only public-page demo.

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). Issues that are small and clearly scoped are intentionally kept available for first-time contributors.

## Privacy

The CLI runs locally. It does not upload seller files, artwork, customer data, or reports.

## Disclaimer

This project is an independent open-source utility. It is not affiliated with or endorsed by Etsy, Canva, or any marketplace mentioned in examples or documentation. Marketplace rules can change; sellers remain responsible for reviewing current platform requirements.

## License

MIT — see [LICENSE](LICENSE).
