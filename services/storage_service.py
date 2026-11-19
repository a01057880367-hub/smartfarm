"""
services/storage_service.py
데이터 영속성 및 파일 저장소 관리 서비스 (JSON 기반)
"""
import json
import os
from typing import Dict, List, Any, Optional
from models.user import User
from models.zone import Zone
from models.environment import EnvironmentRecord
from models.crop_standard import CropStandard, DEFAULT_CROP_STANDARDS
from models.settings import SystemSettings
from models.cost_plan import CostPlan
from models.usage_history import UsageHistory


class StorageService:
    """JSON 파일 기반 로컬 데이터 저장소 매니저"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

        self.users_file = os.path.join(self.data_dir, "users.json")
        self.zones_file = os.path.join(self.data_dir, "zones.json")
        self.standards_file = os.path.join(self.data_dir, "standards.json")
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        self.environments_file = os.path.join(self.data_dir, "environments.json")
        self.plans_file = os.path.join(self.data_dir, "plans.json")
        self.histories_file = os.path.join(self.data_dir, "histories.json")

        self._initialize_defaults()

    def _read_json(self, filepath: str, default: Any) -> Any:
        if not os.path.exists(filepath):
            return default
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    def _write_json(self, filepath: str, data: Any) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _initialize_defaults(self) -> None:
        """기본 작물 기준, 단가 설정 및 테스트용 샘플 데이터 초기화"""
        # 1. 작물 기준
        if not os.path.exists(self.standards_file):
            standards_data = {name: std.to_dict() for name, std in DEFAULT_CROP_STANDARDS.items()}
            self._write_json(self.standards_file, standards_data)

        # 2. 시스템 기본 단가 및 장비 설정
        if not os.path.exists(self.settings_file):
            default_settings = SystemSettings()
            self._write_json(self.settings_file, default_settings.to_dict())

        # 3. 기본 테스트 유저 및 기본 구역 (체험용 demo 계정)
        if not os.path.exists(self.users_file):
            demo_user = User(user_id="farmer", password="123")
            self._write_json(self.users_file, [demo_user.to_dict()])

            demo_zones = [
                Zone(
                    zone_id="zone_01",
                    user_id="farmer",
                    name="A구역 (스마트 온실 1)",
                    crop_type="토마토",
                    area=100.0,
                    soil_type="사양토",
                    last_watering_date="2026-11-15"
                ),
                Zone(
                    zone_id="zone_02",
                    user_id="farmer",
                    name="B구역 (수직 농장 2)",
                    crop_type="상추",
                    area=60.0,
                    soil_type="양토",
                    last_watering_date="2026-11-17"
                ),
            ]
            self._write_json(self.zones_file, [z.to_dict() for z in demo_zones])

            # 환경 측정 샘플 데이터
            demo_env = [
                EnvironmentRecord(
                    record_id="env_01",
                    zone_id="zone_01",
                    user_id="farmer",
                    recorded_at="2026-11-18 09:00",
                    soil_moisture=26.0,
                    temperature=29.5,
                    humidity=82.0,
                    illuminance=18000.0
                ),
                EnvironmentRecord(
                    record_id="env_02",
                    zone_id="zone_01",
                    user_id="farmer",
                    recorded_at="2026-11-19 14:00",
                    soil_moisture=22.0,
                    temperature=28.8,
                    humidity=79.0,
                    illuminance=22000.0
                ),
                EnvironmentRecord(
                    record_id="env_03",
                    zone_id="zone_02",
                    user_id="farmer",
                    recorded_at="2026-11-19 14:00",
                    soil_moisture=34.0,
                    temperature=20.5,
                    humidity=68.0,
                    illuminance=21000.0
                )
            ]
            self._write_json(self.environments_file, [e.to_dict() for e in demo_env])

    # === Users ===
    def get_users(self) -> List[User]:
        data = self._read_json(self.users_file, [])
        return [User.from_dict(d) for d in data]

    def save_users(self, users: List[User]) -> None:
        self._write_json(self.users_file, [u.to_dict() for u in users])

    # === Zones ===
    def get_zones(self) -> List[Zone]:
        data = self._read_json(self.zones_file, [])
        return [Zone.from_dict(d) for d in data]

    def save_zones(self, zones: List[Zone]) -> None:
        self._write_json(self.zones_file, [z.to_dict() for z in zones])

    # === Crop Standards ===
    def get_standards(self) -> Dict[str, CropStandard]:
        data = self._read_json(self.standards_file, {})
        return {name: CropStandard.from_dict(std) for name, std in data.items()}

    def save_standards(self, standards: Dict[str, CropStandard]) -> None:
        self._write_json(self.standards_file, {k: v.to_dict() for k, v in standards.items()})

    # === Settings ===
    def get_settings(self) -> SystemSettings:
        data = self._read_json(self.settings_file, {})
        if not data:
            return SystemSettings()
        return SystemSettings.from_dict(data)

    def save_settings(self, settings: SystemSettings) -> None:
        self._write_json(self.settings_file, settings.to_dict())

    # === Environments ===
    def get_environments(self) -> List[EnvironmentRecord]:
        data = self._read_json(self.environments_file, [])
        return [EnvironmentRecord.from_dict(d) for d in data]

    def save_environments(self, records: List[EnvironmentRecord]) -> None:
        self._write_json(self.environments_file, [r.to_dict() for r in records])

    # === Plans ===
    def get_plans(self) -> List[CostPlan]:
        data = self._read_json(self.plans_file, [])
        return [CostPlan.from_dict(d) for d in data]

    def save_plans(self, plans: List[CostPlan]) -> None:
        self._write_json(self.plans_file, [p.to_dict() for p in plans])

    # === Usage Histories ===
    def get_histories(self) -> List[UsageHistory]:
        data = self._read_json(self.histories_file, [])
        return [UsageHistory.from_dict(d) for d in data]

    def save_histories(self, histories: List[UsageHistory]) -> None:
        self._write_json(self.histories_file, [h.to_dict() for h in histories])
