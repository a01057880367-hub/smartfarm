"""
services/environment_service.py
구역별 환경 측정 데이터 기록, 유효성 검사, 변화량 분석 서비스
"""
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
import uuid
from models.environment import EnvironmentRecord
from services.storage_service import StorageService


class EnvironmentService:
    """구역별 온습도, 토양 수분, 조도 측정값 기록 및 분석 서비스"""

    def __init__(self, storage: StorageService):
        self.storage = storage

    def get_records_by_zone(self, zone_id: str) -> List[EnvironmentRecord]:
        """특정 구역의 모든 측정 기록을 시간 오름차순으로 반환"""
        all_records = self.storage.get_environments()
        zone_records = [r for r in all_records if r.zone_id == zone_id]
        return sorted(zone_records, key=lambda r: r.recorded_at)

    def get_latest_record(self, zone_id: str) -> Optional[EnvironmentRecord]:
        """특정 구역의 가장 최근 측정 기록 반환"""
        records = self.get_records_by_zone(zone_id)
        if records:
            return records[-1]
        return None

    def get_previous_record(self, zone_id: str) -> Optional[EnvironmentRecord]:
        """가장 최근 측정 기록의 바로 직전(이전) 기록 반환"""
        records = self.get_records_by_zone(zone_id)
        if len(records) >= 2:
            return records[-2]
        return None

    def record_environment(
        self,
        user_id: str,
        zone_id: str,
        recorded_at: str,
        moisture_str: str,
        temp_str: str,
        hum_str: str,
        lux_str: str,
        custom_watering_date: Optional[str] = None
    ) -> Tuple[bool, str, Optional[EnvironmentRecord], Optional[Dict[str, str]]]:
        """
        신규 환경 측정값 등록 및 유효성 검증 (요구사항 11, 12, 13)
        Returns: (success, message, record, change_summary_dict)
        """
        # 1. 숫자 형식 변환 검사
        try:
            moisture = float(moisture_str)
            temp = float(temp_str)
            hum = float(hum_str)
            lux = float(lux_str)
        except ValueError:
            return False, "측정값은 모두 유효한 숫자 형식이어야 합니다.", None, None

        # 2. 범위 유효성 검사
        valid, msg = EnvironmentRecord.validate_inputs(moisture, temp, hum, lux)
        if not valid:
            return False, msg, None, None

        # 3. 측정 시각 형식 검사
        try:
            rec_dt = datetime.strptime(recorded_at, "%Y-%m-%d %H:%M")
        except ValueError:
            try:
                rec_dt = datetime.strptime(recorded_at, "%Y-%m-%d")
            except ValueError:
                return False, "측정 일시는 'YYYY-MM-DD HH:MM' 형식이어야 합니다.", None, None

        # 4. 최근 급수일 날짜 유효성 검사 (측정 날짜보다 미래인지 확인)
        if custom_watering_date and custom_watering_date.strip():
            try:
                water_dt = datetime.strptime(custom_watering_date.strip(), "%Y-%m-%d")
                if water_dt.date() > rec_dt.date():
                    return False, f"최근 급수일({custom_watering_date})은 측정 일자({rec_dt.strftime('%Y-%m-%d')})보다 뒤(미래)일 수 없습니다.", None, None
            except ValueError:
                return False, "급수일자는 'YYYY-MM-DD' 형식이어야 합니다.", None, None

        # 이전 최근 기록 조회 (변화량 비교용)
        prev_record = self.get_latest_record(zone_id)

        # 5. 엔티티 생성 및 저장
        rec_id = f"env_{uuid.uuid4().hex[:8]}"
        new_record = EnvironmentRecord(
            record_id=rec_id,
            zone_id=zone_id,
            user_id=user_id,
            recorded_at=recorded_at,
            soil_moisture=round(moisture, 1),
            temperature=round(temp, 1),
            humidity=round(hum, 1),
            illuminance=round(lux, 0)
        )

        all_records = self.storage.get_environments()
        all_records.append(new_record)
        self.storage.save_environments(all_records)

        # 6. 이전 기록과의 변화량 계산 (요구사항 13)
        change_summary = {}
        if prev_record:
            m_diff = new_record.soil_moisture - prev_record.soil_moisture
            t_diff = new_record.temperature - prev_record.temperature
            h_diff = new_record.humidity - prev_record.humidity
            l_diff = new_record.illuminance - prev_record.illuminance

            change_summary = {
                "moisture": f"토양 수분: {prev_record.soil_moisture:.1f}% → {new_record.soil_moisture:.1f}% ({m_diff:+.1f}%p)",
                "temp": f"기온: {prev_record.temperature:.1f}℃ → {new_record.temperature:.1f}℃ ({t_diff:+.1f}℃)",
                "hum": f"상대습도: {prev_record.humidity:.1f}% → {new_record.humidity:.1f}% ({h_diff:+.1f}%p)",
                "lux": f"조도: {prev_record.illuminance:,.0f} lx → {new_record.illuminance:,.0f} lx ({l_diff:+,.0f} lx)",
                "prev_time": prev_record.recorded_at
            }

        return True, "환경 측정값이 성공적으로 저장되었습니다.", new_record, change_summary
