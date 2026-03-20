# AGENTS.md

## Project Context

Geo Environmental Analyzer is a new replacement for legacy environmental
processing scripts. The target system should read a single TXT file, perform
all required environmental analyses end-to-end, and produce a final XLSX
report that is useful in daily analytical work.

The project is being rebuilt with a strong focus on maintainability,
modularity, testability, and clear separation of responsibilities.

## Current MVP Scope

The current MVP includes:

1. Parcel analysis for a route built from input points.
2. Surface water analysis (JCWP).
3. Groundwater analysis (JCWPd).
4. Nature protection analysis with minimal distances.

## Input/Output Contract

### Input

- One simple TXT file.
- Canonical row format: `nr<TAB>nazwa<TAB>x<TAB>y`.
- Points are interpreted as one route in file order.

### Output

- One main XLSX report.
- Expected sheets:
  - `01_Dzialki`
  - `02_Wody_Status`
  - `03_Wody_Cele`
  - `04_Ochrona`
- Distances are reported in kilometers with precision to 2 decimal places.

## Engineering Rules

- Follow SOLID principles.
- Follow PEP 8.
- Keep CLI as a thin layer only.
- Keep configuration outside application logic.
- Keep domain logic testable in isolation.
- Do not hardcode `C:\...` paths in source code.
- Prefer clear boundaries between domain, application, analyses, and infrastructure.

## Working Agreement

- Implement the project task by task.
- Before each larger change, clarify the scope of that task.
- Do not add new application logic without explicit user approval.
- After each completed task, update this file if new important technical or domain knowledge appears.

## Decision Log

- Input is one simple TXT file.
- Input points form one route.
- The main report format is XLSX.
- Distances are reported in kilometers with precision to 2 decimal places.
- MVP includes four analyses: parcels, JCWP, JCWPd, and nature protection.
- ULDK `GetParcelById` returns parcel district name under `obreb`, not `obreb_ewidencyjny`.
- Parcel enrichment currently uses ULDK for municipality name and parcel district name.
- Parcel sheet in the XLSX report uses two columns only: parcel number and district (code + name).
- Water sheets in the XLSX report use a block layout with one title row per water body and label/value rows below.
- Surface water report codes are displayed with the `PLRW...` form.
- Groundwater report titles use spatial metadata `NR_JCWPD` and `KOD_UE`, for example `Jednolita czesc wod podziemnych nr 65 PLGW200065`.
- Nature protection report lists specific protected object names from RDOS `nazwa` fields, not only category names.
- Nature protection report labels are composed as form type plus object name, for example `Obszar chronionego krajobrazu ...`, `Natura 2000 Obszar specjalnej ochrony "..."`, `Rezerwat przyrody "..."`.
- CLI contract is `gea run --input <path> --output <path> --config <path>`.

## Update Policy

- Treat this file as a living project memory.
- Update it whenever we learn something important about:
  - data sources,
  - field mappings,
  - report layout,
  - architecture decisions,
  - workflow rules,
  - technical constraints,
  - accepted assumptions.
- Prefer adding short, high-signal facts instead of long narrative notes.
