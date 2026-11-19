"""
models/equipment.py
스마트팜 장비 도메인 모델 (객체지향 상속 및 다형성 설계)
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Dict, Any


class Equipment(ABC):
    """스마트팜 제어 장비 추상 클래스"""

    def __init__(self, name: str, power_watt: float, equipment_type: str):
        self.name = name
        self.power_watt = power_watt  # 소비전력 (W)
        self.equipment_type = equipment_type

    def calculate_kwh(self, duration_hours: float) -> float:
        """가동 시간(시간 단위)에 따른 전력 소비량(kWh) 계산"""
        return (self.power_watt * duration_hours) / 1000.0

    @abstractmethod
    def simulate_effect(self, duration_minutes: float, current_temp: float, current_hum: float) -> tuple[float, float]:
        """
        장비 가동 후 예상 기온 및 습도 변화 시뮬레이션
        Returns: (predicted_temp, predicted_hum)
        """
        pass

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "power_watt": self.power_watt,
            "equipment_type": self.equipment_type,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Equipment":
        eq_type = data.get("equipment_type", "fan")
        if eq_type == "light":
            return GrowLight(name=data["name"], power_watt=data["power_watt"])
        elif eq_type == "heater":
            return Heater(name=data["name"], power_watt=data["power_watt"])
        else:
            return VentilationFan(name=data["name"], power_watt=data["power_watt"])


class VentilationFan(Equipment):
    """환기팬 장비: 고온/다습 완화"""

    def __init__(self, name: str = "환기팬", power_watt: float = 75.0):
        super().__init__(name=name, power_watt=power_watt, equipment_type="fan")

    def simulate_effect(self, duration_minutes: float, current_temp: float, current_hum: float) -> tuple[float, float]:
        # 10분 가동당 약 1.0℃ 냉각 효과, 습도 4% 감소 (실외 외기 평균 22℃/55% 수렴)
        factor = duration_minutes / 10.0
        predicted_temp = max(22.0, current_temp - (1.2 * factor)) if current_temp > 22.0 else current_temp
        predicted_hum = max(55.0, current_hum - (3.5 * factor)) if current_hum > 55.0 else current_hum
        return round(predicted_temp, 1), round(predicted_hum, 1)


class GrowLight(Equipment):
    """보광등(LED 식물 생장등) 장비: 조도 보강"""

    def __init__(self, name: str = "LED 보광등", power_watt: float = 120.0, illuminance_boost: float = 15000.0):
        super().__init__(name=name, power_watt=power_watt, equipment_type="light")
        self.illuminance_boost = illuminance_boost

    def simulate_effect(self, duration_minutes: float, current_temp: float, current_hum: float) -> tuple[float, float]:
        # LED 열에 의해 기온 소폭 상승 (+0.1℃ / 30분)
        temp_rise = (duration_minutes / 60.0) * 0.2
        return round(current_temp + temp_rise, 1), round(current_hum, 1)


class Heater(Equipment):
    """난방기 장비: 저온 환경 시 기온 상승"""

    def __init__(self, name: str = "온풍난방기", power_watt: float = 1500.0):
        super().__init__(name=name, power_watt=power_watt, equipment_type="heater")

    def simulate_effect(self, duration_minutes: float, current_temp: float, current_hum: float) -> tuple[float, float]:
        factor = duration_minutes / 10.0
        predicted_temp = current_temp + (2.0 * factor)
        predicted_hum = max(30.0, current_hum - (2.0 * factor))
        return round(predicted_temp, 1), round(predicted_hum, 1)
