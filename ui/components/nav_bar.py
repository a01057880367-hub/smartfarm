"""
ui/components/nav_bar.py
상단 글로벌 헤더 및 메뉴 네비게이션 바 컴포넌트
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from ui.styles import AppTheme


class TopNavBar(tk.Frame):
    """상단 글로벌 네비게이션 바 (요구사항 8, 37, 38)"""

    def __init__(
        self,
        parent,
        on_navigate: Callable[[str], None],
        on_logout: Callable[[], None],
        on_exit: Callable[[], None],
        **kwargs
    ):
        super().__init__(parent, bg=AppTheme.PRIMARY, padx=16, pady=10, **kwargs)
        self.on_navigate = on_navigate
        self.on_logout = on_logout
        self.on_exit = on_exit

        self.current_user_name = "사용자"

        # 좌측: 로고 및 타이틀
        left_frame = tk.Frame(self, bg=AppTheme.PRIMARY)
        left_frame.pack(side="left")

        # 로고 아이콘 라벨
        lbl_logo = tk.Label(
            left_frame,
            text="🌿",
            font=("Malgun Gothic", 16),
            bg=AppTheme.PRIMARY,
            fg="#A7F3D0"
        )
        lbl_logo.pack(side="left", padx=(0, 6))

        title_frame = tk.Frame(left_frame, bg=AppTheme.PRIMARY)
        title_frame.pack(side="left")

        lbl_title = tk.Label(
            title_frame,
            text="SmartFarm Manager",
            font=AppTheme.FONT_HEAD_MD,
            fg=AppTheme.TEXT_WHITE,
            bg=AppTheme.PRIMARY
        )
        lbl_title.pack(anchor="w")

        lbl_sub = tk.Label(
            title_frame,
            text="스마트팜 저비용 운영비 절감 시스템",
            font=AppTheme.FONT_SMALL,
            fg="#A7F3D0",
            bg=AppTheme.PRIMARY
        )
        lbl_sub.pack(anchor="w")

        # 우측: 시스템 액션 (사용자 정보, 설정, 로그아웃, 종료)
        right_frame = tk.Frame(self, bg=AppTheme.PRIMARY)
        right_frame.pack(side="right")

        self.lbl_user = tk.Label(
            right_frame,
            text="👤 사용자님",
            font=AppTheme.FONT_SMALL,
            fg="#E2E8F0",
            bg=AppTheme.PRIMARY
        )
        self.lbl_user.pack(side="left", padx=(0, 10))

        btn_settings = tk.Button(
            right_frame,
            text="⚙ 설정",
            font=AppTheme.FONT_SMALL,
            bg="#2E6F40",
            fg=AppTheme.TEXT_WHITE,
            activebackground=AppTheme.PRIMARY_LIGHT,
            activeforeground=AppTheme.TEXT_WHITE,
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=lambda: self.on_navigate("settings")
        )
        btn_settings.pack(side="left", padx=3)

        btn_logout = tk.Button(
            right_frame,
            text="로그아웃",
            font=AppTheme.FONT_SMALL,
            bg="#3F4E4F",
            fg=AppTheme.TEXT_WHITE,
            activebackground="#2C3639",
            activeforeground=AppTheme.TEXT_WHITE,
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.on_logout
        )
        btn_logout.pack(side="left", padx=3)

        btn_exit = tk.Button(
            right_frame,
            text="종료",
            font=AppTheme.FONT_SMALL,
            bg="#B91C1C",
            fg=AppTheme.TEXT_WHITE,
            activebackground="#991B1B",
            activeforeground=AppTheme.TEXT_WHITE,
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.on_exit
        )
        btn_exit.pack(side="left", padx=(3, 0))

        # 중앙: 메인 메뉴 탭 버튼들
        center_frame = tk.Frame(self, bg=AppTheme.PRIMARY)
        center_frame.pack(side="left", padx=(30, 0))

        self.nav_buttons = {}
        menus = [
            ("home", "🏠 홈"),
            ("env_input", "📊 구역별 환경 입력"),
            ("plan", "💡 저비용 운영 계획"),
            ("history", "📋 사용량·비용 이력"),
        ]

        for code, label in menus:
            btn = tk.Button(
                center_frame,
                text=label,
                font=AppTheme.FONT_BODY_BOLD,
                bg=AppTheme.PRIMARY,
                fg="#D1FAE5",
                activebackground=AppTheme.PRIMARY_LIGHT,
                activeforeground=AppTheme.TEXT_WHITE,
                bd=0,
                padx=12,
                pady=6,
                cursor="hand2",
                command=lambda c=code: self._handle_click(c)
            )
            btn.pack(side="left", padx=2)
            self.nav_buttons[code] = btn

    def _handle_click(self, code: str) -> None:
        self.set_active(code)
        self.on_navigate(code)

    def set_active(self, active_code: str) -> None:
        """현재 활성화된 메뉴 탭 하이라이트"""
        for code, btn in self.nav_buttons.items():
            if code == active_code:
                btn.config(bg=AppTheme.PRIMARY_LIGHT, fg=AppTheme.TEXT_WHITE)
            else:
                btn.config(bg=AppTheme.PRIMARY, fg="#D1FAE5")

    def update_user_display(self, user_id: str) -> None:
        self.lbl_user.config(text=f"👤 {user_id} 농가님")
