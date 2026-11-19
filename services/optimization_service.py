"""
services/optimization_service.py
저비용 운영 계획 계산 및 장비 가동 최적화 알고리즘 서비스
"""
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import uuid

from models.zone import Zone
from models.crop_standard import CropStandard, DEFAULT_CROP_STANDARDS
from models.settings import SystemSettings
from models.environment import EnvironmentRecord
from models.cost_plan import CostPlan, EquipmentOperation
from models.equipment import VentilationFan, GrowLight, Heater
from services.storage_service import StorageService


class OptimizationService:
    """스마트팜 환경 제어 및 관개 저비용 최적화 계산 엔진"""

    def __init__(self, storage: StorageService):
        self.storage = storage

    def calculate_plan_for_zone(
        self,
        zone: Zone,
        latest_env: Optional[EnvironmentRecord],
        standards_map: Dict[str, CropStandard],
        settings: SystemSettings,
        today_illuminance_hours: Optional[float] = None
    ) -> Tuple[CostPlan, List[CostPlan]]:
        """
        단일 구역에 대한 운영 계획 후보군 생성 및 최적(최저비용) 계획 산출
        Returns: (optimal_plan, all_candidate_plans)
        """
        crop_std = standards_map.get(zone.crop_type, DEFAULT_CROP_STANDARDS.get("토마토"))

        # 최신 환경 기록이 없는 경우 기본 평균값 가상 적용
        cur_moisture = latest_env.soil_moisture if latest_env else 24.0
        cur_temp = latest_env.temperature if latest_env else 26.0
        cur_hum = latest_env.humidity if latest_env else 70.0
        cur_lux = latest_env.illuminance if latest_env else 20000.0

        # 1. 관개/수분 판단 (요구사항 16, 17)
        moisture_status = crop_std.evaluate_moisture(cur_moisture)
        water_liters = crop_std.calculate_water_liters(zone.area, cur_moisture)
        water_m3 = water_liters / 1000.0
        water_cost = round(water_m3 * settings.water_unit_price, 0)

        # 2. 온습도 상태 평가 (요구사항 19)
        temp_status = crop_std.evaluate_temperature(cur_temp)
        hum_status = crop_std.evaluate_humidity(cur_hum)

        # 3. 조도 및 보광 필요시간 계산 (요구사항 20, 21)
        needed_light_hours = 0.0
        if today_illuminance_hours is not None:
            deficit = crop_std.target_light_hours - today_illuminance_hours
            needed_light_hours = max(0.0, round(deficit, 1))
        else:
            if cur_lux < crop_std.target_illuminance:
                needed_light_hours = 2.0  # 현재 조도 부족 시 기본 2시간 권장
            else:
                needed_light_hours = 0.0

        # 장비 참조
        fan = next((eq for eq in settings.equipments if eq.equipment_type == "fan"), VentilationFan())
        light = next((eq for eq in settings.equipments if eq.equipment_type == "light"), GrowLight())
        heater = next((eq for eq in settings.equipments if eq.equipment_type == "heater"), Heater())

        # 4. 장비 가동 후보군 시뮬레이션 (요구사항 22, 23, 24, 25)
        candidates: List[CostPlan] = []

        # 후보 옵션들 정의: (후보명, 팬 분, 보광 시간, 히터 분, 작업순서)
        candidate_configs = [
            ("후보 1 (최소 가동 / 기본 유지)", 0.0, 0.0, 0.0, "장비 미가동 (자연 환기 및 자연광 유지)"),
            ("후보 2 (표준 환기 10분 + 필요시 보광)", 10.0, needed_light_hours, 0.0, "환기팬 10분 가동 → 기온 재확인 → 필요시 보광등 가동"),
            ("후보 3 (집중 환기 20분 + 충분 보광)", 20.0, needed_light_hours if needed_light_hours > 0 else 1.0, 0.0, "환기팬 20분 집중 환기 → 습도 저감 후 보광등 가동"),
        ]

        # 기온이 너무 낮을 경우 히터 가동 후보 추가
        if cur_temp < crop_std.temp_min:
            candidate_configs.append(
                ("후보 4 (저온 대비 온풍 난방 15분)", 0.0, needed_light_hours, 15.0, "온풍난방기 15분 가동으로 설정 온도 회복")
            )

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        last_water_text = zone.last_watering_date if zone.last_watering_date else "급수 기록 없음"

        for title, fan_min, light_h, heater_min, action_seq in candidate_configs:
            ops: List[EquipmentOperation] = []
            total_kwh = 0.0
            total_elec_cost = 0.0

            # 환기팬
            if fan_min > 0:
                fan_kwh = fan.calculate_kwh(fan_min / 60.0)
                fan_cost = fan_kwh * settings.electricity_unit_price
                ops.append(EquipmentOperation(
                    equipment_name=fan.name,
                    equipment_type="fan",
                    duration_minutes=fan_min,
                    power_watt=fan.power_watt,
                    kwh=round(fan_kwh, 3),
                    cost=round(fan_cost, 0)
                ))
                total_kwh += fan_kwh
                total_elec_cost += fan_cost

            # 난방기
            if heater_min > 0:
                h_kwh = heater.calculate_kwh(heater_min / 60.0)
                h_cost = h_kwh * settings.electricity_unit_price
                ops.append(EquipmentOperation(
                    equipment_name=heater.name,
                    equipment_type="heater",
                    duration_minutes=heater_min,
                    power_watt=heater.power_watt,
                    kwh=round(h_kwh, 3),
                    cost=round(h_cost, 0)
                ))
                total_kwh += h_kwh
                total_elec_cost += h_cost

            # 보광등
            if light_h > 0:
                l_kwh = light.calculate_kwh(light_h)
                l_cost = l_kwh * settings.electricity_unit_price
                ops.append(EquipmentOperation(
                    equipment_name=light.name,
                    equipment_type="light",
                    duration_minutes=light_h * 60.0,
                    power_watt=light.power_watt,
                    kwh=round(l_kwh, 3),
                    cost=round(l_cost, 0)
                ))
                total_kwh += l_kwh
                total_elec_cost += l_cost

            # 환경 변화 시뮬레이션
            sim_temp, sim_hum = cur_temp, cur_hum
            if fan_min > 0:
                sim_temp, sim_hum = fan.simulate_effect(fan_min, sim_temp, sim_hum)
            if heater_min > 0:
                sim_temp, sim_hum = heater.simulate_effect(heater_min, sim_temp, sim_hum)
            if light_h > 0:
                sim_temp, sim_hum = light.simulate_effect(light_h * 60.0, sim_temp, sim_hum)

            # 기준 충족 여부 및 미충족 사유 분석
            issues = []
            if sim_temp < crop_std.temp_min:
                issues.append(f"기온 미달(현재 {sim_temp}℃ < 최저 {crop_std.temp_min}℃)")
            elif sim_temp > crop_std.temp_max:
                issues.append(f"온도 상한 초과(현재 {sim_temp}℃ > 최고 {crop_std.temp_max}℃)")

            if sim_hum > crop_std.humidity_max:
                issues.append(f"습도 과다(현재 {sim_hum}% > 최고 {crop_std.humidity_max}%)")
            elif sim_hum < crop_std.humidity_min:
                issues.append(f"습도 부족(현재 {sim_hum}% < 최저 {crop_std.humidity_min}%)")

            if needed_light_hours > 0 and light_h < needed_light_hours:
                issues.append(f"보광 부족({needed_light_hours - light_h:.1f}시간 부족)")

            meets_criteria = (len(issues) == 0)
            unmet_str = ", ".join(issues) if issues else "모든 생육 기준 충족"

            plan = CostPlan(
                plan_id=f"plan_{uuid.uuid4().hex[:8]}",
                zone_id=zone.zone_id,
                zone_name=zone.name,
                crop_type=zone.crop_type,
                created_at=now_str,
                moisture_status=moisture_status,
                last_watering_date=last_water_text,
                recommended_water_liter=water_liters,
                water_cost=water_cost,
                predicted_temp=sim_temp,
                predicted_humidity=sim_hum,
                additional_light_hours=light_h,
                operations=ops,
                total_kwh=round(total_kwh, 3),
                electricity_cost=round(total_elec_cost, 0),
                total_cost=round(water_cost + total_elec_cost, 0),
                meets_criteria=meets_criteria,
                unmet_issues=unmet_str,
                action_sequence=action_seq,
                candidate_name=title
            )
            candidates.append(plan)

        # 5. 최저비용 추천 알고리즘 (요구사항 26)
        # 생육 기준을 충족하는 후보 중 총비용이 가장 낮은 것을 우선 추천
        valid_candidates = [c for c in candidates if c.meets_criteria]
        if valid_candidates:
            optimal_plan = min(valid_candidates, key=lambda c: c.total_cost)
        else:
            # 기준을 모두 충족하는 후보가 없으면 총비용이 가장 낮은 것을 고르고 미충족 사유 명시
            optimal_plan = min(candidates, key=lambda c: c.total_cost)

        return optimal_plan, candidates

    def save_plan(self, plan: CostPlan) -> bool:
        """선택한 계획 저장 (요구사항 28)"""
        plans = self.storage.get_plans()
        plans.append(plan)
        self.storage.save_plans(plans)
        return True

    def get_plans_for_zone(self, zone_id: str) -> List[CostPlan]:
        """특정 구역에 저장된 계획 목록 조회"""
        plans = self.storage.get_plans()
        return [p for p in plans if p.zone_id == zone_id]
