"""
main.py
스마트팜 운영비 절감 프로그램 (객체지향프로그래밍 팀프로젝트 메인 실행 파일)
"""
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any

from ui.styles import AppTheme
from ui.components.nav_bar import TopNavBar
from ui.views.auth_view import AuthView
from ui.views.home_view import HomeView
from ui.views.env_input_view import EnvInputView
from ui.views.plan_view import PlanView
from ui.views.history_view import HistoryView
from ui.views.settings_view import SettingsView

from services.storage_service import StorageService
from services.auth_service import AuthService
from services.zone_service import ZoneService
from services.environment_service import EnvironmentService
from services.optimization_service import OptimizationService
from services.history_service import HistoryService


class SmartFarmApplication:
    """스마트팜 운영비 절감 프로그램 메인 컨트롤러 (OOP Singleton/Facade 패턴 적용)"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("스마트팜 운영비 절감 시스템 (SmartFarm Cost Optimizer)")
        self.root.geometry("1100x720")
        self.root.minsize(980, 640)
        self.root.configure(bg=AppTheme.BG_LIGHT)

        # 1. 서비스 계층 초기화
        self.storage = StorageService(data_dir="data")
        self.auth_service = AuthService(self.storage)
        self.zone_service = ZoneService(self.storage)
        self.env_service = EnvironmentService(self.storage)
        self.opt_service = OptimizationService(self.storage)
        self.history_service = HistoryService(self.storage, self.zone_service)

        # 2. UI 테마 적용
        AppTheme.apply_theme(self.root)

        # 3. 윈도우 종료 프로토콜 연결 (요구사항 38)
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

        # 4. 루트 UI 레이아웃 컨테이너
        self._build_main_frames()

        # 5. 첫 시작 화면 (회원가입/로그인 뷰) 표시
        self.show_auth_flow()

    def _build_main_frames(self) -> None:
        """글로벌 네비게이션 및 뷰 컨테이너 프레임 생성"""
        # 상단 네비게이션 바 (로그인 후 노출)
        self.nav_bar = TopNavBar(
            self.root,
            on_navigate=self.navigate_to,
            on_logout=self.on_logout,
            on_exit=self.on_exit
        )

        # 메인 뷰 교체 컨테이너
        self.view_container = tk.Frame(self.root, bg=AppTheme.BG_LIGHT)
        self.view_container.pack(fill="both", expand=True)

        # 뷰 인스턴스 딕셔너리
        self.views: Dict[str, Any] = {}

    def show_auth_flow(self) -> None:
        """인증 전 상태: 네비게이션 숨기고 AuthView 표시"""
        self.nav_bar.pack_forget()

        for w in self.view_container.winfo_children():
            w.pack_forget()

        if "auth" not in self.views:
            self.views["auth"] = AuthView(
                self.view_container,
                auth_service=self.auth_service,
                zone_service=self.zone_service,
                on_login_success=self.on_login_success
            )

        self.views["auth"].show_welcome()
        self.views["auth"].pack(fill="both", expand=True)

    def on_login_success(self) -> None:
        """로그인 성공 후 메인 대시보드로 전환 (요구사항 6, 8)"""
        user = self.auth_service.get_current_user()
        if not user:
            return

        # Auth 뷰 숨김
        if "auth" in self.views:
            self.views["auth"].pack_forget()

        # 상단 네비게이션 바 부착 및 사용자명 반영
        self.nav_bar.pack(side="top", fill="x", before=self.view_container)
        self.nav_bar.update_user_display(user.user_id)

        # 메인 뷰들 초기화
        self.views["home"] = HomeView(
            self.view_container,
            auth_service=self.auth_service,
            zone_service=self.zone_service,
            env_service=self.env_service,
            storage=self.storage,
            on_navigate=self.navigate_to
        )

        self.views["env_input"] = EnvInputView(
            self.view_container,
            auth_service=self.auth_service,
            zone_service=self.zone_service,
            env_service=self.env_service,
            on_navigate=self.navigate_to
        )

        self.views["plan"] = PlanView(
            self.view_container,
            auth_service=self.auth_service,
            zone_service=self.zone_service,
            env_service=self.env_service,
            opt_service=self.opt_service,
            storage=self.storage,
            on_navigate=self.navigate_to
        )

        self.views["history"] = HistoryView(
            self.view_container,
            auth_service=self.auth_service,
            zone_service=self.zone_service,
            history_service=self.history_service,
            storage=self.storage,
            on_navigate=self.navigate_to
        )

        self.views["settings"] = SettingsView(
            self.view_container,
            auth_service=self.auth_service,
            zone_service=self.zone_service,
            storage=self.storage,
            on_navigate=self.navigate_to
        )

        # Home 화면으로 진입
        self.navigate_to("home")

    def navigate_to(self, view_name: str) -> None:
        """화면 전환 라우터 (요구사항 8, 37)"""
        if view_name not in self.views:
            return

        for name, v in self.views.items():
            if name != "auth":
                v.pack_forget()

        target_view = self.views[view_name]
        target_view.pack(fill="both", expand=True)

        # 데이터 새로고침
        if hasattr(target_view, "refresh"):
            target_view.refresh()

        self.nav_bar.set_active(view_name)

    def on_logout(self) -> None:
        """로그아웃 처리 (요구사항 37)"""
        if messagebox.askyesno("로그아웃", "로그아웃하시고 첫 화면으로 돌아가시겠습니까?"):
            self.auth_service.logout()
            self.show_auth_flow()

    def on_exit(self) -> None:
        """프로그램 종료 (요구사항 38)"""
        if messagebox.askyesno(
            "프로그램 종료",
            "스마트팜 운영비 절감 프로그램을 종료하시겠습니까?\n저장하지 않은 입력 데이터가 있다면 확인 후 종료해 주세요."
        ):
            self.root.destroy()
            sys.exit(0)


def main():
    root = tk.Tk()
    app = SmartFarmApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()
