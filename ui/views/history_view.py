"""
ui/views/history_view.py
사용량과 비용 이력 등록, 기간별 통계 및 계획 vs 실적 비교 뷰 (요구사항 D: 29~35)
"""
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, List, Dict

from ui.styles import AppTheme
from models.zone import Zone
from models.cost_plan import CostPlan
from models.usage_history import UsageHistory
from services.auth_service import AuthService
from services.zone_service import ZoneService
from services.history_service import HistoryService
from services.storage_service import StorageService


class HistoryView(tk.Frame):
    """
    메뉴 3: 사용량·비용 이력 및 통계 화면
    - 29: 계획 불러오기 (날짜 및 구역 선택)
    - 30, 31: 실제 급수량(L), 장비 가동시간, 보광등 시간, 실측/추정 전력량 입력
    - 32: [실적 저장] 및 최근 급수일 자동 반영
    - 33: 조회 기간 필터 (일별, 주별, 월별, 전체, 구역별)
    - 34: 통계 지표 집계 (총 물, 총 보광시간, 총 전력량, 총비용)
    - 35: 계획 vs 실적 비교 분석 테이블
    """

    def __init__(
        self,
        parent,
        auth_service: AuthService,
        zone_service: ZoneService,
        history_service: HistoryService,
        storage: StorageService,
        on_navigate: Callable[[str], None],
        **kwargs
    ):
        super().__init__(parent, bg=AppTheme.BG_LIGHT, **kwargs)
        self.auth_service = auth_service
        self.zone_service = zone_service
        self.history_service = history_service
        self.storage = storage
        self.on_navigate = on_navigate

        self.current_zones: List[Zone] = []
        self.available_plans: List[CostPlan] = []
        self.selected_plan: Optional[CostPlan] = None

        self._build_ui()

    def _build_ui(self) -> None:
        # 좌우 분할 구조 (좌측: 실적 등록 / 우측: 이력 조회, 통계 및 계획 대비 실적)
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=6)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # [좌측] 실제 작업 실적 입력 폼 (요구사항 29~32)
        # ==========================================
        left_card = tk.Frame(
            self,
            bg=AppTheme.SURFACE,
            highlightbackground=AppTheme.BORDER,
            highlightthickness=1,
            padx=20,
            pady=18
        )
        left_card.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)

        tk.Label(
            left_card,
            text="✍ 오늘 작업 실적 등록",
            font=AppTheme.FONT_HEAD_MD,
            fg=AppTheme.PRIMARY,
            bg=AppTheme.SURFACE
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            left_card,
            text="실제 투입한 급수량 및 장비 가동 시간을 기록합니다.",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.SURFACE
        ).pack(anchor="w", pady=(0, 12))

        # 1. 계획 불러오기 (요구사항 29)
        plan_box = tk.Frame(left_card, bg=AppTheme.SURFACE_ALT, padx=10, pady=8)
        plan_box.pack(fill="x", pady=(0, 10))

        tk.Label(
            plan_box,
            text="저장된 운영 계획 불러오기 (선택):",
            font=AppTheme.FONT_BODY_BOLD,
            bg=AppTheme.SURFACE_ALT
        ).pack(anchor="w", pady=(0, 2))

        self.cb_plan = ttk.Combobox(plan_box, state="readonly", font=AppTheme.FONT_SMALL)
        self.cb_plan.pack(fill="x", pady=(0, 4))
        self.cb_plan.bind("<<ComboboxSelected>>", self._on_plan_selected)

        self.lbl_plan_hint = tk.Label(
            plan_box,
            text="계획을 선택하면 권장 급수량 및 목표 시간이 자동 연동됩니다.",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.SURFACE_ALT
        )
        self.lbl_plan_hint.pack(anchor="w")

        # 2. 기본 정보 (구역, 일자)
        tk.Label(left_card, text="대상 재배 구역", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).pack(anchor="w", pady=(2, 2))
        self.cb_zone = ttk.Combobox(left_card, state="readonly", font=AppTheme.FONT_BODY)
        self.cb_zone.pack(fill="x", pady=(0, 8))

        tk.Label(left_card, text="작업 일자 (YYYY-MM-DD)", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).pack(anchor="w", pady=(2, 2))
        self.ent_date = ttk.Entry(left_card, font=AppTheme.FONT_BODY)
        self.ent_date.pack(fill="x", pady=(0, 8))
        self.ent_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # 3. 실적 수치 입력 필드들 (요구사항 30)
        grid_f = tk.Frame(left_card, bg=AppTheme.SURFACE)
        grid_f.pack(fill="x", pady=(2, 10))
        grid_f.columnconfigure(0, weight=1)
        grid_f.columnconfigure(1, weight=1)

        # 실제 급수량 (L)
        tk.Label(grid_f, text="실제 급수량 (L)", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).grid(row=0, column=0, sticky="w", padx=(0, 4))
        self.ent_water = ttk.Entry(grid_f, font=AppTheme.FONT_BODY)
        self.ent_water.grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=(2, 8))
        self.ent_water.insert(0, "0")

        # 보광등 켠 시간 (h)
        tk.Label(grid_f, text="보광등 켠 시간 (시간)", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).grid(row=0, column=1, sticky="w", padx=(4, 0))
        self.ent_light_h = ttk.Entry(grid_f, font=AppTheme.FONT_BODY)
        self.ent_light_h.grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=(2, 8))
        self.ent_light_h.insert(0, "0")

        # 환기팬 가동 (분)
        tk.Label(grid_f, text="환기팬 가동 (분)", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).grid(row=2, column=0, sticky="w", padx=(0, 4))
        self.ent_fan_min = ttk.Entry(grid_f, font=AppTheme.FONT_BODY)
        self.ent_fan_min.grid(row=3, column=0, sticky="ew", padx=(0, 4), pady=(2, 8))
        self.ent_fan_min.insert(0, "0")

        # 난방기 가동 (분)
        tk.Label(grid_f, text="난방기 가동 (분)", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).grid(row=2, column=1, sticky="w", padx=(4, 0))
        self.ent_heater_min = ttk.Entry(grid_f, font=AppTheme.FONT_BODY)
        self.ent_heater_min.grid(row=3, column=1, sticky="ew", padx=(4, 0), pady=(2, 8))
        self.ent_heater_min.insert(0, "0")

        # 직접 측정 전력량 (선택적) (요구사항 30, 31)
        tk.Label(
            left_card,
            text="직접 측정 전력량 (kWh, 비워둘 시 장비 사양으로 자동 추정)",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.SURFACE
        ).pack(anchor="w", pady=(2, 2))

        self.ent_measured_kwh = ttk.Entry(left_card, font=AppTheme.FONT_BODY)
        self.ent_measured_kwh.pack(fill="x", pady=(0, 14))

        # 저장 버튼 (요구사항 32)
        btn_save_hist = tk.Button(
            left_card,
            text="💾 실적 저장 및 최근 급수일 반영",
            font=AppTheme.FONT_BODY_BOLD,
            bg=AppTheme.PRIMARY,
            fg=AppTheme.TEXT_WHITE,
            activebackground=AppTheme.PRIMARY_LIGHT,
            activeforeground=AppTheme.TEXT_WHITE,
            bd=0,
            pady=10,
            cursor="hand2",
            command=self._handle_save_actual
        )
        btn_save_hist.pack(fill="x")

        # ==========================================
        # [우측] 이력 조회, 통계 및 계획 대비 실적 (요구사항 33~35)
        # ==========================================
        right_card = tk.Frame(
            self,
            bg=AppTheme.SURFACE,
            highlightbackground=AppTheme.BORDER,
            highlightthickness=1,
            padx=20,
            pady=18
        )
        right_card.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=16)

        # 상단 필터 바 (요구사항 33)
        filter_box = tk.Frame(right_card, bg=AppTheme.SURFACE)
        filter_box.pack(fill="x", pady=(0, 10))

        tk.Label(
            filter_box,
            text="📋 운영 이력 & 통계",
            font=AppTheme.FONT_HEAD_MD,
            fg=AppTheme.PRIMARY,
            bg=AppTheme.SURFACE
        ).pack(side="left")

        # 기간 필터 라디오/버튼 그룹
        btn_group = tk.Frame(filter_box, bg=AppTheme.SURFACE)
        btn_group.pack(side="right")

        self.filter_period = tk.StringVar(value="all")
        for val, lbl in [("all", "전체"), ("month", "최근 30일"), ("week", "최근 7일"), ("today", "오늘")]:
            rb = tk.Radiobutton(
                btn_group,
                text=lbl,
                value=val,
                variable=self.filter_period,
                font=AppTheme.FONT_SMALL,
                bg=AppTheme.SURFACE,
                activebackground=AppTheme.SURFACE,
                command=self._apply_filter
            )
            rb.pack(side="left", padx=2)

        # 통계 지표 요약 카드 그리드 (요구사항 34)
        self.stats_grid = tk.Frame(right_card, bg=AppTheme.SURFACE)
        self.stats_grid.pack(fill="x", pady=(0, 12))
        for col in range(4):
            self.stats_grid.columnconfigure(col, weight=1)

        self.lbl_stat_water = self._make_stat_box(self.stats_grid, 0, "총 급수량", "0 L")
        self.lbl_stat_light = self._make_stat_box(self.stats_grid, 1, "총 보광시간", "0 h")
        self.lbl_stat_kwh = self._make_stat_box(self.stats_grid, 2, "총 전력량", "0 kWh")
        self.lbl_stat_cost = self._make_stat_box(self.stats_grid, 3, "총 실적 비용", "0 원", is_highlight=True)

        # 계획 vs 실적 비교 테이블 (요구사항 35)
        tk.Label(
            right_card,
            text="🔍 계획 대비 실제 작업량 및 비용 차이 비교",
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.TEXT_MAIN,
            bg=AppTheme.SURFACE
        ).pack(anchor="w", pady=(8, 4))

        cols = ("date", "zone", "crop", "water_comp", "light_h", "kwh", "cost_comp")
        self.tree_history = ttk.Treeview(
            right_card,
            columns=cols,
            show="headings",
            height=10
        )
        self.tree_history.heading("date", text="일자")
        self.tree_history.heading("zone", text="구역")
        self.tree_history.heading("crop", text="작물")
        self.tree_history.heading("water_comp", text="급수량 (계획/실제)")
        self.tree_history.heading("light_h", text="보광시간")
        self.tree_history.heading("kwh", text="전력량")
        self.tree_history.heading("cost_comp", text="비용 (계획/실제)")

        self.tree_history.column("date", width=85, anchor="center")
        self.tree_history.column("zone", width=95, anchor="w")
        self.tree_history.column("crop", width=65, anchor="center")
        self.tree_history.column("water_comp", width=145, anchor="center")
        self.tree_history.column("light_h", width=70, anchor="center")
        self.tree_history.column("kwh", width=95, anchor="center")
        self.tree_history.column("cost_comp", width=140, anchor="center")

        self.tree_history.pack(fill="both", expand=True)

    def _make_stat_box(self, parent, col: int, title: str, default_val: str, is_highlight: bool = False) -> tk.Label:
        bg_col = "#FEF3C7" if is_highlight else AppTheme.SURFACE_ALT
        fg_col = "#B45309" if is_highlight else AppTheme.PRIMARY

        box = tk.Frame(parent, bg=bg_col, padx=10, pady=8)
        box.grid(row=0, column=col, sticky="nsew", padx=3)

        tk.Label(box, text=title, font=AppTheme.FONT_SMALL, fg=AppTheme.TEXT_MUTED, bg=bg_col).pack(anchor="w")
        lbl_val = tk.Label(box, text=default_val, font=AppTheme.FONT_HEAD_MD, fg=fg_col, bg=bg_col)
        lbl_val.pack(anchor="w", pady=(2, 0))
        return lbl_val

    def refresh(self) -> None:
        """화면 진입 시 데이터 로드"""
        user = self.auth_service.get_current_user()
        if not user:
            return

        self.current_zones = self.zone_service.get_user_zones(user.user_id)
        if self.current_zones:
            self.cb_zone["values"] = [f"{z.name} ({z.crop_type})" for z in self.current_zones]
            self.cb_zone.current(0)

        # 저장된 계획 목록 로드 (요구사항 29)
        all_plans = self.storage.get_plans()
        user_zone_ids = {z.zone_id for z in self.current_zones}
        self.available_plans = [p for p in all_plans if p.zone_id in user_zone_ids]

        plan_titles = ["(계획 없이 직접 입력)"] + [
            f"[{p.created_at[:10]}] {p.zone_name} (권장: {p.recommended_water_liter:,.0f}L / {p.total_cost:,.0f}원)"
            for p in self.available_plans
        ]
        self.cb_plan["values"] = plan_titles
        self.cb_plan.current(0)
        self.selected_plan = None

        self._apply_filter()

    def _on_plan_selected(self, event=None) -> None:
        idx = self.cb_plan.current()
        if idx <= 0:
            self.selected_plan = None
            self.lbl_plan_hint.config(text="직접 실적을 입력합니다.")
            return

        self.selected_plan = self.available_plans[idx - 1]
        p = self.selected_plan

        # 대상 구역 콤보박스 맞추기
        for i, z in enumerate(self.current_zones):
            if z.zone_id == p.zone_id:
                self.cb_zone.current(i)
                break

        # 권장값 자동 채움
        self.ent_water.delete(0, tk.END)
        self.ent_water.insert(0, str(p.recommended_water_liter))

        self.ent_light_h.delete(0, tk.END)
        self.ent_light_h.insert(0, str(p.additional_light_hours))

        # 환기팬 분
        fan_op = next((op for op in p.operations if op.equipment_type == "fan"), None)
        self.ent_fan_min.delete(0, tk.END)
        self.ent_fan_min.insert(0, str(fan_op.duration_minutes if fan_op else 0))

        self.lbl_plan_hint.config(
            text=f"✔ 계획 연동됨 (권장 급수: {p.recommended_water_liter:,.0f}L, 예상비용: {p.total_cost:,.0f}원)"
        )

    def _handle_save_actual(self) -> None:
        user = self.auth_service.get_current_user()
        if not user or not self.current_zones:
            return

        z_idx = self.cb_zone.current()
        if z_idx < 0:
            messagebox.showwarning("알림", "구역을 선택해 주세요.")
            return

        zone = self.current_zones[z_idx]
        date_str = self.ent_date.get().strip()

        try:
            water_l = float(self.ent_water.get().strip())
            light_h = float(self.ent_light_h.get().strip())
            fan_min = float(self.ent_fan_min.get().strip())
            heater_min = float(self.ent_heater_min.get().strip())
        except ValueError:
            messagebox.showwarning("입력 오류", "사용량과 가동 시간은 모두 유효한 숫자여야 합니다.")
            return

        kwh_input = self.ent_measured_kwh.get().strip()
        settings = self.storage.get_settings()

        success, msg, hist = self.history_service.save_actual_record(
            user_id=user.user_id,
            zone_id=zone.zone_id,
            zone_name=zone.name,
            crop_type=zone.crop_type,
            date_str=date_str,
            actual_water_liter=water_l,
            light_hours=light_h,
            fan_minutes=fan_min,
            heater_minutes=heater_min,
            measured_kwh_input=kwh_input,
            settings=settings,
            associated_plan=self.selected_plan
        )

        if not success:
            messagebox.showerror("저장 실패", msg)
            return

        messagebox.showinfo("저장 완료", f"실적 데이터가 성공적으로 저장되었습니다.\n{msg}")
        self._apply_filter()

    def _apply_filter(self) -> None:
        user = self.auth_service.get_current_user()
        if not user:
            return

        p_type = self.filter_period.get()
        histories = self.history_service.filter_histories(
            user_id=user.user_id,
            period_type=p_type
        )

        # 통계 지표 업데이트 (요구사항 34)
        stats = self.history_service.calculate_statistics(histories)
        self.lbl_stat_water.config(text=f"{stats['total_water_liter']:,.1f} L")
        self.lbl_stat_light.config(text=f"{stats['total_light_hours']:,.1f} h")
        self.lbl_stat_kwh.config(text=f"{stats['total_kwh']:,.2f} kWh")
        self.lbl_stat_cost.config(text=f"{stats['total_cost']:,.0f} 원")

        # 비교 테이블 갱신 (요구사항 35)
        for item in self.tree_history.get_children():
            self.tree_history.delete(item)

        if not histories:
            return

        for h in histories:
            water_comp = (
                f"{h.recommended_water_liter:,.0f}L / {h.actual_water_liter:,.0f}L"
                if h.recommended_water_liter > 0
                else f"- / {h.actual_water_liter:,.0f}L"
            )
            cost_comp = (
                f"{h.planned_total_cost:,.0f}원 / {h.total_cost:,.0f}원"
                if h.planned_total_cost > 0
                else f"- / {h.total_cost:,.0f}원"
            )
            kwh_str = f"{h.total_kwh:.2f} kWh{' (추정)' if h.is_estimated_kwh else ' (실측)'}"

            self.tree_history.insert(
                "",
                "end",
                values=(
                    h.date,
                    h.zone_name,
                    h.crop_type,
                    water_comp,
                    f"{h.light_duration_hours:.1f}h",
                    kwh_str,
                    cost_comp
                )
            )
