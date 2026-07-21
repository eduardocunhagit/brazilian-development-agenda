# Brazil's Economic Development Agenda

An open, 150-minute lecture on Brazil's economic development agenda, prepared for international students. The deck is written in English and built with LaTeX Beamer: a 60-slide core presentation plus a backup appendix with formulas, full tables, measurement details, and references.

[Download the current PDF](brazilian_development_agenda_beamer.pdf)

## Coverage

- Orientation for international students: income convergence, a regional map, a historical timeline, and a glossary
- Brazil's growth and productivity puzzle
- Inflation, fiscal policy, public debt, and monetary policy
- Exchange-rate regimes and Brazil's historical experience
- Education, infrastructure, credit, taxation, informality, and productivity
- Public security, organized crime, territorial control, and development
- Racial and territorial inequality, demography, and climate as cross-cutting constraints
- The political economy of reform and an integrated macro-micro agenda

## Repository contents

- `brazilian_development_agenda_beamer.tex`: Beamer source
- `brazilian_development_agenda_beamer.pdf`: compiled lecture
- `brazilian_development_agenda_assets/`: figures, parsed public data, and source manifest
- `scripts/build_lecture_figures.py`: script used to retrieve BCB series and rebuild the figures

## Compile the slides

A TeX distribution with Beamer is required. From the repository root, run:

```bash
pdflatex brazilian_development_agenda_beamer.tex
pdflatex brazilian_development_agenda_beamer.tex
```

## Rebuild the data figures

Install the Python dependencies and run:

```bash
python -m pip install -r requirements.txt
python scripts/build_lecture_figures.py
```

The script downloads public series from the Banco Central do Brasil's SGS API and GDP-per-capita series from the World Bank API. The committed CSV files are a reproducible snapshot retrieved on July 21, 2026. Other figures use the public sources listed in [`brazilian_development_agenda_assets/SOURCES.md`](brazilian_development_agenda_assets/SOURCES.md).

## Contributing

Corrections, updated data, new teaching examples, and improvements to the visual design are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## License

The lecture content and original figures are licensed under CC BY 4.0, and the code is licensed under the MIT License. Source data and third-party material remain subject to their original providers' terms. See [LICENSE.md](LICENSE.md).
