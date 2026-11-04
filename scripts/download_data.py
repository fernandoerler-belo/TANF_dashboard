from pathlib import Path
from urllib.request import Request, urlopen
import zipfile


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

FILES = {
    "fy2022_tanf_caseload.xlsx": (
        "https://acf.gov/sites/default/files/documents/ofa/fy2022_tanf_caseload.xlsx"
    ),
    "fy2023_tanf_caseload.xlsx": (
        "https://acf.gov/sites/default/files/documents/ofa/fy2023_tanf_caseload.xlsx"
    ),
    "fy2024-15months-tanf-caseload.xlsx": (
        "https://acf.gov/sites/default/files/documents/ofa/fy2024-15months-tanf-caseload.xlsx"
    ),
    "fy2024_characteristics.xlsx": (
        "https://acf.gov/system/files/filefield_paths/fy2024-characteristics.xlsx"
    ),
}


def download(filename: str, url: str) -> None:
    target = RAW / filename
    temporary = target.with_suffix(target.suffix + ".part")
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"
            )
        },
    )
    try:
        with urlopen(request, timeout=60) as response, temporary.open("wb") as output:
            if response.status != 200:
                raise RuntimeError(f"Download failed with HTTP {response.status}: {url}")
            output.write(response.read())
        if not zipfile.is_zipfile(temporary):
            raise ValueError(f"Downloaded file is not a valid Excel workbook: {url}")
        temporary.replace(target)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    print(f"Downloaded {filename}")


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for filename, url in FILES.items():
        download(filename, url)


if __name__ == "__main__":
    main()
