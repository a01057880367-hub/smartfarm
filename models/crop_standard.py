"""
models/crop_standard.py
작물별 생육 환경 기준 모델
"""
from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class CropStandard:
    """작물별 생육 환경 관리 기준"""
    crop_name: str                      # 작물명 (예: 토마토, 상추 등)
    min_soil_moisture: float            # 급수 시작 기준 토양 수분 (%)
    irrigation_depth_mm: float          # 1회 관개요구량 (mm)
    temp_min: float                     # 적정 최저 기온 (℃)
    temp_max: float                     # 적정 최고 기온 (℃)
    humidity_min: float                 # 적정 최저 습도 (%RH)
    humidity_max: float                 # 적정 최고 습도 (%RH)
    target_illuminance: float           # 기준 조도 (lx)
    target_light_hours: float           # 1일 목표 보광/일조 시간 (hours)

    def evaluate_moisture(self, current_moisture: float) -> str:
        """토양 수분 판정 ('급수 필요' 또는 '급수 보류')"""
        if current_moisture < self.min_soil_moisture:
            return "급수 필요"
        return "급수 보류"

    def calculate_water_liters(self, area_m2: float, current_moisture: float) -> float:
        """
        권장 급수량(L) 계산:
        급수 필요 시: 관개요구량(mm) * 재배면적(m²) = L (1mm = 1L/m²)
        급수 보류 시: 0 L
        """
        if current_moisture >= self.min_soil_moisture:
            return 0.0
        return round(self.irrigation_depth_mm * area_m2, 1)

    def evaluate_temperature(self, temp: float) -> str:
        """기온 평가 ('낮음', '적정', '높음')"""
        if temp < self.temp_min:
            return "낮음"
        elif temp > self.temp_max:
            return "높음"
        return "적정"

    def evaluate_humidity(self, hum: float) -> str:
        """상대습도 평가 ('낮음', '적정', '높음')"""
        if hum < self.humidity_min:
            return "낮음"
        elif hum > self.humidity_max:
            return "높음"
        return "적정"

    def evaluate_illuminance(self, lux: float) -> str:
        """현재 조도 평가"""
        if lux < self.target_illuminance:
            return "부족"
        return "충족"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CropStandard":
        return cls(
            crop_name=data["crop_name"],
            min_soil_moisture=float(data["min_soil_moisture"]),
            irrigation_depth_mm=float(data["irrigation_depth_mm"]),
            temp_min=float(data["temp_min"]),
            temp_max=float(data["temp_max"]),
            humidity_min=float(data["humidity_min"]),
            humidity_max=float(data["humidity_max"]),
            target_illuminance=float(data["target_illuminance"]),
            target_light_hours=float(data["target_light_hours"]),
        )


# 기본 제공 작물 생육 표준 데이터
DEFAULT_CROP_STANDARDS: Dict[str, CropStandard] = {
    "토마토": CropStandard(
        crop_name="토마토",
        min_soil_moisture=25.0,
        irrigation_depth_mm=10.0,
        temp_min=18.0,
        temp_max=28.0,
        humidity_min=50.0,
        humidity_max=75.0,
        target_illuminance=30000.0,
        target_light_hours=8.0,
    ),
    "상추": CropStandard(
        crop_name="상추",
        min_soil_moisture=30.0,
        irrigation_depth_mm=8.0,
        temp_min=15.0,
        temp_max=22.0,
        humidity_min=60.0,
        humidity_max=80.0,
        target_illuminance=20000.0,
        target_light_hours=7.0,
    ),
    "딸기": CropStandard(
        crop_name="딸기",
        min_soil_moisture=28.0,
        irrigation_depth_mm=9.0,
        temp_min=16.0,
        temp_max=24.0,
        humidity_min=55.0,
        humidity_max=75.0,
        target_illuminance=25000.0,
        target_light_hours=8.0,
    ),
    "파프리카": CropStandard(
        crop_name="파프리카",
        min_soil_moisture=27.0,
        irrigation_depth_mm=10.0,
        temp_min=20.0,
        temp_max=27.0,
        humidity_min=55.0,
        humidity_max=75.0,
        target_illuminance=35000.0,
        target_light_hours=8.0,
    ),
}
