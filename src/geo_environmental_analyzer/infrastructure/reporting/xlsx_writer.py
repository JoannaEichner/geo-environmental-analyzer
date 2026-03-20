from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet.worksheet import Worksheet

from geo_environmental_analyzer.domain.models import AnalysisBundle, ParcelRecord
from geo_environmental_analyzer.domain.protocols import ReportWriter


@dataclass(slots=True)
class ParcelSheetRow:
    parcel_number: str
    cadastral_district: str


def map_parcels_to_sheet_rows(parcels: list[ParcelRecord]) -> list[ParcelSheetRow]:
    rows: list[ParcelSheetRow] = []

    for parcel in parcels:
        district_parts = [
            part
            for part in [parcel.cadastral_district_code, parcel.cadastral_district_name]
            if part
        ]
        rows.append(
            ParcelSheetRow(
                parcel_number=parcel.parcel_number,
                cadastral_district=" ".join(district_parts),
            )
        )

    return rows


class XlsxReportWriter(ReportWriter):
    def write(self, bundle: AnalysisBundle, output_path: Path) -> None:
        workbook = Workbook()
        default_sheet = workbook.active
        workbook.remove(default_sheet)

        self._write_parcels_sheet(workbook, bundle)
        self._write_water_status_sheet(workbook, bundle)
        self._write_water_goals_sheet(workbook, bundle)
        self._write_protected_areas_sheet(workbook, bundle)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        workbook.save(output_path)

    def _write_parcels_sheet(self, workbook: Workbook, bundle: AnalysisBundle) -> None:
        sheet = workbook.create_sheet("01_Dzialki")
        sheet.append(["Numer działki", "Obręb"])

        for row in map_parcels_to_sheet_rows(bundle.parcels):
            sheet.append([row.parcel_number, row.cadastral_district])

        sheet.column_dimensions["A"].width = 18
        sheet.column_dimensions["B"].width = 35

    def _write_water_status_sheet(
        self, workbook: Workbook, bundle: AnalysisBundle
    ) -> None:
        sheet = workbook.create_sheet("02_Wody_Status")
        sheet.column_dimensions["A"].width = 32
        sheet.column_dimensions["B"].width = 70

        for item in bundle.surface_water:
            self._append_block(
                sheet,
                f'{item.code} „{item.name}”:',
                [
                    ("Status JCWP", item.status),
                    ("monitorowana", self._normalize_monitoring(item.monitored)),
                    ("stan (ogólny)", item.overall_state),
                    (
                        "ocena ryzyka nieosiągnięcia celów środowiskowych",
                        self._normalize_risk(item.risk_assessment),
                    ),
                ],
            )

        for item in bundle.groundwater:
            self._append_block(
                sheet,
                item.name,
                [
                    ("monitorowana", self._normalize_monitoring(item.monitored)),
                    ("stan chemiczny", item.chemical_state),
                    ("stan ilościowy", item.quantitative_state),
                    ("stan JCWPd", item.overall_state),
                    (
                        "ocena ryzyka nieosiągnięcia celów środowiskowych",
                        self._normalize_risk(item.risk_assessment),
                    ),
                ],
            )

    def _write_water_goals_sheet(self, workbook: Workbook, bundle: AnalysisBundle) -> None:
        sheet = workbook.create_sheet("03_Wody_Cele")
        sheet.column_dimensions["A"].width = 32
        sheet.column_dimensions["B"].width = 90

        for item in bundle.surface_water:
            self._append_block(
                sheet,
                f'{item.code} „{item.name}”:',
                [
                    ("stan/potencjał ekologiczny", item.ecological_potential_goal),
                    ("stan chemiczny", item.chemical_goal),
                ],
            )

        for item in bundle.groundwater:
            self._append_block(
                sheet,
                item.name,
                [
                    ("stan chemiczny", item.chemical_goal),
                    ("stan ilościowy", item.quantitative_goal),
                ],
            )

    def _write_protected_areas_sheet(
        self, workbook: Workbook, bundle: AnalysisBundle
    ) -> None:
        sheet = workbook.create_sheet("04_Ochrona")
        sheet.append(["Nazwa obiektu", "Odległość [km]"])

        for item in bundle.protected_areas:
            sheet.append([item.form_name, item.distance_km])

        sheet.column_dimensions["A"].width = 55
        sheet.column_dimensions["B"].width = 18

    def _append_block(
        self,
        sheet: Worksheet,
        title: str,
        rows: list[tuple[str, str]],
    ) -> None:
        is_empty_sheet = (
            sheet.max_row == 1
            and sheet["A1"].value is None
            and sheet["B1"].value is None
        )
        start_row = 1 if is_empty_sheet else sheet.max_row + 2
        sheet.merge_cells(
            start_row=start_row, start_column=1, end_row=start_row, end_column=2
        )

        title_cell = sheet.cell(row=start_row, column=1, value=title)
        title_cell.font = Font(bold=True)
        title_cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True,
        )

        current_row = start_row + 1
        for label, value in rows:
            sheet.cell(row=current_row, column=1, value=label)
            sheet.cell(row=current_row, column=2, value=value)
            sheet.cell(row=current_row, column=1).alignment = Alignment(
                wrap_text=True, vertical="top"
            )
            sheet.cell(row=current_row, column=2).alignment = Alignment(
                wrap_text=True, vertical="top"
            )
            current_row += 1

    def _normalize_monitoring(self, value: str) -> str:
        normalized = value.strip().lower()
        if normalized in {"tak", "nie"}:
            return normalized
        return value

    def _normalize_risk(self, value: str) -> str:
        normalized = value.strip().lower()
        if "niezagro" in normalized:
            return "niezagrożona"
        if "zagro" in normalized:
            return "zagrożona"
        return value
