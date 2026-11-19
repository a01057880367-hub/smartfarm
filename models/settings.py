"""
models/settings.py
스마트팜 시스템 전역 설정 모델 (단가 및 장비 목록)
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any
from models.equipment import Equipment, VentilationFan, GrowLight, Heater


@dataclass
class SystemSettings:
    """물·전기 단가 및 등록 장비 관리 설정"""
    water_unit_price: float = 450.0        # 물 단가 (원 / m³)
    electricity_unit_price: float = 140.0  # 전기 단가 (원 / kWh)
    equipments: List[Equipment] = field(default_factory=lambda: [
        VentilationFan(name="환기팬 1호", power_watt=75.0),
        GrowLight(name="LED 보광등 A", power_watt=120.0),
        Heater(name="온풍난방기", power_watt=1500.0)
    ])

    def to_dict(self) -> dict:
        return {
            "water_unit_price": self.water_unit_price,
            "electricity_unit_price": self.electricity_unit_price,
            "equipments": [eq.to_dict() for eq in self.equipments],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SystemSettings":
        equipments = [
            Equipment.from_dict(eq_data) for eq_data in data.get("equipments", [])
        ]
        if not equipments:
            equipments = [
                VentilationFan(name="환기팬 1호", power_watt=75.0),
                GrowLight(name="LED 보광등 A", power_watt=120.0),
                Heater(name="온풍난방기", power_watt=1500.0)
            ]
        return cls(
            water_unit_price=float(data.get("water_unit_price", 450.0)),
            electricity_unit_price=float(data.get("electricity_unit_price", 140.0)),
            equipments=equipments,
        )
