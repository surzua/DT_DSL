"""Data Contract Schemas for Logistics and Demand Forecasting."""

from datetime import date
from typing import Literal, Set
from pydantic import BaseModel, Field, field_validator

EXPECTED_CENTROS: Set[str] = {
    "CD_NORTE",
    "CD_SUR",
    "CD_CENTRO",
    "CD_ESTE",
    "CD_OESTE",
    "CD_PACIFICO",
}

EXPECTED_CANALES: Set[str] = {
    "PORTAL_WEB",
    "AGENTE_COMERCIAL",
    "ATENCION_TELEFONICA",
}

EXPECTED_HORIZONTES: Set[str] = {
    "D+1",
    "D+2",
    "D+3",
    "D+4",
}


class PedidoHistoricoRecord(BaseModel):
    centro_distribucion: str
    fecha_despacho: date
    unidades_reales: float = Field(ge=0.0)
    canal_venta: str

    @field_validator("centro_distribucion")
    @classmethod
    def validate_centro(cls, v: str) -> str:
        if v not in EXPECTED_CENTROS:
            raise ValueError(f"Centro '{v}' no reconocido. Esperados: {EXPECTED_CENTROS}")
        return v

    @field_validator("canal_venta")
    @classmethod
    def validate_canal(cls, v: str) -> str:
        if v not in EXPECTED_CANALES:
            raise ValueError(f"Canal '{v}' no reconocido. Esperados: {EXPECTED_CANALES}")
        return v


class PronosticoDemandaRecord(BaseModel):
    centro_distribucion: str
    fecha_emision: date
    fecha_despacho: date
    horizonte: str
    unidades_pronosticadas: float = Field(ge=0.0)

    @field_validator("centro_distribucion")
    @classmethod
    def validate_centro(cls, v: str) -> str:
        if v not in EXPECTED_CENTROS:
            raise ValueError(f"Centro '{v}' no reconocido. Esperados: {EXPECTED_CENTROS}")
        return v

    @field_validator("horizonte")
    @classmethod
    def validate_horizonte(cls, v: str) -> str:
        if v not in EXPECTED_HORIZONTES:
            raise ValueError(f"Horizonte '{v}' no reconocido. Esperados: {EXPECTED_HORIZONTES}")
        return v


class CapacidadLogisticaRecord(BaseModel):
    centro_distribucion: str
    fecha: date
    capacidad_maxima_unidades: float = Field(gt=0.0)

    @field_validator("centro_distribucion")
    @classmethod
    def validate_centro(cls, v: str) -> str:
        if v not in EXPECTED_CENTROS:
            raise ValueError(f"Centro '{v}' no reconocido. Esperados: {EXPECTED_CENTROS}")
        return v


class PlanEntregaClienteRecord(BaseModel):
    cliente_id: str
    centro_distribucion: str
    canal_venta: str
    fecha_plan: date
    unidades_plan: float = Field(ge=0.0)
    fecha_compra_real: date
    unidades_reales: float = Field(ge=0.0)
    fuera_de_plan: int = Field(ge=0, le=1)

    @field_validator("centro_distribucion")
    @classmethod
    def validate_centro(cls, v: str) -> str:
        if v not in EXPECTED_CENTROS:
            raise ValueError(f"Centro '{v}' no reconocido. Esperados: {EXPECTED_CENTROS}")
        return v
