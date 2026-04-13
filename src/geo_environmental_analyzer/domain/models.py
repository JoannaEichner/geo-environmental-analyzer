from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class InputPoint:
    number: str
    name: str
    x_raw: float
    y_raw: float


@dataclass(slots=True)
class OrderedRoute:
    points: list[InputPoint] = field(default_factory=list)


@dataclass(slots=True)
class ParcelRecord:
    parcel_number: str
    cadastral_district_code: str
    cadastral_district_name: str = ""
    municipality_name: str = ""
    parcel_identifier: str = ""


@dataclass(slots=True)
class SurfaceWaterResult:
    code: str
    name: str
    status: str
    monitored: str
    overall_state: str
    risk_assessment: str
    ecological_potential_goal: str
    chemical_goal: str


@dataclass(slots=True)
class GroundWaterResult:
    code: str
    name: str
    monitored: str
    chemical_state: str
    quantitative_state: str
    overall_state: str
    risk_assessment: str
    quantitative_goal: str
    chemical_goal: str


@dataclass(slots=True)
class ProtectedAreaDistance:
    form_name: str
    distance_km: float


@dataclass(slots=True)
class AnalysisBundle:
    route: OrderedRoute
    parcels: list[ParcelRecord] = field(default_factory=list)
    surface_water: list[SurfaceWaterResult] = field(default_factory=list)
    groundwater: list[GroundWaterResult] = field(default_factory=list)
    protected_areas: list[ProtectedAreaDistance] = field(default_factory=list)
