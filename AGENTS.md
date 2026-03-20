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
