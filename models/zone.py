"""
models/zone.py
재배 구역 도메인 엔티티
"""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Zone:
    """스마트팜 재배 구역 정보 모델"""
    zone_id: str
    user_id: str
    name: str                   # 구역 이름 (예: A구역)
    crop_type: str              # 작물 종류 (예: 토마토, 상추, 딸기, 파프리카)
    area: float                 # 재배면적 (m²)
    soil_type: str              # 토양 종류 (예: 사양토, 양토, 점질토, 코코피트)
    last_watering_date: Optional[str] = None  # 가장 최근 실제 급수일 (YYYY-MM-DD)

    def update_watering_date(self, date_str: str) -> None:
        """최근 급수일 갱신"""
        self.last_watering_date = date_str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Zone":
        return cls(
            zone_id=data["zone_id"],
            user_id=data["user_id"],
            name=data["name"],
            crop_type=data["crop_type"],
            area=float(data["area"]),
            soil_type=data["soil_type"],
            last_watering_date=data.get("last_watering_date")
        )
