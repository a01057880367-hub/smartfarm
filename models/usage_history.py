"""
models/usage_history.py
실제 사용량 및 운영 비용 실적 도메인 모델
"""
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional


@dataclass
class UsageHistory:
    """작업 후 실제 투입된 물·전기 사용량 및 실적 비용 모델"""
    history_id: str
    user_id: str
    zone_id: str
    zone_name: str
    crop_type: str
    date: str                           # 작업 일자 (YYYY-MM-DD)
    actual_water_liter: float           # 실제 급수량 (L)
    light_duration_hours: float         # 보광등 켠 시간 (h)
    fan_duration_minutes: float         # 환기팬 가동 시간 (분)
    heater_duration_minutes: float      # 난방기 가동 시간 (분)
    total_kwh: float                    # 소비 전력량 (kWh)
    is_estimated_kwh: bool              # 측정 전력량 여부 (True면 추정, False면 실측)
    water_cost: float                   # 실제 물 비용 (원)
    electricity_cost: float             # 실제 전기 비용 (원)
    total_cost: float                   # 실제 총 운영비 (원)
    plan_id: Optional[str] = None       # 연결된 사전 계획 ID
    recommended_water_liter: float = 0.0 # 계획 권장 급수량 (비교용)
    planned_total_cost: float = 0.0     # 계획 예상 총비용 (비교용)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "UsageHistory":
        return cls(**data)
