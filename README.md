# TANF Across America

**[Open the public dashboard](https://tanf-across-america.streamlit.app/)**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://tanf-across-america.streamlit.app/)

A public-facing Streamlit dashboard for monthly TANF cash-assistance caseloads in the 50 states, using only data published by the federal U.S. Department of Health and Human Services, Administration for Children and Families (HHS/ACF).

State filters select state-level observations in the federal workbooks. State-published datasets are outside the project scope. Additional measures must come from federal sources and remain unavailable when those sources do not support them.

## Explore the dashboard

The dashboard starts with no selection and zero metrics. Choose a Census region to view combined monthly counts and average monthly caseloads for its states, or choose an individual state. "All regions" combines all 50 states. Click any state on the map to view that state. "Clear state / reset" clears both selectors, resets metrics to zero, and empties the chart and monthly table. Clearing the state selector also resets the display.

The map loads Plotly and geographic boundaries in the browser; the sidebar remains available if those resources cannot load. Regional counts use only the 50 states in the federal workbooks (excluding D.C.).

## Run locally

Use Python 3.12 for Streamlit Community Cloud. The dashboard is also tested locally with Python 3.14. Runtime package versions are pinned in `requirements.txt`.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python scripts\download_data.py
python -m streamlit run app.py
```

The official, aggregate ACF Excel workbooks are included under `data/raw/`. Run the download script to refresh them. It downloads into temporary files, verifies each is a valid Excel workbook, and replaces the local copy only after validation.

## Validate

```powershell
python -m pytest -q
```

The dashboard checks required columns, duplicate observations, nonnegative integer counts, the identity `total recipients = adults + children`, and 12 reported months per fiscal year before rendering.

## GitHub and public hosting

Source repository: [fernandoerler-belo/TANF_dashboard](https://github.com/fernandoerler-belo/TANF_dashboard).

The repository includes the dashboard, clickable state map, federal data workbooks, tests, and Streamlit configuration. No API keys or secrets are required. Downloading the source code does not require access to the author's computer.

To publish the interactive dashboard, sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with the GitHub account that owns the repository and create an app with these settings:

| Setting | Value |
| --- | --- |
| Repository | `fernandoerler-belo/TANF_dashboard` |
| Branch | `main` |
| Main file path | `app.py` |
| Python version (Advanced settings) | `3.12` |
| Secrets | Leave empty |

See [the deployment guide](docs/DEPLOYMENT.md) for the publishing and public-sharing steps. The deployed dashboard is public at https://tanf-across-america.streamlit.app/. Viewers do not need access to the source repository or the author's computer. `http://localhost:8501/` is only for local use.

After deployment, pushes to `main` update the hosted app automatically. Keep the aggregate workbooks in `data/raw/`; refresh them locally with `python scripts/download_data.py`, validate them, and commit the refreshed files when needed.

No secrets, credentials, or personal records are used. See [data coverage and definitions](docs/DATA_COVERAGE.md) for the federal-only scope and supported measures.
