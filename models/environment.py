"""
models/environment.py
환경 측정 기록 도메인 엔티티
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Tuple


@dataclass
class EnvironmentRecord:
    """구역별 온습도, 수분, 조도 측정 기록 모델"""
    record_id: str
    zone_id: str
    user_id: str
    recorded_at: str          # 측정 일시 (YYYY-MM-DD HH:MM)
    soil_moisture: float      # 토양 수분 (%)
    temperature: float        # 기온 (℃)
    humidity: float           # 상대 습도 (%RH)
    illuminance: float        # 조도 (lx)

    @staticmethod
    def validate_inputs(moisture: float, temp: float, hum: float, lux: float) -> Tuple[bool, str]:
        """
        환경 측정값 범위 유효성 검사
        - 토양 수분: 0 ~ 100%
        - 기온: -20 ~ 60℃
        - 공기 상대습도: 0 ~ 100%
        - 조도: 0 이상
        """
        if not (0.0 <= moisture <= 100.0):
            return False, "토양 수분은 0%에서 100% 사이여야 합니다."
        if not (-20.0 <= temp <= 60.0):
            return False, "기온은 -20℃에서 60℃ 사이여야 합니다."
        if not (0.0 <= hum <= 100.0):
            return False, "공기 상대습도는 0%에서 100% 사이여야 합니다."
        if lux < 0.0:
            return False, "조도는 0 lx 이상이어야 합니다."
        return True, ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "EnvironmentRecord":
        return cls(
            record_id=data["record_id"],
            zone_id=data["zone_id"],
            user_id=data["user_id"],
            recorded_at=data["recorded_at"],
            soil_moisture=float(data["soil_moisture"]),
            temperature=float(data["temperature"]),
            humidity=float(data["humidity"]),
            illuminance=float(data["illuminance"]),
        )
