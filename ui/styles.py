"""
ui/styles.py
스마트팜 UI 디자인 테마, 색상 팔레트 및 ttk 스타일 정의
"""
import tkinter as tk
from tkinter import ttk


class AppTheme:
    """스마트팜 UI 색상 팔레트 및 공통 스타일 상수"""

    # 모던 스마트팜 그린 & 슬레이트 색상 팔레트
    PRIMARY = "#1E5128"         # 짙은 포레스트 그린 (신뢰감, 자연)
    PRIMARY_LIGHT = "#4E9F3D"   # 밝은 에메랄드 그린 (강조, 활성화)
    PRIMARY_HOVER = "#163E1F"
    SECONDARY = "#191A19"       # 딥 다크
    ACCENT = "#2ECC71"          # 생동감 있는 녹색

    # 배경 및 패널 색상
    BG_LIGHT = "#F4F6F9"        # 앱 기본 배경
    SURFACE = "#FFFFFF"         # 카드 및 컨테이너 배경
    SURFACE_ALT = "#F8FAFC"     # 연한 서브 배경
    BORDER = "#E2E8F0"          # 카드 테두리선
    BORDER_DARK = "#CBD5E1"

    # 텍스트 색상
    TEXT_MAIN = "#1E293B"       # 본문 텍스트 (다크 슬레이트)
    TEXT_MUTED = "#64748B"      # 보조 텍스트 (그레이)
    TEXT_LIGHT = "#94A3B8"
    TEXT_WHITE = "#FFFFFF"

    # 상태 및 피드백 색상
    SUCCESS = "#10B981"         # 적정 / 정상 (녹색)
    WARNING = "#F59E0B"         # 주의 / 조절 필요 (오렌지)
    DANGER = "#EF4444"          # 급수 필요 / 경고 (레드)
    INFO = "#3B82F6"            # 정보 (블루)

    # 폰트 구성 (시스템 기본 맑은 고딕 또는 샌세리프)
    FONT_FAMILY = "Malgun Gothic"
    FONT_HEAD_XL = ("Malgun Gothic", 18, "bold")
    FONT_HEAD_LG = ("Malgun Gothic", 15, "bold")
    FONT_HEAD_MD = ("Malgun Gothic", 12, "bold")
    FONT_BODY = ("Malgun Gothic", 10)
    FONT_BODY_BOLD = ("Malgun Gothic", 10, "bold")
    FONT_SMALL = ("Malgun Gothic", 9)
    FONT_STAT_VAL = ("Malgun Gothic", 20, "bold")

    @classmethod
    def apply_theme(cls, root: tk.Tk) -> None:
        """ttk 위젯 전역 스타일 적용"""
        style = ttk.Style(root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # 일반 프레임
        style.configure("TFrame", background=cls.BG_LIGHT)
        style.configure("Card.TFrame", background=cls.SURFACE, relief="flat")
        style.configure("Header.TFrame", background=cls.PRIMARY)

        # 일반 라벨
        style.configure("TLabel", background=cls.BG_LIGHT, foreground=cls.TEXT_MAIN, font=cls.FONT_BODY)
        style.configure("Card.TLabel", background=cls.SURFACE, foreground=cls.TEXT_MAIN, font=cls.FONT_BODY)
        style.configure("CardMuted.TLabel", background=cls.SURFACE, foreground=cls.TEXT_MUTED, font=cls.FONT_SMALL)
        style.configure("HeaderTitle.TLabel", background=cls.PRIMARY, foreground=cls.TEXT_WHITE, font=cls.FONT_HEAD_LG)
        style.configure("HeaderSub.TLabel", background=cls.PRIMARY, foreground="#D8F3DC", font=cls.FONT_SMALL)

        # 기본 버튼
        style.configure(
            "Primary.TButton",
            background=cls.PRIMARY,
            foreground=cls.TEXT_WHITE,
            font=cls.FONT_BODY_BOLD,
            padding=(12, 7),
            borderwidth=0
        )
        style.map("Primary.TButton",
            background=[("active", cls.PRIMARY_LIGHT), ("pressed", cls.PRIMARY_HOVER)],
            foreground=[("active", cls.TEXT_WHITE)]
        )

        style.configure(
            "Secondary.TButton",
            background="#E2E8F0",
            foreground=cls.TEXT_MAIN,
            font=cls.FONT_BODY,
            padding=(10, 6),
            borderwidth=0
        )
        style.map("Secondary.TButton",
            background=[("active", "#CBD5E1")],
            foreground=[("active", cls.TEXT_MAIN)]
        )

        style.configure(
            "Accent.TButton",
            background=cls.PRIMARY_LIGHT,
            foreground=cls.TEXT_WHITE,
            font=cls.FONT_BODY_BOLD,
            padding=(12, 7),
            borderwidth=0
        )
        style.map("Accent.TButton",
            background=[("active", cls.PRIMARY)]
        )

        style.configure(
            "Danger.TButton",
            background=cls.DANGER,
            foreground=cls.TEXT_WHITE,
            font=cls.FONT_BODY_BOLD,
            padding=(10, 5),
            borderwidth=0
        )
        style.map("Danger.TButton",
            background=[("active", "#DC2626")]
        )

        # Treeview (표)
        style.configure(
            "Treeview",
            background=cls.SURFACE,
            foreground=cls.TEXT_MAIN,
            rowheight=28,
            fieldbackground=cls.SURFACE,
            font=cls.FONT_BODY,
            borderwidth=1,
            relief="solid"
        )
        style.configure(
            "Treeview.Heading",
            background="#E2E8F0",
            foreground=cls.TEXT_MAIN,
            font=cls.FONT_BODY_BOLD,
            padding=(5, 6)
        )
        style.map("Treeview",
            background=[("selected", "#D8F3DC")],
            foreground=[("selected", cls.PRIMARY)]
        )

        # Entry 및 Combobox
        style.configure("TEntry", fieldbackground=cls.SURFACE, foreground=cls.TEXT_MAIN, padding=5)
        style.configure("TCombobox", fieldbackground=cls.SURFACE, foreground=cls.TEXT_MAIN, padding=5)
