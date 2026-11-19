"""
ui/views/settings_view.py
구역 관리, 작물 관리 기준, 장비 소비전력 및 유틸리티 단가 설정 뷰 (요구사항 E: 36)
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, List

from ui.styles import AppTheme
from models.zone import Zone
from models.settings import SystemSettings
from models.crop_standard import CropStandard
from services.auth_service import AuthService
from services.zone_service import ZoneService
from services.storage_service import StorageService


class SettingsView(tk.Frame):
    """
    설정 화면 (요구사항 36)
    - 탭 1: 구역 관리 (수정, 추가, 삭제)
    - 탭 2: 물·전기 단가 및 장비 소비전력 관리
    - 탭 3: 작물별 생육 환경 기준 관리 (토마토, 상추 등)
    """

    def __init__(
        self,
        parent,
        auth_service: AuthService,
        zone_service: ZoneService,
        storage: StorageService,
        on_navigate: Callable[[str], None],
        **kwargs
    ):
        super().__init__(parent, bg=AppTheme.BG_LIGHT, **kwargs)
        self.auth_service = auth_service
        self.zone_service = zone_service
        self.storage = storage
        self.on_navigate = on_navigate

        self.user_zones: List[Zone] = []

        self._build_ui()

    def _build_ui(self) -> None:
        self.pack_propagate(False)

        # 상단 타이틀 바
        header = tk.Frame(self, bg=AppTheme.BG_LIGHT, padx=24, pady=16)
        header.pack(fill="x")

        tk.Label(
            header,
            text="⚙ 시스템 및 재배 환경 설정",
            font=AppTheme.FONT_HEAD_LG,
            fg=AppTheme.PRIMARY,
            bg=AppTheme.BG_LIGHT
        ).pack(anchor="w")

        tk.Label(
            header,
            text="재배 구역 제원, 물·전기 유틸리티 단가, 작물별 적정 생육 기준을 관리합니다.",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.BG_LIGHT
        ).pack(anchor="w", pady=(2, 0))

        # 메인 노트북 (탭)
        style = ttk.Style()
        style.configure("Settings.TNotebook", background=AppTheme.BG_LIGHT)
        style.configure("Settings.TNotebook.Tab", font=AppTheme.FONT_BODY_BOLD, padding=(14, 8))

        self.notebook = ttk.Notebook(self, style="Settings.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        # 탭 1: 구역 관리
        tab_zone = tk.Frame(self.notebook, bg=AppTheme.SURFACE, padx=20, pady=16)
        self.notebook.add(tab_zone, text=" 🌱 재배 구역 관리 ")
        self._build_zone_tab(tab_zone)

        # 탭 2: 단가 및 장비
        tab_unit = tk.Frame(self.notebook, bg=AppTheme.SURFACE, padx=20, pady=16)
        self.notebook.add(tab_unit, text=" ⚡ 단가 및 장비 소비전력 ")
        self._build_unit_tab(tab_unit)

        # 탭 3: 작물 기준
        tab_crop = tk.Frame(self.notebook, bg=AppTheme.SURFACE, padx=20, pady=16)
        self.notebook.add(tab_crop, text=" 🌾 작물별 생육 기준 ")
        self._build_crop_tab(tab_crop)

    # ==========================================
    # 탭 1: 재배 구역 관리
    # ==========================================
    def _build_zone_tab(self, parent: tk.Frame) -> None:
        parent.columnconfigure(0, weight=6)
        parent.columnconfigure(1, weight=4)
        parent.rowconfigure(0, weight=1)

        # 좌측: 구역 목록 Treeview
        left_f = tk.Frame(parent, bg=AppTheme.SURFACE)
        left_f.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        tk.Label(left_f, text="등록된 재배 구역 목록", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).pack(anchor="w", pady=(0, 6))

        cols = ("name", "crop", "area", "soil", "last_water")
        self.tree_zones = ttk.Treeview(left_f, columns=cols, show="headings", height=8)
        self.tree_zones.heading("name", text="구역 이름")
        self.tree_zones.heading("crop", text="작물 종류")
        self.tree_zones.heading("area", text="면적 (m²)")
        self.tree_zones.heading("soil", text="토양 종류")
        self.tree_zones.heading("last_water", text="최근 급수일")

        self.tree_zones.column("name", width=140, anchor="w")
        self.tree_zones.column("crop", width=80, anchor="center")
        self.tree_zones.column("area", width=80, anchor="e")
        self.tree_zones.column("soil", width=90, anchor="center")
        self.tree_zones.column("last_water", width=100, anchor="center")

        self.tree_zones.pack(fill="both", expand=True)
        self.tree_zones.bind("<<TreeviewSelect>>", self._on_zone_tree_select)

        # 우측: 구역 추가 / 수정 폼
        right_f = tk.Frame(parent, bg=AppTheme.SURFACE_ALT, padx=16, pady=14)
        right_f.grid(row=0, column=1, sticky="nsew")

        tk.Label(right_f, text="구역 상세 정보 추가 / 수정", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE_ALT).pack(anchor="w", pady=(0, 8))

        tk.Label(right_f, text="구역 이름", font=AppTheme.FONT_SMALL, bg=AppTheme.SURFACE_ALT).pack(anchor="w")
        self.ent_z_name = ttk.Entry(right_f, font=AppTheme.FONT_BODY)
        self.ent_z_name.pack(fill="x", pady=(2, 6))

        tk.Label(right_f, text="작물 종류", font=AppTheme.FONT_SMALL, bg=AppTheme.SURFACE_ALT).pack(anchor="w")
        self.cb_z_crop = ttk.Combobox(right_f, values=["토마토", "상추", "딸기", "파프리카"], font=AppTheme.FONT_BODY)
        self.cb_z_crop.pack(fill="x", pady=(2, 6))

        tk.Label(right_f, text="재배면적 (m²)", font=AppTheme.FONT_SMALL, bg=AppTheme.SURFACE_ALT).pack(anchor="w")
        self.ent_z_area = ttk.Entry(right_f, font=AppTheme.FONT_BODY)
        self.ent_z_area.pack(fill="x", pady=(2, 6))

        tk.Label(right_f, text="토양 종류", font=AppTheme.FONT_SMALL, bg=AppTheme.SURFACE_ALT).pack(anchor="w")
        self.ent_z_soil = ttk.Entry(right_f, font=AppTheme.FONT_BODY)
        self.ent_z_soil.pack(fill="x", pady=(2, 6))

        tk.Label(right_f, text="최근 급수일 (선택, YYYY-MM-DD)", font=AppTheme.FONT_SMALL, bg=AppTheme.SURFACE_ALT).pack(anchor="w")
        self.ent_z_water = ttk.Entry(right_f, font=AppTheme.FONT_BODY)
        self.ent_z_water.pack(fill="x", pady=(2, 12))

        # 액션 버튼
        btn_box = tk.Frame(right_f, bg=AppTheme.SURFACE_ALT)
        btn_box.pack(fill="x")

        btn_add = tk.Button(
            btn_box,
            text="+ 새 구역 추가",
            font=AppTheme.FONT_SMALL,
            bg=AppTheme.PRIMARY,
            fg=AppTheme.TEXT_WHITE,
            bd=0,
            pady=6,
            cursor="hand2",
            command=self._handle_add_zone
        )
        btn_add.pack(side="left", fill="x", expand=True, padx=(0, 4))

        btn_mod = tk.Button(
            btn_box,
            text="수정 저장",
            font=AppTheme.FONT_SMALL,
            bg="#2563EB",
            fg=AppTheme.TEXT_WHITE,
            bd=0,
            pady=6,
            cursor="hand2",
            command=self._handle_update_zone
        )
        btn_mod.pack(side="left", fill="x", expand=True, padx=(4, 4))

        btn_del = tk.Button(
            btn_box,
            text="삭제",
            font=AppTheme.FONT_SMALL,
            bg=AppTheme.DANGER,
            fg=AppTheme.TEXT_WHITE,
            bd=0,
            pady=6,
            cursor="hand2",
            command=self._handle_delete_zone
        )
        btn_del.pack(side="left", fill="x", expand=True, padx=(4, 0))

    def _on_zone_tree_select(self, event=None) -> None:
        sel = self.tree_zones.selection()
        if not sel:
            return
        idx = self.tree_zones.index(sel[0])
        if idx < 0 or idx >= len(self.user_zones):
            return

        z = self.user_zones[idx]
        self.ent_z_name.delete(0, tk.END)
        self.ent_z_name.insert(0, z.name)

        self.cb_z_crop.set(z.crop_type)

        self.ent_z_area.delete(0, tk.END)
        self.ent_z_area.insert(0, str(z.area))

        self.ent_z_soil.delete(0, tk.END)
        self.ent_z_soil.insert(0, z.soil_type)

        self.ent_z_water.delete(0, tk.END)
        if z.last_watering_date:
            self.ent_z_water.insert(0, z.last_watering_date)

    def _handle_add_zone(self) -> None:
        user = self.auth_service.get_current_user()
        if not user:
            return

        name = self.ent_z_name.get().strip()
        crop = self.cb_z_crop.get().strip()
        soil = self.ent_z_soil.get().strip()
        water = self.ent_z_water.get().strip() or None

        try:
            area = float(self.ent_z_area.get().strip())
        except ValueError:
            messagebox.showwarning("입력 오류", "재배면적은 올바른 숫자여야 합니다.")
            return

        success, msg, _ = self.zone_service.add_zone(
            user_id=user.user_id,
            name=name,
            crop_type=crop,
            area=area,
            soil_type=soil,
            last_watering_date=water
        )
        if not success:
            messagebox.showwarning("실패", msg)
            return

        messagebox.showinfo("완료", msg)
        self.refresh()

    def _handle_update_zone(self) -> None:
        sel = self.tree_zones.selection()
        if not sel:
            messagebox.showwarning("알림", "목록에서 수정할 구역을 선택해 주세요.")
            return

        idx = self.tree_zones.index(sel[0])
        z = self.user_zones[idx]

        name = self.ent_z_name.get().strip()
        crop = self.cb_z_crop.get().strip()
        soil = self.ent_z_soil.get().strip()
        water = self.ent_z_water.get().strip() or None

        try:
            area = float(self.ent_z_area.get().strip())
        except ValueError:
            messagebox.showwarning("입력 오류", "재배면적은 올바른 숫자여야 합니다.")
            return

        success, msg = self.zone_service.update_zone(
            zone_id=z.zone_id,
            name=name,
            crop_type=crop,
            area=area,
            soil_type=soil,
            last_watering_date=water
        )
        if not success:
            messagebox.showwarning("실패", msg)
            return

        messagebox.showinfo("완료", msg)
        self.refresh()

    def _handle_delete_zone(self) -> None:
        sel = self.tree_zones.selection()
        if not sel:
            messagebox.showwarning("알림", "삭제할 구역을 선택해 주세요.")
            return

        idx = self.tree_zones.index(sel[0])
        z = self.user_zones[idx]

        if not messagebox.askyesno("삭제 확인", f"'{z.name}' 구역을 정말 삭제하시겠습니까?"):
            return

        self.zone_service.delete_zone(z.zone_id)
        messagebox.showinfo("삭제 완료", f"'{z.name}' 구역이 삭제되었습니다.")
        self.refresh()

    # ==========================================
    # 탭 2: 단가 및 장비 소비전력 관리
    # ==========================================
    def _build_unit_tab(self, parent: tk.Frame) -> None:
        grid_f = tk.Frame(parent, bg=AppTheme.SURFACE)
        grid_f.pack(fill="x", pady=10)
        grid_f.columnconfigure(0, weight=1)
        grid_f.columnconfigure(1, weight=1)

        # 1. 물 단가
        tk.Label(grid_f, text="💧 물 공급 단가 (원 / m³)", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.ent_water_price = ttk.Entry(grid_f, font=AppTheme.FONT_BODY)
        self.ent_water_price.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(2, 14))

        # 2. 전기 단가
        tk.Label(grid_f, text="⚡ 전기 요금 단가 (원 / kWh)", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.ent_elec_price = ttk.Entry(grid_f, font=AppTheme.FONT_BODY)
        self.ent_elec_price.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(2, 14))

        # 3. 장비별 소비전력
        tk.Label(grid_f, text="🌀 환기팬 소비전력 (W)", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).grid(row=2, column=0, sticky="w", padx=(0, 10))
        self.ent_fan_power = ttk.Entry(grid_f, font=AppTheme.FONT_BODY)
        self.ent_fan_power.grid(row=3, column=0, sticky="ew", padx=(0, 10), pady=(2, 14))

        tk.Label(grid_f, text="💡 LED 보광등 소비전력 (W)", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).grid(row=2, column=1, sticky="w", padx=(10, 0))
        self.ent_light_power = ttk.Entry(grid_f, font=AppTheme.FONT_BODY)
        self.ent_light_power.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=(2, 14))

        tk.Label(grid_f, text="🔥 온풍난방기 소비전력 (W)", font=AppTheme.FONT_BODY_BOLD, bg=AppTheme.SURFACE).grid(row=4, column=0, sticky="w", padx=(0, 10))
        self.ent_heater_power = ttk.Entry(grid_f, font=AppTheme.FONT_BODY)
        self.ent_heater_power.grid(row=5, column=0, sticky="ew", padx=(0, 10), pady=(2, 20))

        btn_save_settings = tk.Button(
            parent,
            text="💾 단가 및 장비 소비전력 설정 저장",
            font=AppTheme.FONT_BODY_BOLD,
            bg=AppTheme.PRIMARY,
            fg=AppTheme.TEXT_WHITE,
            bd=0,
            pady=10,
            cursor="hand2",
            command=self._save_unit_settings
        )
        btn_save_settings.pack(fill="x")

    def _save_unit_settings(self) -> None:
        try:
            w_price = float(self.ent_water_price.get().strip())
            e_price = float(self.ent_elec_price.get().strip())
            fan_w = float(self.ent_fan_power.get().strip())
            light_w = float(self.ent_light_power.get().strip())
            heat_w = float(self.ent_heater_power.get().strip())
        except ValueError:
            messagebox.showwarning("입력 오류", "모든 단가와 소비전력은 유효한 숫자여야 합니다.")
            return

        settings = self.storage.get_settings()
        settings.water_unit_price = w_price
        settings.electricity_unit_price = e_price

        for eq in settings.equipments:
            if eq.equipment_type == "fan":
                eq.power_watt = fan_w
            elif eq.equipment_type == "light":
                eq.power_watt = light_w
            elif eq.equipment_type == "heater":
                eq.power_watt = heat_w

        self.storage.save_settings(settings)
        messagebox.showinfo("저장 완료", "단가 및 장비 소비전력 설정이 저장되었습니다.")

    # ==========================================
    # 탭 3: 작물별 생육 기준
    # ==========================================
    def _build_crop_tab(self, parent: tk.Frame) -> None:
        tk.Label(
            parent,
            text="작물별 최적 환경 기준치 (급수 시작 수분, 관개요구량, 적정 온습도, 목표 조도/일조시간)",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.SURFACE
        ).pack(anchor="w", pady=(0, 10))

        cols = ("crop", "moisture", "depth", "temp", "hum", "lux", "hours")
        self.tree_crops = ttk.Treeview(parent, columns=cols, show="headings", height=6)
        self.tree_crops.heading("crop", text="작물명")
        self.tree_crops.heading("moisture", text="급수기준 수분(%)")
        self.tree_crops.heading("depth", text="1회관개량(mm)")
        self.tree_crops.heading("temp", text="적정 기온(℃)")
        self.tree_crops.heading("hum", text="적정 습도(%RH)")
        self.tree_crops.heading("lux", text="기준 조도(lx)")
        self.tree_crops.heading("hours", text="목표 일조시간(h)")

        self.tree_crops.column("crop", width=90, anchor="center")
        self.tree_crops.column("moisture", width=120, anchor="center")
        self.tree_crops.column("depth", width=110, anchor="center")
        self.tree_crops.column("temp", width=110, anchor="center")
        self.tree_crops.column("hum", width=110, anchor="center")
        self.tree_crops.column("lux", width=100, anchor="center")
        self.tree_crops.column("hours", width=110, anchor="center")

        self.tree_crops.pack(fill="x")

    def refresh(self) -> None:
        """화면 진입 시 설정 데이터 로드"""
        user = self.auth_service.get_current_user()
        if not user:
            return

        # 1. 구역 목록 갱신
        self.user_zones = self.zone_service.get_user_zones(user.user_id)
        for it in self.tree_zones.get_children():
            self.tree_zones.delete(it)

        for z in self.user_zones:
            self.tree_zones.insert(
                "",
                "end",
                values=(z.name, z.crop_type, f"{z.area:.1f}", z.soil_type, z.last_watering_date or "기록 없음")
            )

        # 2. 단가 및 장비 소비전력 갱신
        settings = self.storage.get_settings()
        self.ent_water_price.delete(0, tk.END)
        self.ent_water_price.insert(0, str(settings.water_unit_price))

        self.ent_elec_price.delete(0, tk.END)
        self.ent_elec_price.insert(0, str(settings.electricity_unit_price))

        fan_w = next((eq.power_watt for eq in settings.equipments if eq.equipment_type == "fan"), 75.0)
        light_w = next((eq.power_watt for eq in settings.equipments if eq.equipment_type == "light"), 120.0)
        heat_w = next((eq.power_watt for eq in settings.equipments if eq.equipment_type == "heater"), 1500.0)

        self.ent_fan_power.delete(0, tk.END)
        self.ent_fan_power.insert(0, str(fan_w))

        self.ent_light_power.delete(0, tk.END)
        self.ent_light_power.insert(0, str(light_w))

        self.ent_heater_power.delete(0, tk.END)
        self.ent_heater_power.insert(0, str(heat_w))

        # 3. 작물 기준 갱신
        standards = self.storage.get_standards()
        for it in self.tree_crops.get_children():
            self.tree_crops.delete(it)

        for name, std in standards.items():
            self.tree_crops.insert(
                "",
                "end",
                values=(
                    std.crop_name,
                    f"< {std.min_soil_moisture:.1f}%",
                    f"{std.irrigation_depth_mm:.1f} mm",
                    f"{std.temp_min:.1f} ~ {std.temp_max:.1f} ℃",
                    f"{std.humidity_min:.1f} ~ {std.humidity_max:.1f} %",
                    f"{std.target_illuminance:,.0f} lx",
                    f"{std.target_light_hours:.1f} 시간"
                )
            )
