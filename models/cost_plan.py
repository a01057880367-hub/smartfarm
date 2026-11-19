"""
models/cost_plan.py
저비용 운영 계획 및 장비 가동 후보군 도메인 모델
"""
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any


@dataclass
class EquipmentOperation:
    """개별 장비 가동 계획 항목"""
    equipment_name: str
    equipment_type: str
    duration_minutes: float    # 가동 시간 (분)
    power_watt: float          # 소비전력 (W)
    kwh: float                 # 소비 전력량 (kWh)
    cost: float                # 전기 비용 (원)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "EquipmentOperation":
        return cls(**data)


@dataclass
class CostPlan:
    """구역별 저비용 운영 계획 도메인 모델"""
    plan_id: str
    zone_id: str
    zone_name: str
    crop_type: str
    created_at: str
    moisture_status: str              # '급수 필요' 또는 '급수 보류'
    last_watering_date: str           # 최근 급수일 (YYYY-MM-DD or '급수 기록 없음')
    recommended_water_liter: float    # 권장 급수량 (L)
    water_cost: float                 # 예상 물 비용 (원)
    predicted_temp: float             # 예상 기온 (℃)
    predicted_humidity: float         # 예상 습도 (%RH)
    additional_light_hours: float     # 추가 보광 시간 (h)
    operations: List[EquipmentOperation] = field(default_factory=list)
    total_kwh: float = 0.0            # 총 예상 전력량 (kWh)
    electricity_cost: float = 0.0     # 예상 전기 비용 (원)
    total_cost: float = 0.0           # 총 예상 운영비 (물 + 전기, 원)
    meets_criteria: bool = True       # 재배환경 기준 충족 여부
    unmet_issues: str = ""            # 미충족 시 사유 (예: '온도 상한 초과')
    action_sequence: str = ""         # 권장 작업 순서 (예: '환기 10분 → 기온 재확인 → 보광')
    candidate_name: str = ""          # 후보 계획명 (예: '후보 A: 환기 10분 + 보광')

    def to_dict(self) -> dict:
        data = asdict(self)
        data["operations"] = [op.to_dict() for op in self.operations]
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "CostPlan":
        ops = [EquipmentOperation.from_dict(op) for op in data.get("operations", [])]
        data_copy = dict(data)
        data_copy["operations"] = ops
        return cls(**data_copy)
