"""
services/zone_service.py
재배 구역(Zone) 도메인 로직 및 데이터 관리 서비스
"""
from typing import List, Optional, Tuple
import uuid
from models.zone import Zone
from services.storage_service import StorageService


class ZoneService:
    """사용자별 스마트팜 재배 구역을 관리하는 서비스"""

    def __init__(self, storage: StorageService):
        self.storage = storage

    def get_user_zones(self, user_id: str) -> List[Zone]:
        """특정 사용자가 등록한 구역 목록 반환"""
        all_zones = self.storage.get_zones()
        return [z for z in all_zones if z.user_id == user_id]

    def has_user_zones(self, user_id: str) -> bool:
        """등록된 재배 구역이 있는지 확인 (요구사항 7)"""
        return len(self.get_user_zones(user_id)) > 0

    def get_zone_by_id(self, zone_id: str) -> Optional[Zone]:
        """구역 ID로 특정 구역 조회"""
        all_zones = self.storage.get_zones()
        for z in all_zones:
            if z.zone_id == zone_id:
                return z
        return None

    def add_zone(
        self,
        user_id: str,
        name: str,
        crop_type: str,
        area: float,
        soil_type: str,
        last_watering_date: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Zone]]:
        """
        신규 재배 구역 등록
        - 구역 이름, 작물, 면적(0 초과), 토양 확인
        """
        name = name.strip()
        crop_type = crop_type.strip()
        soil_type = soil_type.strip()

        if not name:
            return False, "구역 이름을 입력해 주세요.", None
        if not crop_type:
            return False, "작물 종류를 선택하거나 입력해 주세요.", None
        if area <= 0:
            return False, "재배면적은 0보다 큰 숫자여야 합니다.", None
        if not soil_type:
            return False, "토양 종류를 입력해 주세요.", None

        zone_id = f"zone_{uuid.uuid4().hex[:6]}"
        new_zone = Zone(
            zone_id=zone_id,
            user_id=user_id,
            name=name,
            crop_type=crop_type,
            area=float(area),
            soil_type=soil_type,
            last_watering_date=last_watering_date
        )

        all_zones = self.storage.get_zones()
        all_zones.append(new_zone)
        self.storage.save_zones(all_zones)
        return True, f"'{name}' 구역이 성공적으로 등록되었습니다.", new_zone

    def update_zone(
        self,
        zone_id: str,
        name: str,
        crop_type: str,
        area: float,
        soil_type: str,
        last_watering_date: Optional[str] = None
    ) -> Tuple[bool, str]:
        """구역 정보 수정 (요구사항 36)"""
        all_zones = self.storage.get_zones()
        for z in all_zones:
            if z.zone_id == zone_id:
                if not name.strip() or not crop_type.strip() or area <= 0:
                    return False, "올바른 구역 정보를 입력해 주세요."
                z.name = name.strip()
                z.crop_type = crop_type.strip()
                z.area = float(area)
                z.soil_type = soil_type.strip()
                if last_watering_date is not None:
                    z.last_watering_date = last_watering_date
                self.storage.save_zones(all_zones)
                return True, "구역 정보가 수정되었습니다."
        return False, "해당 구역을 찾을 수 없습니다."

    def update_last_watering_date(self, zone_id: str, watering_date: str) -> bool:
        """실제 급수 시 해당 구역의 최근 급수일 자동 반영"""
        all_zones = self.storage.get_zones()
        for z in all_zones:
            if z.zone_id == zone_id:
                z.update_watering_date(watering_date)
                self.storage.save_zones(all_zones)
                return True
        return False

    def delete_zone(self, zone_id: str) -> bool:
        """구역 삭제"""
        all_zones = self.storage.get_zones()
        filtered = [z for z in all_zones if z.zone_id != zone_id]
        if len(filtered) != len(all_zones):
            self.storage.save_zones(filtered)
            return True
        return False
