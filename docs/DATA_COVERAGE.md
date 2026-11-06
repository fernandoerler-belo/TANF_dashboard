# Federal data coverage

Only federally published HHS/ACF data is used. State-level observations from federal workbooks remain in scope; state-published files, agency reports, and open-data sources are excluded. Unsupported measures remain unavailable.

## Federal sources used

| Dataset | Official source and workbook | Reporting period | Grain and published measures |
|---|---|---|---|
| TANF caseload | [FY2022](https://acf.gov/ofa/data/tanf-caseload-data-2022) · [workbook](https://acf.gov/sites/default/files/documents/ofa/fy2022_tanf_caseload.xlsx) | Monthly; FY2022 October 2021–September 2022 is used | State counts for families, total recipients, adult recipients, and child recipients. The workbook also contains later calendar-month columns; these are excluded from FY2022. |
| TANF caseload | [FY2023](https://acf.gov/ofa/data/tanf-caseload-data-2023) · [workbook](https://acf.gov/sites/default/files/documents/ofa/fy2023_tanf_caseload.xlsx) | Monthly; FY2023 October 2022–September 2023 | Same four state-level monthly measures. |
| TANF caseload | [FY2024](https://acf.gov/ofa/data/tanf-caseload-data-2024) · [workbook](https://acf.gov/sites/default/files/documents/ofa/fy2024-15months-tanf-caseload.xlsx) | Monthly; FY2024 October 2023–September 2024 is used | Same four state-level monthly measures. The workbook also contains October–December 2024; those months are outside FY2024. |
| Recipient characteristics and financial circumstances | [ACF FY2024 release](https://acf.gov/ofa/data/characteristics-and-financial-circumstances-tanf-recipients-fiscal-year-2024) · [Excel workbook](https://acf.gov/system/files/filefield_paths/fy2024-characteristics.xlsx) | FY2024 annual data; ACF says reports are based on data reported as of July 1, 2025 | Separate state-level annual tables for adult/child characteristics, age bands, family composition, financial circumstances, and federal time-limit categories. These are aggregate tables, not person-level records or monthly cross-tabs. |

ACF describes the characteristics release as covering demographic information for adults and children in active families and closed cases, plus financial circumstances of cash-assistance recipients. Its FY2024 release highlights an average monthly cash-assistance amount of **$673 per recipient family**. It is a family-level figure, not an individual recipient benefit.

## Measure audit and dashboard scope

| Requested measure | Federal source support | Stage 1 treatment |
|---|---|---|
| Monthly total recipients | Caseload workbook, monthly state counts | Chart and average; a recipient is an individual reported in a TANF assistance unit. |
| Monthly adults and children | Separate monthly counts in caseload workbook | Chart as distinct recipient subgroups. Total recipients are checked against adults plus children. |
| Monthly families | Separate monthly family caseload in workbook | Separate family chart and average; families are not presented as people. |
| Average child recipients per assistance family | Derived from the federal monthly child recipient and family caseload counts | Sum child recipient counts across the selected months and states, divided by the matching sum of family counts, using unrounded values. Includes assistance families with no adult recipient; it does not measure all household children. Unavailable if the family denominator is zero. |
| Average monthly cash assistance per recipient | Not reported in the federal source at person grain. The characteristics release reports per-family assistance. | Not displayed. The dashboard omits this measure; it does not divide family benefits by recipients or substitute total program spending. |
| Average recipient age | Characteristics report has age bands, not exact individual ages or an exact mean. | Not displayed. No midpoint or other estimate is calculated. |
| Demographic filters in combination | Characteristics are published in separate aggregate tables, with differing populations and no joint person-level records. | Not implemented. No demographic intersections or cross-filtering. |

**Definitions and period labels:** FY means October 1 through September 30. The monthly figures are the reported caseload for each month, not a count of unique people over the year. Families are TANF assistance units reported in the family tables; adult and child recipients are people in the recipient tables. The dashboard uses TANF-only workbooks, not combined TANF and Separate State Program (SSP)-MOE totals. ACF’s [TANF data report instructions and definitions](https://acf.gov/sites/default/files/documents/ofa/acf-199209-TANFSSP-data-report-instructions-valid-thru-2028-12.pdf) contain field-level federal reporting definitions.

## Refresh and validation

1. Run `python scripts/download_data.py`. It fetches the four official `.xlsx` files from the URLs listed in the script and this document.
2. The script downloads to a `.part` file, checks that the response is an Excel/ZIP workbook, then atomically replaces the local file. Network, HTTP, and file-format errors stop the refresh explicitly.
3. Run `python -m pytest -q`; the loader checks sheet headers, fiscal-year month columns, state/month uniqueness, nonnegative integer values, recipient subtotal consistency, and 12 months per fiscal year.
4. Review the ACF release page for a new year or revised workbook before adding it. Update the federal download catalog, loader, tests, coverage table, and dashboard metric labels together. Do not mix SSP-MOE with TANF or assume revised definitions are comparable.

## Future federal coverage

Future additions must use federal publications, retain the published population and period, and preserve the limits of aggregate tables.

| Topic | Federal availability and limitation |
|---|---|
| County detail | The bundled ACF workbooks publish state-level data. County detail remains unavailable. |
| Reported sex | FY2024 characteristics tables report male/female categories separately for adults and children; these fields are not gender identity or joint cross-tabs. |
| Age | Separate adult and child age bands are available; an exact average age is not supported. |
| Family size | Annual state-level assistance-unit size tables are available; these are separate from monthly caseloads. |
| Education | Annual adult attainment and child education tables have separate populations and denominators. |
| Countable months and time-limit status | Published federal categories do not provide individual histories or fully describe state-specific clocks, exemptions, and extensions. |

The characteristics workbook is preserved for future federal-table integration. The current dashboard displays monthly caseloads only. Separate demographic tables must not be combined into unsupported intersections. Reaching a time limit is not evidence of improper receipt; demographic characteristics must not be used to infer misuse.
