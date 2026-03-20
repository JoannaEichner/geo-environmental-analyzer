# Geo Environmental Analyzer

## Project Goal

Geo Environmental Analyzer is an end-to-end environmental analysis tool.
It reads one TXT file with points, interprets those points as a single route,
and generates a structured XLSX report.

The project is intended to replace legacy one-off scripts with a cleaner,
modular, testable, and professional architecture.

## MVP Scope

The MVP includes four analysis areas:

1. Parcels intersected by the route.
2. Surface water bodies (JCWP).
3. Groundwater bodies (JCWPd).
4. Nature protection forms and their minimal distances.

## Input And Output Contract

### Input

- One TXT file is the canonical input.
- Canonical row format: `nr<TAB>nazwa<TAB>x<TAB>y`.
- Points are interpreted as one ordered route.

### Output

- One XLSX report is the canonical output.
- The report contains the following sheets:
  - `01_Dzialki`
  - `02_Wody_Status`
  - `03_Wody_Cele`
  - `04_Ochrona`
- Distances are reported in kilometers with precision to 2 decimal places.

## Working Rules

- We work in a modular way.
- We implement one task at a time.
- We do not add logic beyond the agreed scope.
- Documentation and project decisions must be updated as the project evolves.
- The reference plan lives in [plan.md](/c:/Users/jboro/Desktop/Nauka/geo-environmental-analyzer/plan.md).
- The task breakdown lives in [implementation_tasks.md](/c:/Users/jboro/Desktop/Nauka/geo-environmental-analyzer/implementation_tasks.md).
