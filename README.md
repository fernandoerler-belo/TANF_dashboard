# TANF Across America

Dashboard on TANF information in the US. A public-facing Streamlit dashboard for monthly TANF cash-assistance caseloads in the 50 states.

## Run locally

Python 3.10 or newer is recommended.

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

## Deploy to Streamlit Community Cloud

1. Push this project to a public GitHub repository.
2. In [Streamlit Community Cloud](https://share.streamlit.io/), create an app from the repository, select `app.py`, and deploy. Cloud installs the runtime packages from `requirements.txt`.
3. Keep the aggregate workbooks in `data/raw/` or run `python scripts/download_data.py` locally before committing refreshed official workbooks.

No secrets, credentials, or personal records are used. See [data coverage and definitions](docs/DATA_COVERAGE.md) before extending the measures.
