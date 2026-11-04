# Stage 1 data coverage

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
| Average monthly cash assistance per recipient | Not reported in the federal source at person grain. The characteristics release reports per-family assistance. | Explicitly unavailable. The dashboard separately labels the supported FY2024 national value as $673 per family per month; it does not divide family benefits by recipients or substitute total program spending. |
| Average recipient age | Characteristics report has age bands, not exact individual ages or an exact mean. | Explicitly unavailable. No midpoint or other estimate is calculated. |
| Demographic filters in combination | Characteristics are published in separate aggregate tables, with differing populations and no joint person-level records. | Not implemented. No demographic intersections or cross-filtering. |

**Definitions and period labels:** FY means October 1 through September 30. The monthly figures are the reported caseload for each month, not a count of unique people over the year. Families are TANF assistance units reported in the family tables; adult and child recipients are people in the recipient tables. The dashboard uses TANF-only workbooks, not combined TANF and Separate State Program (SSP)-MOE totals. ACF’s [TANF data report instructions and definitions](https://acf.gov/sites/default/files/documents/ofa/acf-199209-TANFSSP-data-report-instructions-valid-thru-2028-12.pdf) contain field-level federal reporting definitions.

## Refresh and validation

1. Run `python scripts/download_data.py`. It fetches the four official `.xlsx` files from the URLs listed in the script and this document.
2. The script downloads to a `.part` file, checks that the response is an Excel/ZIP workbook, then atomically replaces the local file. Network, HTTP, and file-format errors stop the refresh explicitly.
3. Run `python -m pytest -q`; the loader checks sheet headers, fiscal-year month columns, state/month uniqueness, nonnegative integer values, recipient subtotal consistency, and 12 months per fiscal year.
4. Review the ACF release page for a new year or revised workbook before adding it. Update the manifest, tests, coverage table, and dashboard metric labels together. Do not mix SSP-MOE with TANF or assume revised definitions are comparable.

## Later-stage coverage plan

| Later topic | Federal availability and limitation | Official state-level sources to investigate |
|---|---|---|
| County detail | The ACF caseload and characteristics workbooks used here publish state, not county, estimates. Federal aggregates cannot be allocated to counties. | State TANF agency administrative reports and state open-data portals; request county caseload aggregates from the state agency where not published. Find the appropriate agency via ACF's [State TANF page](https://acf.gov/ofa/programs-services/TANF/state) and [USAGov's state social services directory](https://www.usa.gov/state-social-services). Record each state's source, definition, suppression rules, and release cadence before combining. |
| Reported sex/gender | FY2024 characteristics tables report adult and child counts in male/female categories separately; they do not supply joint cross-tabs for other characteristics. These categories are reported fields and should not be relabeled as gender identity. | State TANF agency aggregate administrative reports for more current or locally detailed published categories. |
| Age | Federal report supplies age groups separately for adult and child recipients, not exact ages or a validated exact mean. | State TANF agency aggregate tables; retain their age bands and population/period labels. |
| Family size | Federal tables report counts by assistance-unit size and number of recipients, at state and annual grain. They do not establish county-level detail. | State TANF agency caseload reports for county/locality breakouts. |
| Education | Federal characteristics tables include adult educational-attainment categories and separate child education reporting. It is annual and separately tabulated. | State TANF agency administrative reports where published; confirm denominator and collected/not-known categories. |
| Cumulative countable months | Federal reports include time-limit categories, but categories are not a complete person-level monthly history and federal/state rules may differ. | State agency time-limit policy/administrative reports and the agency's published state TANF plan; request only de-identified, aggregate duration distributions. |
| Time-limit status | The federal characteristics report includes federal time-limit-related categories and exemption status, but does not fully capture all state policies, exceptions, extensions, or case histories. | State TANF plan and official agency policy/manuals, extension/exemption reports, and state administrative reporting. Document state-specific clocks and exceptions before comparing. |

For official policy documents, use ACF's [State TANF page](https://acf.gov/ofa/programs-services/TANF/state) and [state TANF policy instructions](https://acf.gov/ofa/policy-guidance/policy-instructions/state-tanf-policy) alongside the corresponding state agency's own published materials. A later analysis of duration or time-limit status must account for exclusions, exemptions, extensions, and state rules. Reaching a time limit is not evidence of improper receipt; demographic characteristics must not be used to infer misuse.
