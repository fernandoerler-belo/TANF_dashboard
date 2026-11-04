from datetime import datetime
from pathlib import Path
from typing import Final

import pandas as pd


DATA_DIR: Final = Path(__file__).parent / "data" / "raw"

STATE_NAMES: Final = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming",
]

STATE_ABBREVIATIONS: Final = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY",
}

REGIONS: Final = {
    "Northeast": [
        "Connecticut", "Maine", "Massachusetts", "New Hampshire", "Rhode Island",
        "Vermont", "New Jersey", "New York", "Pennsylvania",
    ],
    "Midwest": [
        "Illinois", "Indiana", "Michigan", "Ohio", "Wisconsin", "Iowa", "Kansas",
        "Minnesota", "Missouri", "Nebraska", "North Dakota", "South Dakota",
    ],
    "South": [
        "Delaware", "District of Columbia", "Florida", "Georgia", "Maryland",
        "North Carolina", "South Carolina", "Virginia", "West Virginia", "Alabama",
        "Kentucky", "Mississippi", "Tennessee", "Arkansas", "Louisiana", "Oklahoma",
        "Texas",
    ],
    "West": [
        "Arizona", "Colorado", "Idaho", "Montana", "Nevada", "New Mexico", "Utah",
        "Wyoming", "Alaska", "California", "Hawaii", "Oregon", "Washington",
    ],
}

METRIC_LABELS: Final = {
    "total_recipients": "Total recipients",
    "adults": "Adult recipients",
    "children": "Child recipients",
    "families": "Families",
}

WORKBOOKS: Final = {
    2022: ("fy2022_tanf_caseload.xlsx", {
        "total_recipients": "TRec", "adults": "Adults", "children": "Children",
        "families": "TFam",
    }),
    2023: ("fy2023_tanf_caseload.xlsx", {
        "total_recipients": "TRec", "adults": "Adults", "children": "Children",
        "families": "TFam",
    }),
    2024: ("fy2024-15months-tanf-caseload.xlsx", {
        "total_recipients": "TotalRecipent", "adults": "Adults", "children": "Children",
        "families": "TotalFam",
    }),
}


def _month_from_header(value: object) -> pd.Timestamp | None:
    if isinstance(value, (datetime, pd.Timestamp)):
        return pd.Timestamp(value).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if isinstance(value, str):
        for date_format in ("%b-%y", "%B %Y", "%b %Y", "%b-%Y"):
            try:
                return pd.Timestamp(datetime.strptime(value.strip(), date_format)).replace(day=1)
            except ValueError:
                continue
    return None


def _read_metric(path: Path, sheet_name: str, metric: str, fiscal_year: int) -> pd.DataFrame:
    table = pd.read_excel(path, sheet_name=sheet_name, header=3, engine="openpyxl")
    if table.empty or table.columns[0] != "State":
        raise ValueError(f"{path.name}:{sheet_name} does not have the expected State header.")

    month_columns = {
        column: _month_from_header(column)
        for column in table.columns[1:]
    }
    month_columns = {
        column: month
        for column, month in month_columns.items()
        if month is not None
        and month.year in (fiscal_year - 1, fiscal_year)
        and (month.year, month.month) >= (fiscal_year - 1, 10)
        and (month.year, month.month) <= (fiscal_year, 9)
    }
    if not month_columns:
        raise ValueError(f"No FY{fiscal_year} month columns found in {path.name}:{sheet_name}.")

    table = table.loc[table["State"].isin(STATE_NAMES), ["State", *month_columns]]
    long = table.melt(
        id_vars="State",
        value_vars=list(month_columns),
        var_name="month_header",
        value_name=metric,
    )
    long["month"] = long["month_header"].map(month_columns)
    long[metric] = pd.to_numeric(long[metric], errors="coerce")
    return long.drop(columns="month_header").rename(columns={"State": "state"})


def load_caseload_data(data_dir: Path = DATA_DIR) -> pd.DataFrame:
    """Load FY2022–FY2024 state monthly TANF counts from official ACF workbooks."""
    yearly_data: list[pd.DataFrame] = []
    for fiscal_year, (filename, sheets) in WORKBOOKS.items():
        path = data_dir / filename
        if not path.is_file():
            raise FileNotFoundError(
                f"Missing {path}. Run `python scripts/download_data.py` to download official ACF files."
            )

        metric_frames = [
            _read_metric(path, sheet, metric, fiscal_year)
            for metric, sheet in sheets.items()
        ]
        merged = metric_frames[0]
        for frame in metric_frames[1:]:
            merged = merged.merge(frame, on=["state", "month"], how="outer", validate="one_to_one")
        merged["fiscal_year"] = fiscal_year
        yearly_data.append(merged)

    return (
        pd.concat(yearly_data, ignore_index=True)
        .sort_values(["fiscal_year", "state", "month"])
        .reset_index(drop=True)
    )


def validate_caseload_data(data: pd.DataFrame) -> None:
    required = {"state", "fiscal_year", "month", *METRIC_LABELS}
    missing_columns = required - set(data.columns)
    if missing_columns:
        raise ValueError(f"Caseload data is missing columns: {sorted(missing_columns)}")
    if data.empty:
        raise ValueError("No caseload rows were loaded.")
    if data.duplicated(["fiscal_year", "state", "month"]).any():
        raise ValueError("Duplicate state/month observations were found.")
    if not data["state"].isin(STATE_NAMES).all():
        raise ValueError("Unexpected geography found; expected the 50 states only.")

    counts = data[list(METRIC_LABELS)].stack().dropna()
    if counts.lt(0).any():
        raise ValueError("Negative caseload count found.")
    if not counts.map(lambda value: float(value).is_integer()).all():
        raise ValueError("Caseload counts must be whole numbers.")

    complete_recipients = data.dropna(subset=["total_recipients", "adults", "children"])
    if not (complete_recipients["total_recipients"] ==
            complete_recipients["adults"] + complete_recipients["children"]).all():
        raise ValueError("Total recipients do not equal adults plus children.")

    month_counts = data.groupby("fiscal_year")["month"].nunique()
    if not month_counts.eq(12).all():
        raise ValueError(f"Expected 12 fiscal-year months per year, found {month_counts.to_dict()}.")
