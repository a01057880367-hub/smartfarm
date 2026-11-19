"""
ui/views/env_input_view.py
구역별 환경 측정 데이터 입력 및 변화량 모니터링 뷰 (요구사항 B: 9~14)
"""
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, Dict, List

from ui.styles import AppTheme
from models.zone import Zone
from services.auth_service import AuthService
from services.zone_service import ZoneService
from services.environment_service import EnvironmentService


class EnvInputView(tk.Frame):
    """
    메뉴 1: 구역별 환경 입력 화면
    - 9: 구역 선택 시 작물 종류, 재배면적, 토양 종류 표시
    - 10: 최근 실제 급수일 불러오기 및 직접 입력 지원
    - 11: 측정 일시, 토양 수분(%), 기온(℃), 습도(%RH), 조도(lx) 입력
    - 12: 입력값 유효성 검사 (범위, 숫자, 날짜 정합성)
    - 13: 측정 시각과 함께 저장 및 직전 측정값 대비 변화량 표시
    - 14: [운영 계획 보기] 바로가기 지원
    """

    def __init__(
        self,
        parent,
        auth_service: AuthService,
        zone_service: ZoneService,
        env_service: EnvironmentService,
        on_navigate: Callable[[str], None],
        **kwargs
    ):
        super().__init__(parent, bg=AppTheme.BG_LIGHT, **kwargs)
        self.auth_service = auth_service
        self.zone_service = zone_service
        self.env_service = env_service
        self.on_navigate = on_navigate

        self.current_zones: List[Zone] = []
        self.selected_zone: Optional[Zone] = None

        self._build_ui()

    def _build_ui(self) -> None:
        # 좌우 분할 레이아웃
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 좌측: 입력 폼 패널
        left_card = tk.Frame(
            self,
            bg=AppTheme.SURFACE,
            highlightbackground=AppTheme.BORDER,
            highlightthickness=1,
            padx=24,
            pady=20
        )
        left_card.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)

        tk.Label(
            left_card,
            text="📊 구역별 환경 센서 측정값 입력",
            font=AppTheme.FONT_HEAD_MD,
            fg=AppTheme.PRIMARY,
            bg=AppTheme.SURFACE
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            left_card,
            text="구역을 선택하고 현재 측정된 온실 환경 데이터를 입력해 주세요.",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.SURFACE
        ).pack(anchor="w", pady=(0, 16))

        # 1. 구역 선택 (요구사항 9)
        tk.Label(left_card, text="대상 재배 구역 선택", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).pack(anchor="w")
        self.cb_zone = ttk.Combobox(left_card, state="readonly", font=AppTheme.FONT_BODY)
        self.cb_zone.pack(fill="x", pady=(2, 10))
        self.cb_zone.bind("<<ComboboxSelected>>", self._on_zone_selected)

        # 구역 상세 제원 정보 박스 (요구사항 9)
        self.info_box = tk.Frame(left_card, bg=AppTheme.SURFACE_ALT, padx=12, pady=10)
        self.info_box.pack(fill="x", pady=(0, 14))

        self.lbl_zone_info = tk.Label(
            self.info_box,
            text="구역을 선택하면 작물 종류, 면적, 토양 정보가 표시됩니다.",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.SURFACE_ALT,
            justify="left"
        )
        self.lbl_zone_info.pack(anchor="w")

        # 2. 최근 실제 급수일 (요구사항 10)
        water_row = tk.Frame(left_card, bg=AppTheme.SURFACE)
        water_row.pack(fill="x", pady=(0, 10))

        tk.Label(water_row, text="최근 실제 급수일 (YYYY-MM-DD)", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).pack(anchor="w")
        self.ent_last_water = ttk.Entry(water_row, font=AppTheme.FONT_BODY)
        self.ent_last_water.pack(fill="x", pady=(2, 0))

        # 3. 측정 일시 및 환경 입력 폼 (요구사항 11)
        grid_form = tk.Frame(left_card, bg=AppTheme.SURFACE)
        grid_form.pack(fill="x", pady=(4, 10))
        grid_form.columnconfigure(0, weight=1)
        grid_form.columnconfigure(1, weight=1)

        # 측정 일시
        tk.Label(grid_form, text="측정 날짜 및 시각", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))
        self.ent_datetime = ttk.Entry(grid_form, font=AppTheme.FONT_BODY)
        self.ent_datetime.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # 토양 수분 (%)
        tk.Label(grid_form, text="토양 수분 (%) [0~100]", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).grid(row=2, column=0, sticky="w", padx=(0, 5))
        self.ent_moisture = ttk.Entry(grid_form, font=AppTheme.FONT_BODY)
        self.ent_moisture.grid(row=3, column=0, sticky="ew", padx=(0, 5), pady=(2, 10))

        # 기온 (℃)
        tk.Label(grid_form, text="현재 기온 (℃)", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).grid(row=2, column=1, sticky="w", padx=(5, 0))
        self.ent_temp = ttk.Entry(grid_form, font=AppTheme.FONT_BODY)
        self.ent_temp.grid(row=3, column=1, sticky="ew", padx=(5, 0), pady=(2, 10))

        # 상대 습도 (%RH)
        tk.Label(grid_form, text="공기 상대습도 (%RH) [0~100]", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).grid(row=4, column=0, sticky="w", padx=(0, 5))
        self.ent_hum = ttk.Entry(grid_form, font=AppTheme.FONT_BODY)
        self.ent_hum.grid(row=5, column=0, sticky="ew", padx=(0, 5), pady=(2, 10))

        # 조도 (lx)
        tk.Label(grid_form, text="현재 조도 (lx) [>=0]", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).grid(row=4, column=1, sticky="w", padx=(5, 0))
        self.ent_lux = ttk.Entry(grid_form, font=AppTheme.FONT_BODY)
        self.ent_lux.grid(row=5, column=1, sticky="ew", padx=(5, 0), pady=(2, 10))

        # 유효성 피드백 라벨
        self.lbl_feedback = tk.Label(
            left_card,
            text="",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.DANGER,
            bg=AppTheme.SURFACE,
            wraplength=380,
            justify="left"
        )
        self.lbl_feedback.pack(anchor="w", pady=(0, 8))

        # 액션 버튼 영역
        btn_box = tk.Frame(left_card, bg=AppTheme.SURFACE)
        btn_box.pack(fill="x", pady=(4, 0))

        self.btn_save = tk.Button(
            btn_box,
            text="측정값 등록 및 저장",
            font=AppTheme.FONT_BODY_BOLD,
            bg=AppTheme.PRIMARY,
            fg=AppTheme.TEXT_WHITE,
            activebackground=AppTheme.PRIMARY_LIGHT,
            activeforeground=AppTheme.TEXT_WHITE,
            bd=0,
            pady=10,
            cursor="hand2",
            command=self._handle_save
        )
        self.btn_save.pack(side="left", fill="x", expand=True, padx=(0, 6))

        # 우측: 직전 기록 대비 변화 분석 패널 (요구사항 13, 14)
        right_card = tk.Frame(
            self,
            bg=AppTheme.SURFACE,
            highlightbackground=AppTheme.BORDER,
            highlightthickness=1,
            padx=24,
            pady=20
        )
        right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)

        tk.Label(
            right_card,
            text="📈 환경 변화 추이 및 권장 안내",
            font=AppTheme.FONT_HEAD_MD,
            fg=AppTheme.PRIMARY,
            bg=AppTheme.SURFACE
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            right_card,
            text="동일 구역의 직전 측정 기록과 비교하여 환경 변화를 실시간 분석합니다.",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.SURFACE
        ).pack(anchor="w", pady=(0, 16))

        # 변화량 표시 카드 컨테이너
        self.change_container = tk.Frame(right_card, bg=AppTheme.SURFACE)
        self.change_container.pack(fill="x", pady=(0, 16))

        self._render_placeholder_change()

        # 하단 운영 계획 바로가기 배너 (요구사항 14)
        plan_cta = tk.Frame(
            right_card,
            bg="#ECFDF5",
            highlightbackground="#A7F3D0",
            highlightthickness=1,
            padx=16,
            pady=14
        )
        plan_cta.pack(fill="x", side="bottom")

        tk.Label(
            plan_cta,
            text="💡 방금 등록한 측정값으로 최적 운영비를 계산할까요?",
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.PRIMARY,
            bg="#ECFDF5"
        ).pack(anchor="w")

        tk.Label(
            plan_cta,
            text="작물 생육 기준과 전기·물 단가를 바탕으로 최저 비용 조치 계획을 확인합니다.",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_MUTED,
            bg="#ECFDF5"
        ).pack(anchor="w", pady=(2, 10))

        btn_go_plan = tk.Button(
            plan_cta,
            text="운영 계획 보기 바로가기 →",
            font=AppTheme.FONT_BODY_BOLD,
            bg=AppTheme.PRIMARY,
            fg=AppTheme.TEXT_WHITE,
            activebackground=AppTheme.PRIMARY_LIGHT,
            activeforeground=AppTheme.TEXT_WHITE,
            bd=0,
            pady=8,
            cursor="hand2",
            command=lambda: self.on_navigate("plan")
        )
        btn_go_plan.pack(fill="x")

    def _render_placeholder_change(self) -> None:
        for w in self.change_container.winfo_children():
            w.destroy()

        box = tk.Frame(self.change_container, bg=AppTheme.SURFACE_ALT, padx=16, pady=20)
        box.pack(fill="x")
        tk.Label(
            box,
            text="측정값을 저장하면 직전 측정 기록과의\n환경 변화량(수분, 기온, 습도, 조도)이 이곳에 표시됩니다.",
            font=AppTheme.FONT_BODY,
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.SURFACE_ALT,
            justify="center"
        ).pack()

    def refresh(self) -> None:
        """화면 진입 시 구역 목록 및 기본값 갱신"""
        user = self.auth_service.get_current_user()
        if not user:
            return

        self.current_zones = self.zone_service.get_user_zones(user.user_id)
        if not self.current_zones:
            self.cb_zone["values"] = []
            self.lbl_zone_info.config(text="등록된 재배 구역이 없습니다.")
            return

        zone_names = [f"{z.name} ({z.crop_type})" for z in self.current_zones]
        self.cb_zone["values"] = zone_names
        self.cb_zone.current(0)
        self._on_zone_selected()

        # 현재 일시 자동 입력
        self.ent_datetime.delete(0, tk.END)
        self.ent_datetime.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))

    def _on_zone_selected(self, event=None) -> None:
        idx = self.cb_zone.current()
        if idx < 0 or idx >= len(self.current_zones):
            return

        self.selected_zone = self.current_zones[idx]
        z = self.selected_zone

        # 구역 제원 표시 (요구사항 9)
        self.lbl_zone_info.config(
            text=f"• 작물 종류: {z.crop_type}\n• 재배면적: {z.area:.1f} m²\n• 토양 종류: {z.soil_type}"
        )

        # 최근 급수일 표시 (요구사항 10)
        self.ent_last_water.delete(0, tk.END)
        if z.last_watering_date:
            self.ent_last_water.insert(0, z.last_watering_date)
        else:
            self.ent_last_water.insert(0, "")

        self.lbl_feedback.config(text="")

    def _handle_save(self) -> None:
        user = self.auth_service.get_current_user()
        if not user or not self.selected_zone:
            messagebox.showwarning("알림", "대상 구역을 선택해 주세요.")
            return

        rec_time = self.ent_datetime.get().strip()
        moisture_s = self.ent_moisture.get().strip()
        temp_s = self.ent_temp.get().strip()
        hum_s = self.ent_hum.get().strip()
        lux_s = self.ent_lux.get().strip()
        custom_water = self.ent_last_water.get().strip()

        # 유효성 검사 및 저장 (요구사항 12, 13)
        success, msg, record, change = self.env_service.record_environment(
            user_id=user.user_id,
            zone_id=self.selected_zone.zone_id,
            recorded_at=rec_time,
            moisture_str=moisture_s,
            temp_str=temp_s,
            hum_str=hum_s,
            lux_str=lux_s,
            custom_watering_date=custom_water
        )

        if not success:
            self.lbl_feedback.config(text=msg, fg=AppTheme.DANGER)
            return

        # 최근 급수일 입력값이 있다면 구역 정보에도 반영
        if custom_water:
            self.zone_service.update_last_watering_date(self.selected_zone.zone_id, custom_water)
            self.selected_zone.last_watering_date = custom_water

        self.lbl_feedback.config(text=msg, fg=AppTheme.SUCCESS)

        # 직전 기록과 변화량 표시 (요구사항 13)
        self._display_changes(record, change)

        messagebox.showinfo("저장 완료", f"'{self.selected_zone.name}'의 환경 측정값이 저장되었습니다.")

    def _display_changes(self, record, change: Optional[Dict[str, str]]) -> None:
        for w in self.change_container.winfo_children():
            w.destroy()

        box = tk.Frame(
            self.change_container,
            bg=AppTheme.SURFACE,
            highlightbackground="#E2E8F0",
            highlightthickness=1,
            padx=16,
            pady=14
        )
        box.pack(fill="x")

        tk.Label(
            box,
            text=f"✔ 방금 등록된 측정값 ({record.recorded_at})",
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.PRIMARY,
            bg=AppTheme.SURFACE
        ).pack(anchor="w", pady=(0, 6))

        if change:
            tk.Label(
                box,
                text=f"이전 측정({change.get('prev_time', '')}) 대비 변화:",
                font=AppTheme.FONT_SMALL,
                fg=AppTheme.TEXT_MUTED,
                bg=AppTheme.SURFACE
            ).pack(anchor="w", pady=(0, 8))

            items = [
                change.get("moisture", ""),
                change.get("temp", ""),
                change.get("hum", ""),
                change.get("lux", "")
            ]
            for it in items:
                lbl = tk.Label(
                    box,
                    text=f"• {it}",
                    font=AppTheme.FONT_BODY,
                    fg=AppTheme.TEXT_MAIN,
                    bg=AppTheme.SURFACE
                )
                lbl.pack(anchor="w", pady=1)
        else:
            tk.Label(
                box,
                text="이 구역의 첫 번째 측정 기록입니다. 다음 측정값부터 변화량이 자동 산출됩니다.",
                font=AppTheme.FONT_SMALL,
                fg=AppTheme.TEXT_MUTED,
                bg=AppTheme.SURFACE
            ).pack(anchor="w")
