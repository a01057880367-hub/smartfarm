"""
services/history_service.py
사용량과 비용 이력 저장, 통계 집계 및 계획 vs 실적 비교 서비스
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import uuid

from models.usage_history import UsageHistory
from models.cost_plan import CostPlan
from models.settings import SystemSettings
from services.storage_service import StorageService
from services.zone_service import ZoneService


class HistoryService:
    """실제 투입 자원 이력 기록, 통계 산출 및 계획 대비 실적 분석 서비스"""

    def __init__(self, storage: StorageService, zone_service: ZoneService):
        self.storage = storage
        self.zone_service = zone_service

    def save_actual_record(
        self,
        user_id: str,
        zone_id: str,
        zone_name: str,
        crop_type: str,
        date_str: str,
        actual_water_liter: float,
        light_hours: float,
        fan_minutes: float,
        heater_minutes: float,
        measured_kwh_input: Optional[str],
        settings: SystemSettings,
        associated_plan: Optional[CostPlan] = None
    ) -> Tuple[bool, str, Optional[UsageHistory]]:
        """
        실적 기록 저장 (요구사항 30, 31, 32)
        - 측정 전력량이 있으면 실측치 사용, 없으면 장비 소비전력으로 추정 ('(추정)' 플래그)
        - 실제 급수량 > 0 인 경우 해당 구역의 최근 급수일 자동 갱신
        """
        if actual_water_liter < 0 or light_hours < 0 or fan_minutes < 0 or heater_minutes < 0:
            return False, "사용량 및 가동 시간은 0 이상이어야 합니다.", None

        # 전력량 결정: 직접 측정 vs 소비전력 추정
        is_estimated = True
        total_kwh = 0.0

        if measured_kwh_input and measured_kwh_input.strip():
            try:
                val = float(measured_kwh_input.strip())
                if val >= 0:
                    total_kwh = round(val, 3)
                    is_estimated = False
            except ValueError:
                pass

        if is_estimated:
            # 기본 소비전력 기준으로 추정 (환기팬 75W, 보광등 120W, 난방기 1500W)
            fan_power = next((eq.power_watt for eq in settings.equipments if eq.equipment_type == "fan"), 75.0)
            light_power = next((eq.power_watt for eq in settings.equipments if eq.equipment_type == "light"), 120.0)
            heater_power = next((eq.power_watt for eq in settings.equipments if eq.equipment_type == "heater"), 1500.0)

            est_fan_kwh = (fan_power * (fan_minutes / 60.0)) / 1000.0
            est_light_kwh = (light_power * light_hours) / 1000.0
            est_heater_kwh = (heater_power * (heater_minutes / 60.0)) / 1000.0

            total_kwh = round(est_fan_kwh + est_light_kwh + est_heater_kwh, 3)

        # 비용 계산
        water_m3 = actual_water_liter / 1000.0
        water_cost = round(water_m3 * settings.water_unit_price, 0)
        electricity_cost = round(total_kwh * settings.electricity_unit_price, 0)
        total_cost = water_cost + electricity_cost

        # 계획 비교 데이터
        plan_id = associated_plan.plan_id if associated_plan else None
        rec_water = associated_plan.recommended_water_liter if associated_plan else 0.0
        plan_cost = associated_plan.total_cost if associated_plan else 0.0

        history = UsageHistory(
            history_id=f"hist_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            zone_id=zone_id,
            zone_name=zone_name,
            crop_type=crop_type,
            date=date_str,
            actual_water_liter=round(actual_water_liter, 1),
            light_duration_hours=round(light_hours, 1),
            fan_duration_minutes=round(fan_minutes, 1),
            heater_duration_minutes=round(heater_minutes, 1),
            total_kwh=total_kwh,
            is_estimated_kwh=is_estimated,
            water_cost=water_cost,
            electricity_cost=electricity_cost,
            total_cost=total_cost,
            plan_id=plan_id,
            recommended_water_liter=rec_water,
            planned_total_cost=plan_cost
        )

        all_hist = self.storage.get_histories()
        all_hist.append(history)
        self.storage.save_histories(all_hist)

        # 요구사항 32: 실제 급수량이 0 L보다 큰 기록은 해당 구역의 최근 급수일에 반영
        if actual_water_liter > 0:
            self.zone_service.update_last_watering_date(zone_id, date_str)

        return True, "실적 데이터가 성공적으로 저장되었습니다.", history

    def filter_histories(
        self,
        user_id: str,
        period_type: str = "all",  # 'today', 'week', 'month', 'custom', 'all'
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        zone_id: Optional[str] = None,
        crop_type: Optional[str] = None
    ) -> List[UsageHistory]:
        """조회 기간 및 구역/작물 필터링 (요구사항 33)"""
        all_hist = [h for h in self.storage.get_histories() if h.user_id == user_id]

        today = datetime.now().date()

        filtered = []
        for h in all_hist:
            try:
                h_date = datetime.strptime(h.date, "%Y-%m-%d").date()
            except ValueError:
                continue

            # 기간 필터
            if period_type == "today":
                if h_date != today:
                    continue
            elif period_type == "week":
                if h_date < today - timedelta(days=7):
                    continue
            elif period_type == "month":
                if h_date < today - timedelta(days=30):
                    continue
            elif period_type == "custom":
                if start_date:
                    s_d = datetime.strptime(start_date, "%Y-%m-%d").date()
                    if h_date < s_d:
                        continue
                if end_date:
                    e_d = datetime.strptime(end_date, "%Y-%m-%d").date()
                    if h_date > e_d:
                        continue

            # 구역 필터
            if zone_id and zone_id != "all" and h.zone_id != zone_id:
                continue

            # 작물 필터
            if crop_type and crop_type != "all" and h.crop_type != crop_type:
                continue

            filtered.append(h)

        return sorted(filtered, key=lambda x: x.date, reverse=True)

    def calculate_statistics(self, histories: List[UsageHistory]) -> Dict[str, Any]:
        """선택 기간 집계 및 통계 산출 (요구사항 34)"""
        total_water = sum(h.actual_water_liter for h in histories)
        total_light_h = sum(h.light_duration_hours for h in histories)
        total_kwh = sum(h.total_kwh for h in histories)
        total_water_cost = sum(h.water_cost for h in histories)
        total_elec_cost = sum(h.electricity_cost for h in histories)
        total_cost = sum(h.total_cost for h in histories)

        # 계획 대비 절감/차이 집계
        total_planned_cost = sum(h.planned_total_cost for h in histories if h.planned_total_cost > 0)
        cost_diff = total_cost - total_planned_cost

        return {
            "count": len(histories),
            "total_water_liter": round(total_water, 1),
            "total_light_hours": round(total_light_h, 1),
            "total_kwh": round(total_kwh, 2),
            "total_water_cost": round(total_water_cost, 0),
            "total_electricity_cost": round(total_elec_cost, 0),
            "total_cost": round(total_cost, 0),
            "total_planned_cost": round(total_planned_cost, 0),
            "cost_diff": round(cost_diff, 0),
        }
