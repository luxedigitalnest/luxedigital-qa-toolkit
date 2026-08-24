# LuxeDigital QA Toolkit

Open-source quality assurance tools for Etsy and other digital-product sellers.

**LuxeDigital QA Toolkit** scans a digital delivery folder or ZIP before publication and flags common customer-experience problems: confusing filenames, missing files, oversized packages, weak image resolution, suspicious empty files, and delivery-readiness issues.

The goal is simple: **catch preventable mistakes before the customer downloads them.**

## Why this exists

Digital sellers often assemble PNGs, PDFs, SVGs, ZIP archives, Canva access instructions, and bonus files manually. A single bad filename, empty export, low-resolution image, or poorly structured ZIP can create support messages, refunds, and bad reviews.

This project provides a transparent, local-first QA layer that anyone can use or improve.

## Features

- Scan a folder or ZIP file
- Inventory all delivery files
- Detect zero-byte and suspiciously tiny files
- Check filename quality
- Flag deeply nested folders
- Inspect PNG/JPG/WebP dimensions with Pillow
- Estimate print size at 300 DPI
- Detect unusually large individual files and packages
- Generate Markdown and JSON QA reports
- Exit with a non-zero status when errors are found
- Works locally; customer files are not uploaded anywhere

## Quick start

```bash
git clone https://github.com/luxedigitalnest/luxedigital-qa-toolkit.git
cd luxedigital-qa-toolkit
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e .
ldqa scan ./your-product-folder
```

Or scan a ZIP:

```bash
ldqa scan ./delivery.zip --report qa-report.md --json-report qa-report.json
```

## What it checks

| Check | Purpose |
|---|---|
| Empty files | Prevent broken downloads |
| Tiny files | Catch failed or incomplete exports |
| Filename quality | Reduce buyer confusion |
| Nested folders | Keep delivery packages easy to navigate |
| Image dimensions | Catch low-resolution exports |
| 300-DPI print estimate | Show realistic print dimensions |
| Large files | Surface download friction |
| Package size | Flag unwieldy deliveries |
| Duplicate names/content | Prevent ambiguous or redundant files |

## Roadmap

See [ROADMAP.md](ROADMAP.md).

Planned areas include SVG validation, PDF page/dimension checks, Canva-delivery checks, configurable marketplace packaging profiles, accessibility guidance, and a browser-based report viewer.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Privacy

The CLI runs locally. It does not upload seller files, artwork, customer data, or reports.

## Disclaimer

This project is an independent open-source utility. It is not affiliated with or endorsed by Etsy, Canva, or any marketplace mentioned in examples or documentation. Marketplace rules can change; sellers remain responsible for reviewing current platform requirements.

## License

MIT — see [LICENSE](LICENSE).
