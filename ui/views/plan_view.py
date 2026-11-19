"""
ui/views/plan_view.py
저비용 운영 계획 수립, 장비 가동 시뮬레이션 및 최저비용 추천 뷰 (요구사항 C: 15~28)
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, List, Dict

from ui.styles import AppTheme
from models.zone import Zone
from models.cost_plan import CostPlan
from services.auth_service import AuthService
from services.zone_service import ZoneService
from services.environment_service import EnvironmentService
from services.optimization_service import OptimizationService
from services.storage_service import StorageService


class PlanView(tk.Frame):
    """
    메뉴 2: 저비용 운영 계획 화면
    - 15: [계획 계산] 트리거 및 도메인 데이터 로드
    - 16, 17, 18: 토양 수분 판정, 권장 급수량(L) 산출, 구역별 권장량 요약 표 및 합산
    - 19: 기온·습도 적정 범위 비교 ('낮음', '적정', '높음')
    - 20, 21: 조도 비교 및 보광 시간 계산
    - 22, 23: 장비 가동 후보군 시뮬레이션 및 작업 순서 도출
    - 24, 25: 전력량(kWh), 물·전기 비용 및 총 예상 운영비 산출
    - 26, 27: 최저비용 추천 계획 하이라이트 표시
    - 28: [후보 비교] 목록 뷰 및 [계획 저장]
    """

    def __init__(
        self,
        parent,
        auth_service: AuthService,
        zone_service: ZoneService,
        env_service: EnvironmentService,
        opt_service: OptimizationService,
        storage: StorageService,
        on_navigate: Callable[[str], None],
        **kwargs
    ):
        super().__init__(parent, bg=AppTheme.BG_LIGHT, **kwargs)
        self.auth_service = auth_service
        self.zone_service = zone_service
        self.env_service = env_service
        self.opt_service = opt_service
        self.storage = storage
        self.on_navigate = on_navigate

        self.current_zones: List[Zone] = []
        self.selected_zone: Optional[Zone] = None
        self.current_optimal_plan: Optional[CostPlan] = None
        self.current_candidates: List[CostPlan] = []

        self._build_ui()

    def _build_ui(self) -> None:
        # 캔버스 스크롤 지원
        canvas = tk.Canvas(self, bg=AppTheme.BG_LIGHT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.content_frame = tk.Frame(canvas, bg=AppTheme.BG_LIGHT, padx=20, pady=16)

        self.content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 1. 상단 컨트롤 바 (구역 선택 & 계산 버튼) (요구사항 15)
        top_bar = tk.Frame(
            self.content_frame,
            bg=AppTheme.SURFACE,
            highlightbackground=AppTheme.BORDER,
            highlightthickness=1,
            padx=18,
            pady=14
        )
        top_bar.pack(fill="x", pady=(0, 16))

        bar_left = tk.Frame(top_bar, bg=AppTheme.SURFACE)
        bar_left.pack(side="left")

        tk.Label(
            bar_left,
            text="분석 대상 구역:",
            font=AppTheme.FONT_BODY_BOLD,
            bg=AppTheme.SURFACE
        ).pack(side="left", padx=(0, 8))

        self.cb_zone = ttk.Combobox(bar_left, state="readonly", width=26, font=AppTheme.FONT_BODY)
        self.cb_zone.pack(side="left", padx=(0, 14))

        # 누적 일조 시간 옵션 (선택적)
        tk.Label(
            bar_left,
            text="오늘 누적 일조(h, 선택):",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.SURFACE
        ).pack(side="left", padx=(0, 4))

        self.ent_light_hours = ttk.Entry(bar_left, width=6, font=AppTheme.FONT_BODY)
        self.ent_light_hours.pack(side="left")

        btn_calc = tk.Button(
            top_bar,
            text="⚡ 저비용 운영 계획 계산",
            font=AppTheme.FONT_BODY_BOLD,
            bg=AppTheme.PRIMARY,
            fg=AppTheme.TEXT_WHITE,
            activebackground=AppTheme.PRIMARY_LIGHT,
            activeforeground=AppTheme.TEXT_WHITE,
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            command=self._handle_calculate
        )
        btn_calc.pack(side="right")

        # 2. 전체 구역 권장 급수량 요약 표 (요구사항 18)
        self.summary_table_frame = tk.Frame(
            self.content_frame,
            bg=AppTheme.SURFACE,
            highlightbackground=AppTheme.BORDER,
            highlightthickness=1,
            padx=18,
            pady=14
        )
        self.summary_table_frame.pack(fill="x", pady=(0, 16))

        tk.Label(
            self.summary_table_frame,
            text="💧 구역별 관개(급수) 판단 및 권장량 요약",
            font=AppTheme.FONT_HEAD_MD,
            fg=AppTheme.PRIMARY,
            bg=AppTheme.SURFACE
        ).pack(anchor="w", pady=(0, 8))

        # Treeview 요약 테이블
        table_cols = ("zone", "crop", "moisture", "status", "last_water", "water_liter", "water_cost")
        self.tree_summary = ttk.Treeview(
            self.summary_table_frame,
            columns=table_cols,
            show="headings",
            height=3
        )
        self.tree_summary.heading("zone", text="구역명")
        self.tree_summary.heading("crop", text="작물")
        self.tree_summary.heading("moisture", text="현재 토양수분")
        self.tree_summary.heading("status", text="판단 결과")
        self.tree_summary.heading("last_water", text="최근 급수일")
        self.tree_summary.heading("water_liter", text="권장 급수량")
        self.tree_summary.heading("water_cost", text="예상 물 비용")

        self.tree_summary.column("zone", width=140, anchor="w")
        self.tree_summary.column("crop", width=80, anchor="center")
        self.tree_summary.column("moisture", width=100, anchor="center")
        self.tree_summary.column("status", width=90, anchor="center")
        self.tree_summary.column("last_water", width=110, anchor="center")
        self.tree_summary.column("water_liter", width=120, anchor="e")
        self.tree_summary.column("water_cost", width=110, anchor="e")

        self.tree_summary.pack(fill="x", pady=(0, 8))

        self.lbl_total_water = tk.Label(
            self.summary_table_frame,
            text="전체 권장 급수량 합계: 0 L (예상 물 비용: 0원)",
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.PRIMARY,
            bg=AppTheme.SURFACE
        )
        self.lbl_total_water.pack(anchor="e")

        # 3. 최적 추천 운영 계획 메인 카드 (요구사항 26, 27)
        self.optimal_card = tk.Frame(
            self.content_frame,
            bg=AppTheme.SURFACE,
            highlightbackground=AppTheme.PRIMARY_LIGHT,
            highlightthickness=2,
            padx=20,
            pady=18
        )
        self.optimal_card.pack(fill="x", pady=(0, 16))

        self._render_optimal_placeholder()

        # 4. 후보군 비교 섹션 (요구사항 28)
        self.compare_frame = tk.Frame(
            self.content_frame,
            bg=AppTheme.SURFACE,
            highlightbackground=AppTheme.BORDER,
            highlightthickness=1,
            padx=18,
            pady=16
        )
        self.compare_frame.pack(fill="x", pady=(0, 16))

        tk.Label(
            self.compare_frame,
            text="📊 장비 가동 후보군 상세 비교 (비용 및 생육 기준 충족 여부)",
            font=AppTheme.FONT_HEAD_MD,
            fg=AppTheme.TEXT_MAIN,
            bg=AppTheme.SURFACE
        ).pack(anchor="w", pady=(0, 8))

        cand_cols = ("name", "fan", "light", "pred_temp", "pred_hum", "kwh", "elec_cost", "total_cost", "meets")
        self.tree_cand = ttk.Treeview(
            self.compare_frame,
            columns=cand_cols,
            show="headings",
            height=4
        )
        self.tree_cand.heading("name", text="후보 계획명")
        self.tree_cand.heading("fan", text="환기팬 가동")
        self.tree_cand.heading("light", text="보광등 가동")
        self.tree_cand.heading("pred_temp", text="예상 기온")
        self.tree_cand.heading("pred_hum", text="예상 습도")
        self.tree_cand.heading("kwh", text="예상 전력량")
        self.tree_cand.heading("elec_cost", text="전기 비용")
        self.tree_cand.heading("total_cost", text="총 예상비용")
        self.tree_cand.heading("meets", text="기준 충족 여부")

        self.tree_cand.column("name", width=180, anchor="w")
        self.tree_cand.column("fan", width=90, anchor="center")
        self.tree_cand.column("light", width=90, anchor="center")
        self.tree_cand.column("pred_temp", width=80, anchor="center")
        self.tree_cand.column("pred_hum", width=80, anchor="center")
        self.tree_cand.column("kwh", width=90, anchor="e")
        self.tree_cand.column("elec_cost", width=90, anchor="e")
        self.tree_cand.column("total_cost", width=100, anchor="e")
        self.tree_cand.column("meets", width=140, anchor="center")

        self.tree_cand.pack(fill="x")

    def _render_optimal_placeholder(self) -> None:
        for w in self.optimal_card.winfo_children():
            w.destroy()

        tk.Label(
            self.optimal_card,
            text="상단에서 구역을 선택한 후 [저비용 운영 계획 계산] 버튼을 누르면\n생육 기준 충족 여부와 최소 비용을 종합 분석한 최적 추천 계획이 표시됩니다.",
            font=AppTheme.FONT_BODY,
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.SURFACE,
            justify="center",
            pady=20
        ).pack()

    def refresh(self) -> None:
        """화면 진입 시 데이터 로드"""
        user = self.auth_service.get_current_user()
        if not user:
            return

        self.current_zones = self.zone_service.get_user_zones(user.user_id)
        if not self.current_zones:
            self.cb_zone["values"] = []
            return

        self.cb_zone["values"] = [f"{z.name} ({z.crop_type})" for z in self.current_zones]
        self.cb_zone.current(0)

        # 전체 구역 급수 요약 테이블 즉시 초기 계산
        self._populate_all_zones_summary()

    def _populate_all_zones_summary(self) -> None:
        """모든 구역에 대한 급수 필요 여부 및 권장량 합산 표 (요구사항 18)"""
        for item in self.tree_summary.get_children():
            self.tree_summary.delete(item)

        standards = self.storage.get_standards()
        settings = self.storage.get_settings()

        total_liters = 0.0
        total_water_cost = 0.0

        for zone in self.current_zones:
            latest = self.env_service.get_latest_record(zone.zone_id)
            cur_moisture = latest.soil_moisture if latest else 24.0
            crop_std = standards.get(zone.crop_type)

            if crop_std:
                status = crop_std.evaluate_moisture(cur_moisture)
                water_l = crop_std.calculate_water_liters(zone.area, cur_moisture)
            else:
                status = "급수 필요" if cur_moisture < 25.0 else "급수 보류"
                water_l = zone.area * 10.0 if status == "급수 필요" else 0.0

            w_cost = round((water_l / 1000.0) * settings.water_unit_price, 0)
            total_liters += water_l
            total_water_cost += w_cost

            self.tree_summary.insert(
                "",
                "end",
                values=(
                    zone.name,
                    zone.crop_type,
                    f"{cur_moisture:.1f}%",
                    status,
                    zone.last_watering_date or "급수 기록 없음",
                    f"{water_l:,.1f} L",
                    f"{w_cost:,.0f} 원"
                )
            )

        self.lbl_total_water.config(
            text=f"전체 권장 급수량 합계: {total_liters:,.1f} L (예상 물 비용: {total_water_cost:,.0f} 원)"
        )

    def _handle_calculate(self) -> None:
        idx = self.cb_zone.current()
        if idx < 0 or idx >= len(self.current_zones):
            messagebox.showwarning("알림", "분석할 구역을 선택해 주세요.")
            return

        self.selected_zone = self.current_zones[idx]
        latest_env = self.env_service.get_latest_record(self.selected_zone.zone_id)
        standards = self.storage.get_standards()
        settings = self.storage.get_settings()

        # 누적 일조 시간 파싱 (선택적)
        hours_input = self.ent_light_hours.get().strip()
        light_h_opt = None
        if hours_input:
            try:
                light_h_opt = float(hours_input)
            except ValueError:
                pass

        # 최적화 알고리즘 실행
        optimal, candidates = self.opt_service.calculate_plan_for_zone(
            zone=self.selected_zone,
            latest_env=latest_env,
            standards_map=standards,
            settings=settings,
            today_illuminance_hours=light_h_opt
        )

        self.current_optimal_plan = optimal
        self.current_candidates = candidates

        # 결과 화면 렌더링 (요구사항 26, 27)
        self._render_optimal_plan(optimal, latest_env)

        # 후보군 테이블 갱신 (요구사항 28)
        self._populate_candidates_table(candidates)

    def _render_optimal_plan(self, plan: CostPlan, env) -> None:
        for w in self.optimal_card.winfo_children():
            w.destroy()

        # 헤더: 추천 뱃지 및 타이틀
        head_f = tk.Frame(self.optimal_card, bg=AppTheme.SURFACE)
        head_f.pack(fill="x", pady=(0, 10))

        tk.Label(
            head_f,
            text="⭐ 추천 최저비용 운영 계획",
            font=AppTheme.FONT_HEAD_MD,
            fg=AppTheme.PRIMARY,
            bg=AppTheme.SURFACE
        ).pack(side="left")

        badge_col = AppTheme.SUCCESS if plan.meets_criteria else AppTheme.WARNING
        tk.Label(
            head_f,
            text=f" {plan.unmet_issues} ",
            font=AppTheme.FONT_SMALL,
            fg=badge_col,
            bg="#F1F5F9",
            padx=8,
            pady=3
        ).pack(side="left", padx=(10, 0))

        # 계획 저장 버튼 (요구사항 28)
        btn_save = tk.Button(
            head_f,
            text="💾 이 계획 저장하기",
            font=AppTheme.FONT_BODY_BOLD,
            bg=AppTheme.PRIMARY,
            fg=AppTheme.TEXT_WHITE,
            activebackground=AppTheme.PRIMARY_LIGHT,
            activeforeground=AppTheme.TEXT_WHITE,
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._save_current_plan
        )
        btn_save.pack(side="right")

        # 권장 작업 순서 박스 (요구사항 23)
        act_box = tk.Frame(self.optimal_card, bg="#F0FDF4", highlightbackground="#86EFAC", highlightthickness=1, padx=12, pady=8)
        act_box.pack(fill="x", pady=(0, 12))

        tk.Label(
            act_box,
            text=f"📋 권장 작업 순서: {plan.action_sequence}",
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.PRIMARY,
            bg="#F0FDF4"
        ).pack(anchor="w")

        # 4분할 지표 그리드
        stat_grid = tk.Frame(self.optimal_card, bg=AppTheme.SURFACE)
        stat_grid.pack(fill="x", pady=(0, 12))
        for col in range(4):
            stat_grid.columnconfigure(col, weight=1)

        # 1) 급수 권장
        col1 = tk.Frame(stat_grid, bg=AppTheme.SURFACE_ALT, padx=12, pady=10)
        col1.grid(row=0, column=0, sticky="nsew", padx=4)
        tk.Label(col1, text="권장 급수량", font=AppTheme.FONT_SMALL, fg=AppTheme.TEXT_MUTED, bg=AppTheme.SURFACE_ALT).pack(anchor="w")
        tk.Label(col1, text=f"{plan.recommended_water_liter:,.0f} L", font=AppTheme.FONT_HEAD_MD, fg=AppTheme.PRIMARY, bg=AppTheme.SURFACE_ALT).pack(anchor="w")
        tk.Label(col1, text=f"판단: {plan.moisture_status} (최근 급수: {plan.last_watering_date})", font=AppTheme.FONT_SMALL, fg=AppTheme.TEXT_MUTED, bg=AppTheme.SURFACE_ALT).pack(anchor="w")

        # 2) 온습도 예측
        col2 = tk.Frame(stat_grid, bg=AppTheme.SURFACE_ALT, padx=12, pady=10)
        col2.grid(row=0, column=1, sticky="nsew", padx=4)
        tk.Label(col2, text="조절 후 예상 기온/습도", font=AppTheme.FONT_SMALL, fg=AppTheme.TEXT_MUTED, bg=AppTheme.SURFACE_ALT).pack(anchor="w")
        tk.Label(col2, text=f"{plan.predicted_temp:.1f}℃ / {plan.predicted_humidity:.1f}%", font=AppTheme.FONT_HEAD_MD, fg=AppTheme.TEXT_MAIN, bg=AppTheme.SURFACE_ALT).pack(anchor="w")
        tk.Label(col2, text="장비 가동 후 환경 수렴치", font=AppTheme.FONT_SMALL, fg=AppTheme.TEXT_MUTED, bg=AppTheme.SURFACE_ALT).pack(anchor="w")

        # 3) 보광 시간
        col3 = tk.Frame(stat_grid, bg=AppTheme.SURFACE_ALT, padx=12, pady=10)
        col3.grid(row=0, column=2, sticky="nsew", padx=4)
        tk.Label(col3, text="추가 보광 시간", font=AppTheme.FONT_SMALL, fg=AppTheme.TEXT_MUTED, bg=AppTheme.SURFACE_ALT).pack(anchor="w")
        tk.Label(col3, text=f"{plan.additional_light_hours:.1f} 시간", font=AppTheme.FONT_HEAD_MD, fg=AppTheme.TEXT_MAIN, bg=AppTheme.SURFACE_ALT).pack(anchor="w")
        tk.Label(col3, text="LED 식물생장등 기준", font=AppTheme.FONT_SMALL, fg=AppTheme.TEXT_MUTED, bg=AppTheme.SURFACE_ALT).pack(anchor="w")

        # 4) 총 예상 운영비
        col4 = tk.Frame(stat_grid, bg="#FEF3C7", highlightbackground="#FDE68A", highlightthickness=1, padx=12, pady=10)
        col4.grid(row=0, column=3, sticky="nsew", padx=4)
        tk.Label(col4, text="총 예상 운영비 (물+전기)", font=AppTheme.FONT_SMALL, fg="#92400E", bg="#FEF3C7").pack(anchor="w")
        tk.Label(col4, text=f"{plan.total_cost:,.0f} 원", font=AppTheme.FONT_HEAD_MD, fg="#B45309", bg="#FEF3C7").pack(anchor="w")
        tk.Label(col4, text=f"물 {plan.water_cost:,.0f}원 + 전기 {plan.electricity_cost:,.0f}원", font=AppTheme.FONT_SMALL, fg="#92400E", bg="#FEF3C7").pack(anchor="w")

    def _populate_candidates_table(self, candidates: List[CostPlan]) -> None:
        for item in self.tree_cand.get_children():
            self.tree_cand.delete(item)

        for c in candidates:
            # 환기팬 분
            fan_op = next((op for op in c.operations if op.equipment_type == "fan"), None)
            fan_str = f"{fan_op.duration_minutes:.0f}분" if fan_op else "0분"

            # 보광 시간
            light_op = next((op for op in c.operations if op.equipment_type == "light"), None)
            light_str = f"{c.additional_light_hours:.1f}시간" if c.additional_light_hours > 0 else "0시간"

            meets_str = "✔ 적합 (기준 충족)" if c.meets_criteria else f"⚠ {c.unmet_issues}"

            self.tree_cand.insert(
                "",
                "end",
                values=(
                    c.candidate_name,
                    fan_str,
                    light_str,
                    f"{c.predicted_temp:.1f}℃",
                    f"{c.predicted_humidity:.1f}%",
                    f"{c.total_kwh:.3f} kWh",
                    f"{c.electricity_cost:,.0f}원",
                    f"{c.total_cost:,.0f}원",
                    meets_str
                )
            )

    def _save_current_plan(self) -> None:
        if not self.current_optimal_plan:
            return

        self.opt_service.save_plan(self.current_optimal_plan)
        messagebox.showinfo(
            "계획 저장 완료",
            f"'{self.current_optimal_plan.zone_name}'의 운영 계획이 성공적으로 저장되었습니다.\n"
            f"[사용량·비용 이력] 메뉴에서 이 계획을 불러와 실제 작업 결과를 기록할 수 있습니다."
        )
