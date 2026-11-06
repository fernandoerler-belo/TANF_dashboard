# Publish TANF Across America

## Deployment settings

- Hosting: Streamlit Community Cloud (https://share.streamlit.io/).
- GitHub repository: `fernandoerler-belo/TANF_dashboard`.
- Deployment branch: `main`.
- Entrypoint: `app.py` in the repository root.
- Python: select `3.12` under Advanced settings.
- Dependencies: `requirements.txt` contains the tested runtime versions.
- Secrets: none required. Never commit `.streamlit/secrets.toml`.
- Data: the four official federal Excel workbooks are committed under `data/raw/`.

## Publish

1. Sign in to Streamlit Community Cloud with the GitHub account that owns the repository. Complete any account setup or GitHub authorization yourself, checking the permissions requested.
2. Choose **Create app**, then the option to deploy an existing GitHub app.
3. Enter the repository, branch, and entrypoint listed above. If the repository is not suggested, enter the values manually or paste `https://github.com/fernandoerler-belo/TANF_dashboard/blob/main/app.py` into the GitHub URL option.
4. Open **Advanced settings**, select Python `3.12`, leave Secrets empty, and save.
5. Choose an available app subdomain if desired, then deploy. Wait until the dashboard finishes loading.
6. Check app sharing settings and make the dashboard public so viewers do not need to be invited.
7. Copy the assigned `https://...streamlit.app/` URL. Test it in a private browser window, select a state and a region, and check the monthly chart and table.
8. Add the verified public URL near the top of `README.md` and to the repository's About/Website field.

## Updates

Push reviewed changes to `main`. Community Cloud detects updates to the deployment branch and rebuilds dependencies when required. Files on other branches do not update this deployment.

## Validation

Run `python -m pytest -q` before publishing changes. The existing tests cover all 50 states and three fiscal years, recipient totals, selection reset behavior, regional sums, and the child-recipient-per-family calculation.

The map uses publicly accessible Plotly browser resources. If those resources are unavailable to a visitor, the sidebar remains available for state selection. Dashboard data is loaded from the committed workbooks, using paths relative to the app files rather than Windows-specific paths.

## Troubleshooting

- Missing module: confirm `requirements.txt` is present on the deployment branch and inspect the app build logs.
- Missing data: confirm all files in `data/raw/` were pushed to the deployment branch.
- Old dashboard: confirm the deployed branch is `main` and compare its latest commit with the cloud logs.
- Public link requires invitation: review app sharing settings, then retest in a private window.
- Localhost link does not work on another computer: share the assigned Streamlit URL instead.

Official guide: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
