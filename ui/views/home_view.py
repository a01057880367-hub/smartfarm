"""
ui/views/home_view.py
스마트팜 메인 홈 대시보드 화면 (요구사항 A: 8)
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, List

from ui.styles import AppTheme
from ui.components.stat_card import StatCard
from models.zone import Zone
from services.auth_service import AuthService
from services.zone_service import ZoneService
from services.environment_service import EnvironmentService
from services.storage_service import StorageService


class HomeView(tk.Frame):
    """
    스마트팜 메인 Home 화면
    - 프로그램 타이틀 및 농가 구역 목록 요약 표시
    - 메뉴 바로가기 큰 버튼: [구역별 환경 입력], [저비용 운영 계획], [사용량·비용 이력]
    - 재배 구역별 카드 (작물, 면적, 토양, 최근 급수일, 최신 온습도/수분)
    """

    def __init__(
        self,
        parent,
        auth_service: AuthService,
        zone_service: ZoneService,
        env_service: EnvironmentService,
        storage: StorageService,
        on_navigate: Callable[[str], None],
        **kwargs
    ):
        super().__init__(parent, bg=AppTheme.BG_LIGHT, **kwargs)
        self.auth_service = auth_service
        self.zone_service = zone_service
        self.env_service = env_service
        self.storage = storage
        self.on_navigate = on_navigate

        self._build_ui()

    def _build_ui(self) -> None:
        # 스크롤 가능한 캔버스 컨테이너 구성
        canvas = tk.Canvas(self, bg=AppTheme.BG_LIGHT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=AppTheme.BG_LIGHT, padx=24, pady=20)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=None, yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 1. 환영 인사 및 상단 요약 배너
        self.banner_frame = tk.Frame(
            self.scrollable_frame,
            bg=AppTheme.SURFACE,
            highlightbackground=AppTheme.BORDER,
            highlightthickness=1,
            padx=20,
            pady=16
        )
        self.banner_frame.pack(fill="x", pady=(0, 16))

        self.lbl_welcome = tk.Label(
            self.banner_frame,
            text="🌿 스마트팜 관제 대시보드",
            font=AppTheme.FONT_HEAD_LG,
            fg=AppTheme.PRIMARY,
            bg=AppTheme.SURFACE
        )
        self.lbl_welcome.pack(anchor="w")

        self.lbl_sub = tk.Label(
            self.banner_frame,
            text="구역별 센서 환경을 모니터링하고 실시간 최적 에너지·용수 절감 계획을 수립하세요.",
            font=AppTheme.FONT_BODY,
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.SURFACE
        )
        self.lbl_sub.pack(anchor="w", pady=(4, 0))

        # 2. 빠른 메뉴 이동 바로가기 카드 섹션 (요구사항 8)
        nav_cards_frame = tk.Frame(self.scrollable_frame, bg=AppTheme.BG_LIGHT)
        nav_cards_frame.pack(fill="x", pady=(0, 20))

        menu_shortcuts = [
            (
                "📊 구역별 환경 입력",
                "온도, 습도, 토양수분, 조도 입력 및 변화량 추적",
                "env_input",
                AppTheme.PRIMARY_LIGHT
            ),
            (
                "💡 저비용 운영 계획",
                "관개 필요량 계산 및 최저비용 장비 가동 시뮬레이션",
                "plan",
                AppTheme.PRIMARY
            ),
            (
                "📋 사용량·비용 이력",
                "실제 급수 및 전력 사용량 통계, 계획 vs 실적 비교",
                "history",
                "#2563EB"
            ),
        ]

        for i, (title, desc, route, btn_color) in enumerate(menu_shortcuts):
            card = tk.Frame(
                nav_cards_frame,
                bg=AppTheme.SURFACE,
                highlightbackground=AppTheme.BORDER,
                highlightthickness=1,
                padx=16,
                pady=14
            )
            card.pack(side="left", fill="both", expand=True, padx=(0 if i == 0 else 12, 0))

            tk.Label(
                card,
                text=title,
                font=AppTheme.FONT_HEAD_MD,
                fg=AppTheme.TEXT_MAIN,
                bg=AppTheme.SURFACE
            ).pack(anchor="w")

            tk.Label(
                card,
                text=desc,
                font=AppTheme.FONT_SMALL,
                fg=AppTheme.TEXT_MUTED,
                bg=AppTheme.SURFACE,
                wraplength=220,
                justify="left"
            ).pack(anchor="w", pady=(4, 12))

            btn = tk.Button(
                card,
                text="메뉴 이동 →",
                font=AppTheme.FONT_BODY_BOLD,
                bg=btn_color,
                fg=AppTheme.TEXT_WHITE,
                activebackground=AppTheme.PRIMARY_HOVER,
                activeforeground=AppTheme.TEXT_WHITE,
                bd=0,
                padx=12,
                pady=6,
                cursor="hand2",
                command=lambda r=route: self.on_navigate(r)
            )
            btn.pack(anchor="w")

        # 3. 재배 구역 목록 헤더
        zones_header = tk.Frame(self.scrollable_frame, bg=AppTheme.BG_LIGHT)
        zones_header.pack(fill="x", pady=(10, 8))

        tk.Label(
            zones_header,
            text="🌱 등록된 재배 구역 현황",
            font=AppTheme.FONT_HEAD_MD,
            fg=AppTheme.TEXT_MAIN,
            bg=AppTheme.BG_LIGHT
        ).pack(side="left")

        btn_add_zone = tk.Button(
            zones_header,
            text="+ 새 구역 추가",
            font=AppTheme.FONT_SMALL,
            bg=AppTheme.SURFACE,
            fg=AppTheme.PRIMARY,
            highlightbackground=AppTheme.PRIMARY,
            highlightthickness=1,
            bd=0,
            padx=10,
            pady=3,
            cursor="hand2",
            command=lambda: self.on_navigate("settings")
        )
        btn_add_zone.pack(side="right")

        # 구역 카드 리스트 컨테이너
        self.zones_container = tk.Frame(self.scrollable_frame, bg=AppTheme.BG_LIGHT)
        self.zones_container.pack(fill="x")

    def refresh(self) -> None:
        """화면 진입 시 데이터 최신화"""
        user = self.auth_service.get_current_user()
        if not user:
            return

        self.lbl_welcome.config(text=f"🌿 {user.user_id} 농가님의 스마트팜 관제 대시보드")

        # 기존 구역 카드들 제거
        for w in self.zones_container.winfo_children():
            w.destroy()

        zones = self.zone_service.get_user_zones(user.user_id)
        if not zones:
            empty_box = tk.Frame(
                self.zones_container,
                bg=AppTheme.SURFACE,
                highlightbackground=AppTheme.BORDER,
                highlightthickness=1,
                padx=20,
                pady=24
            )
            empty_box.pack(fill="x")
            tk.Label(
                empty_box,
                text="등록된 재배 구역이 없습니다. [설정] 메뉴에서 새 구역을 등록해 주세요.",
                font=AppTheme.FONT_BODY,
                fg=AppTheme.TEXT_MUTED,
                bg=AppTheme.SURFACE
            ).pack()
            return

        # 구역 카드 렌더링
        for zone in zones:
            latest_env = self.env_service.get_latest_record(zone.zone_id)
            self._render_zone_card(zone, latest_env)

    def _render_zone_card(self, zone: Zone, latest_env) -> None:
        card = tk.Frame(
            self.zones_container,
            bg=AppTheme.SURFACE,
            highlightbackground=AppTheme.BORDER,
            highlightthickness=1,
            padx=18,
            pady=16
        )
        card.pack(fill="x", pady=(0, 12))

        # 상단: 구역 이름 및 기본 제원
        top_f = tk.Frame(card, bg=AppTheme.SURFACE)
        top_f.pack(fill="x", pady=(0, 10))

        name_f = tk.Frame(top_f, bg=AppTheme.SURFACE)
        name_f.pack(side="left")

        tk.Label(
            name_f,
            text=zone.name,
            font=AppTheme.FONT_HEAD_MD,
            fg=AppTheme.TEXT_MAIN,
            bg=AppTheme.SURFACE
        ).pack(side="left")

        # 작물 뱃지
        tk.Label(
            name_f,
            text=f" {zone.crop_type} ",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.PRIMARY,
            bg="#D1FAE5",
            padx=6,
            pady=2
        ).pack(side="left", padx=(8, 0))

        # 우측: 면적 및 토양 정보
        info_f = tk.Frame(top_f, bg=AppTheme.SURFACE)
        info_f.pack(side="right")

        tk.Label(
            info_f,
            text=f"면적: {zone.area:.1f} m²  |  토양: {zone.soil_type}  |  최근 급수일: {zone.last_watering_date or '기록 없음'}",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.SURFACE
        ).pack()

        # 하단: 최신 환경 센서 측정값 표시 그리드
        env_grid = tk.Frame(card, bg=AppTheme.SURFACE_ALT, padx=12, pady=10)
        env_grid.pack(fill="x", pady=(0, 10))

        if latest_env:
            metrics = [
                ("토양 수분", f"{latest_env.soil_moisture:.1f}%", AppTheme.PRIMARY if latest_env.soil_moisture >= 25 else AppTheme.DANGER),
                ("현재 기온", f"{latest_env.temperature:.1f} ℃", AppTheme.TEXT_MAIN),
                ("공기 습도", f"{latest_env.humidity:.1f} %RH", AppTheme.TEXT_MAIN),
                ("현재 조도", f"{latest_env.illuminance:,.0f} lx", AppTheme.TEXT_MAIN),
            ]
            for i, (m_title, m_val, m_col) in enumerate(metrics):
                col_f = tk.Frame(env_grid, bg=AppTheme.SURFACE_ALT)
                col_f.pack(side="left", fill="x", expand=True)

                tk.Label(col_f, text=m_title, font=AppTheme.FONT_SMALL, fg=AppTheme.TEXT_MUTED, bg=AppTheme.SURFACE_ALT).pack(anchor="w")
                tk.Label(col_f, text=m_val, font=AppTheme.FONT_BODY_BOLD, fg=m_col, bg=AppTheme.SURFACE_ALT).pack(anchor="w")

            tk.Label(
                card,
                text=f"최근 측정: {latest_env.recorded_at}",
                font=AppTheme.FONT_SMALL,
                fg=AppTheme.TEXT_MUTED,
                bg=AppTheme.SURFACE
            ).pack(anchor="e")
        else:
            tk.Label(
                env_grid,
                text="아직 측정된 환경 센서 기록이 없습니다. [구역별 환경 입력]에서 첫 측정값을 등록해 주세요.",
                font=AppTheme.FONT_SMALL,
                fg=AppTheme.TEXT_MUTED,
                bg=AppTheme.SURFACE_ALT
            ).pack(anchor="w")
