"""
ui/views/auth_view.py
회원가입, 로그인 및 최초 구역 등록 뷰 (요구사항 A: 1~7)
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

from ui.styles import AppTheme
from services.auth_service import AuthService
from services.zone_service import ZoneService


class AuthView(tk.Frame):
    """
    프로그램 시작, 회원가입 및 로그인 화면
    - 1: 시작 화면 (회원가입/로그인 선택 문구 및 버튼)
    - 2: 회원가입 폼 (아이디, 비밀번호, 비밀번호 확인)
    - 3: 유효성 검사 및 에러 안내
    - 4: 가입 완료 안내 및 로그인 화면 전환
    - 5: 로그인 폼
    - 6: 로그인 인증 처리 및 세션 로드
    - 7: 최초 사용자 구역 등록 처리
    """

    def __init__(
        self,
        parent,
        auth_service: AuthService,
        zone_service: ZoneService,
        on_login_success: Callable[[], None],
        **kwargs
    ):
        super().__init__(parent, bg=AppTheme.BG_LIGHT, **kwargs)
        self.auth_service = auth_service
        self.zone_service = zone_service
        self.on_login_success = on_login_success

        self._build_ui()
        self.show_welcome()

    def _build_ui(self) -> None:
        """중앙 정렬 카드 레이아웃 생성"""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 메인 카드 컨테이너
        self.card = tk.Frame(
            self,
            bg=AppTheme.SURFACE,
            highlightbackground=AppTheme.BORDER,
            highlightthickness=1,
            padx=40,
            pady=36,
            width=460
        )
        self.card.grid(row=0, column=0)
        self.card.grid_propagate(False)

        # 상단 공통 로고 및 프로그램 타이틀
        self.logo_label = tk.Label(
            self.card,
            text="🌿 SmartFarm Manager",
            font=AppTheme.FONT_HEAD_XL,
            fg=AppTheme.PRIMARY,
            bg=AppTheme.SURFACE
        )
        self.logo_label.pack(pady=(0, 6))

        self.sub_label = tk.Label(
            self.card,
            text="스마트팜 온실 환경 분석 및 저비용 운영비 절감 시스템",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.SURFACE
        )
        self.sub_label.pack(pady=(0, 24))

        # 가변 콘텐츠 영역
        self.content_frame = tk.Frame(self.card, bg=AppTheme.SURFACE)
        self.content_frame.pack(fill="both", expand=True)

    def _clear_content(self) -> None:
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # ==========================================
    # 1. 시작 화면 (요구사항 1)
    # ==========================================
    def show_welcome(self) -> None:
        self._clear_content()

        prompt_box = tk.Frame(
            self.content_frame,
            bg=AppTheme.SURFACE_ALT,
            highlightbackground=AppTheme.BORDER,
            highlightthickness=1,
            padx=20,
            pady=20
        )
        prompt_box.pack(fill="x", pady=(10, 24))

        lbl_prompt = tk.Label(
            prompt_box,
            text="“회원가입을 하시겠습니까, 로그인하시겠습니까?”",
            font=AppTheme.FONT_HEAD_MD,
            fg=AppTheme.TEXT_MAIN,
            bg=AppTheme.SURFACE_ALT,
            wraplength=340,
            justify="center"
        )
        lbl_prompt.pack()

        lbl_desc = tk.Label(
            prompt_box,
            text="기존 계정이 있으시면 로그인을, 처음 방문하셨다면 회원가입을 선택해 주세요.",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.SURFACE_ALT,
            wraplength=340,
            justify="center"
        )
        lbl_desc.pack(pady=(8, 0))

        # 버튼 영역
        btn_frame = tk.Frame(self.content_frame, bg=AppTheme.SURFACE)
        btn_frame.pack(fill="x", pady=6)

        btn_login = tk.Button(
            btn_frame,
            text="로그인",
            font=AppTheme.FONT_HEAD_MD,
            bg=AppTheme.PRIMARY,
            fg=AppTheme.TEXT_WHITE,
            activebackground=AppTheme.PRIMARY_LIGHT,
            activeforeground=AppTheme.TEXT_WHITE,
            bd=0,
            pady=12,
            cursor="hand2",
            command=self.show_login
        )
        btn_login.pack(fill="x", pady=(0, 10))

        btn_register = tk.Button(
            btn_frame,
            text="회원가입",
            font=AppTheme.FONT_BODY_BOLD,
            bg="#E2E8F0",
            fg=AppTheme.TEXT_MAIN,
            activebackground="#CBD5E1",
            activeforeground=AppTheme.TEXT_MAIN,
            bd=0,
            pady=10,
            cursor="hand2",
            command=self.show_register
        )
        btn_register.pack(fill="x")

        # 데모 빠른 체험 버튼
        btn_demo = tk.Button(
            self.content_frame,
            text="⚡ 체험용 데모 계정으로 바로 시작 (farmer / 123)",
            font=AppTheme.FONT_SMALL,
            bg=AppTheme.SURFACE,
            fg=AppTheme.PRIMARY_LIGHT,
            activebackground=AppTheme.SURFACE,
            activeforeground=AppTheme.PRIMARY,
            bd=0,
            cursor="hand2",
            command=self._quick_demo_login
        )
        btn_demo.pack(pady=(20, 0))

    # ==========================================
    # 2. 로그인 화면 (요구사항 5, 6)
    # ==========================================
    def show_login(self) -> None:
        self._clear_content()

        lbl_title = tk.Label(
            self.content_frame,
            text="로그인",
            font=AppTheme.FONT_HEAD_MD,
            fg=AppTheme.PRIMARY,
            bg=AppTheme.SURFACE
        )
        lbl_title.pack(anchor="w", pady=(0, 14))

        # 아이디 입력
        lbl_id = tk.Label(
            self.content_frame,
            text="아이디",
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.TEXT_MAIN,
            bg=AppTheme.SURFACE
        )
        lbl_id.pack(anchor="w", pady=(4, 2))

        self.entry_login_id = ttk.Entry(self.content_frame, font=AppTheme.FONT_BODY)
        self.entry_login_id.pack(fill="x", pady=(0, 10))
        self.entry_login_id.focus()

        # 비밀번호 입력
        lbl_pw = tk.Label(
            self.content_frame,
            text="비밀번호",
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.TEXT_MAIN,
            bg=AppTheme.SURFACE
        )
        lbl_pw.pack(anchor="w", pady=(4, 2))

        self.entry_login_pw = ttk.Entry(self.content_frame, font=AppTheme.FONT_BODY, show="●")
        self.entry_login_pw.pack(fill="x", pady=(0, 8))
        self.entry_login_pw.bind("<Return>", lambda e: self._handle_login())

        # 에러 메시지 라벨
        self.lbl_login_msg = tk.Label(
            self.content_frame,
            text="",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.DANGER,
            bg=AppTheme.SURFACE
        )
        self.lbl_login_msg.pack(anchor="w", pady=(0, 10))

        # 로그인 버튼
        btn_submit = tk.Button(
            self.content_frame,
            text="로그인하기",
            font=AppTheme.FONT_BODY_BOLD,
            bg=AppTheme.PRIMARY,
            fg=AppTheme.TEXT_WHITE,
            activebackground=AppTheme.PRIMARY_LIGHT,
            activeforeground=AppTheme.TEXT_WHITE,
            bd=0,
            pady=10,
            cursor="hand2",
            command=self._handle_login
        )
        btn_submit.pack(fill="x", pady=(0, 10))

        # 하단 네비게이션 링크
        nav_box = tk.Frame(self.content_frame, bg=AppTheme.SURFACE)
        nav_box.pack(fill="x")

        btn_back = tk.Button(
            nav_box,
            text="← 첫 화면으로",
            font=AppTheme.FONT_SMALL,
            bg=AppTheme.SURFACE,
            fg=AppTheme.TEXT_MUTED,
            bd=0,
            cursor="hand2",
            command=self.show_welcome
        )
        btn_back.pack(side="left")

        btn_to_reg = tk.Button(
            nav_box,
            text="회원가입 이동 →",
            font=AppTheme.FONT_SMALL,
            bg=AppTheme.SURFACE,
            fg=AppTheme.PRIMARY_LIGHT,
            bd=0,
            cursor="hand2",
            command=self.show_register
        )
        btn_to_reg.pack(side="right")

    def _handle_login(self) -> None:
        user_id = self.entry_login_id.get().strip()
        pw = self.entry_login_pw.get().strip()

        success, msg = self.auth_service.login(user_id, pw)
        if not success:
            self.lbl_login_msg.config(text=msg)
            return

        # 로그인 성공 (요구사항 6, 7)
        self._check_first_time_zone_setup(user_id)

    def _quick_demo_login(self) -> None:
        """데모 계정으로 즉시 로그인"""
        self.auth_service.login("farmer", "123")
        self.on_login_success()

    # ==========================================
    # 3. 회원가입 화면 (요구사항 2, 3, 4)
    # ==========================================
    def show_register(self) -> None:
        self._clear_content()

        lbl_title = tk.Label(
            self.content_frame,
            text="새 계정 회원가입",
            font=AppTheme.FONT_HEAD_MD,
            fg=AppTheme.PRIMARY,
            bg=AppTheme.SURFACE
        )
        lbl_title.pack(anchor="w", pady=(0, 14))

        # 아이디
        lbl_id = tk.Label(
            self.content_frame,
            text="아이디",
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.TEXT_MAIN,
            bg=AppTheme.SURFACE
        )
        lbl_id.pack(anchor="w", pady=(2, 2))

        self.entry_reg_id = ttk.Entry(self.content_frame, font=AppTheme.FONT_BODY)
        self.entry_reg_id.pack(fill="x", pady=(0, 8))
        self.entry_reg_id.focus()

        # 비밀번호
        lbl_pw = tk.Label(
            self.content_frame,
            text="비밀번호",
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.TEXT_MAIN,
            bg=AppTheme.SURFACE
        )
        lbl_pw.pack(anchor="w", pady=(2, 2))

        self.entry_reg_pw = ttk.Entry(self.content_frame, font=AppTheme.FONT_BODY, show="●")
        self.entry_reg_pw.pack(fill="x", pady=(0, 8))

        # 비밀번호 확인
        lbl_pwc = tk.Label(
            self.content_frame,
            text="비밀번호 확인",
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.TEXT_MAIN,
            bg=AppTheme.SURFACE
        )
        lbl_pwc.pack(anchor="w", pady=(2, 2))

        self.entry_reg_pwc = ttk.Entry(self.content_frame, font=AppTheme.FONT_BODY, show="●")
        self.entry_reg_pwc.pack(fill="x", pady=(0, 8))
        self.entry_reg_pwc.bind("<Return>", lambda e: self._handle_register())

        # 에러 메시지 라벨 (요구사항 3)
        self.lbl_reg_msg = tk.Label(
            self.content_frame,
            text="",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.DANGER,
            bg=AppTheme.SURFACE,
            wraplength=360,
            justify="left"
        )
        self.lbl_reg_msg.pack(anchor="w", pady=(0, 10))

        # 가입 완료 버튼
        btn_submit = tk.Button(
            self.content_frame,
            text="가입 완료 및 계정 생성",
            font=AppTheme.FONT_BODY_BOLD,
            bg=AppTheme.PRIMARY,
            fg=AppTheme.TEXT_WHITE,
            activebackground=AppTheme.PRIMARY_LIGHT,
            activeforeground=AppTheme.TEXT_WHITE,
            bd=0,
            pady=10,
            cursor="hand2",
            command=self._handle_register
        )
        btn_submit.pack(fill="x", pady=(0, 10))

        # 하단 돌아가기 링크
        btn_back = tk.Button(
            self.content_frame,
            text="← 시작 화면으로 돌아가기",
            font=AppTheme.FONT_SMALL,
            bg=AppTheme.SURFACE,
            fg=AppTheme.TEXT_MUTED,
            bd=0,
            cursor="hand2",
            command=self.show_welcome
        )
        btn_back.pack(anchor="w")

    def _handle_register(self) -> None:
        uid = self.entry_reg_id.get().strip()
        pw = self.entry_reg_pw.get().strip()
        pwc = self.entry_reg_pwc.get().strip()

        success, msg = self.auth_service.register(uid, pw, pwc)
        if not success:
            self.lbl_reg_msg.config(text=msg)
            return

        # 요구사항 4: "회원가입이 완료되었습니다. 로그인해 주세요." 안내 후 로그인 화면 이동
        messagebox.showinfo("회원가입 완료", "회원가입이 완료되었습니다. 로그인해 주세요.")
        self.show_login()
        self.entry_login_id.insert(0, uid)
        self.entry_login_pw.focus()

    # ==========================================
    # 4. 최초 사용자 재배 구역 등록 (요구사항 7)
    # ==========================================
    def _check_first_time_zone_setup(self, user_id: str) -> None:
        """
        등록된 재배 구역이 없는 사용자는 처음 한 번
        구역 이름, 작물 종류, 재배면적, 토양 종류를 등록한다.
        """
        if self.zone_service.has_user_zones(user_id):
            self.on_login_success()
            return

        # 최초 사용자 구역 등록 다이얼로그 띄우기
        self._show_initial_zone_modal(user_id)

    def _show_initial_zone_modal(self, user_id: str) -> None:
        modal = tk.Toplevel(self)
        modal.title("최초 재배 구역 등록")
        modal.geometry("440x480")
        modal.resizable(False, False)
        modal.configure(bg=AppTheme.SURFACE)
        modal.transient(self)
        modal.grab_set()

        pad_f = tk.Frame(modal, bg=AppTheme.SURFACE, padx=24, pady=20)
        pad_f.pack(fill="both", expand=True)

        tk.Label(
            pad_f,
            text="🌱 스마트팜 첫 재배 구역 등록",
            font=AppTheme.FONT_HEAD_MD,
            fg=AppTheme.PRIMARY,
            bg=AppTheme.SURFACE
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            pad_f,
            text="처음 이용하시는 농가입니다. 관리하실 첫 번째 재배 구역 정보를 등록해 주세요.",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.SURFACE,
            wraplength=390,
            justify="left"
        ).pack(anchor="w", pady=(0, 16))

        # 구역 이름
        tk.Label(pad_f, text="구역 이름 (예: A구역, 제1온실)", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).pack(anchor="w")
        ent_name = ttk.Entry(pad_f, font=AppTheme.FONT_BODY)
        ent_name.pack(fill="x", pady=(2, 10))
        ent_name.insert(0, "A구역 (스마트 온실 1)")

        # 작물 종류
        tk.Label(pad_f, text="작물 종류", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).pack(anchor="w")
        cb_crop = ttk.Combobox(pad_f, values=["토마토", "상추", "딸기", "파프리카"], state="readonly", font=AppTheme.FONT_BODY)
        cb_crop.pack(fill="x", pady=(2, 10))
        cb_crop.set("토마토")

        # 재배면적 (m²)
        tk.Label(pad_f, text="재배면적 (m²)", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).pack(anchor="w")
        ent_area = ttk.Entry(pad_f, font=AppTheme.FONT_BODY)
        ent_area.pack(fill="x", pady=(2, 10))
        ent_area.insert(0, "100.0")

        # 토양 종류
        tk.Label(pad_f, text="토양 종류", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).pack(anchor="w")
        cb_soil = ttk.Combobox(pad_f, values=["사양토", "양토", "점질토", "코코피트", "암면 배지"], font=AppTheme.FONT_BODY)
        cb_soil.pack(fill="x", pady=(2, 16))
        cb_soil.set("사양토")

        lbl_modal_msg = tk.Label(pad_f, text="", font=AppTheme.FONT_SMALL, fg=AppTheme.DANGER, bg=AppTheme.SURFACE)
        lbl_modal_msg.pack(anchor="w", pady=(0, 8))

        def _save_initial_zone():
            name = ent_name.get().strip()
            crop = cb_crop.get().strip()
            soil = cb_soil.get().strip()
            try:
                area = float(ent_area.get().strip())
            except ValueError:
                lbl_modal_msg.config(text="재배면적은 유효한 숫자여야 합니다.")
                return

            success, msg, zone = self.zone_service.add_zone(
                user_id=user_id,
                name=name,
                crop_type=crop,
                area=area,
                soil_type=soil
            )
            if not success:
                lbl_modal_msg.config(text=msg)
                return

            messagebox.showinfo("등록 완료", f"'{name}' 구역이 등록되었습니다.\n대시보드로 이동합니다.")
            modal.destroy()
            self.on_login_success()

        btn_save = tk.Button(
            pad_f,
            text="구역 등록 완료 및 시작하기",
            font=AppTheme.FONT_BODY_BOLD,
            bg=AppTheme.PRIMARY,
            fg=AppTheme.TEXT_WHITE,
            bd=0,
            pady=10,
            cursor="hand2",
            command=_save_initial_zone
        )
        btn_save.pack(fill="x")
