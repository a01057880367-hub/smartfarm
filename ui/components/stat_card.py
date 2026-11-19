"""
ui/components/stat_card.py
지표 요약 통계 카드 컴포넌트
"""
import tkinter as tk
from tkinter import ttk
from ui.styles import AppTheme


class StatCard(tk.Frame):
    """지표 및 상태 요약 카드 위젯"""

    def __init__(
        self,
        parent,
        title: str,
        value: str,
        unit: str = "",
        status_text: str = "",
        status_color: str = AppTheme.SUCCESS,
        subtext: str = "",
        width: int = 180,
        **kwargs
    ):
        super().__init__(
            parent,
            bg=AppTheme.SURFACE,
            highlightbackground=AppTheme.BORDER,
            highlightthickness=1,
            padx=14,
            pady=12,
            **kwargs
        )
        self.status_color = status_color

        # 상단 타이틀
        self.lbl_title = tk.Label(
            self,
            text=title,
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.SURFACE
        )
        self.lbl_title.pack(anchor="w")

        # 중앙 값 및 단위
        val_frame = tk.Frame(self, bg=AppTheme.SURFACE)
        val_frame.pack(anchor="w", pady=(4, 2))

        self.lbl_value = tk.Label(
            val_frame,
            text=value,
            font=AppTheme.FONT_STAT_VAL,
            fg=AppTheme.TEXT_MAIN,
            bg=AppTheme.SURFACE
        )
        self.lbl_value.pack(side="left")

        if unit:
            self.lbl_unit = tk.Label(
                val_frame,
                text=f" {unit}",
                font=AppTheme.FONT_BODY,
                fg=AppTheme.TEXT_MUTED,
                bg=AppTheme.SURFACE
            )
            self.lbl_unit.pack(side="left", pady=(5, 0))

        # 하단 뱃지 또는 보조 텍스트
        bot_frame = tk.Frame(self, bg=AppTheme.SURFACE)
        bot_frame.pack(anchor="w", fill="x", pady=(4, 0))

        if status_text:
            self.lbl_badge = tk.Label(
                bot_frame,
                text=f" ● {status_text} ",
                font=AppTheme.FONT_SMALL,
                fg=status_color,
                bg="#F1F5F9",
                padx=4,
                pady=1
            )
            self.lbl_badge.pack(side="left")

        if subtext:
            self.lbl_sub = tk.Label(
                bot_frame,
                text=subtext,
                font=AppTheme.FONT_SMALL,
                fg=AppTheme.TEXT_MUTED,
                bg=AppTheme.SURFACE
            )
            self.lbl_sub.pack(side="left", padx=(6, 0))

    def update_data(self, value: str, status_text: str = "", status_color: str = "", subtext: str = ""):
        """카드 데이터 동적 갱신"""
        self.lbl_value.config(text=value)
        if hasattr(self, "lbl_badge") and status_text:
            color = status_color if status_color else self.status_color
            self.lbl_badge.config(text=f" ● {status_text} ", fg=color)
        if hasattr(self, "lbl_sub") and subtext:
            self.lbl_sub.config(text=subtext)
