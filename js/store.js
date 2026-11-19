/**
 * js/store.js
 * 로컬스토리지 기반 영속성 데이터 저장소 및 초기 데모 데이터
 */

const DEFAULT_CROP_STANDARDS = {
  "토마토": {
    crop_name: "토마토",
    min_soil_moisture: 25.0,
    irrigation_depth_mm: 10.0,
    temp_min: 18.0,
    temp_max: 28.0,
    humidity_min: 50.0,
    humidity_max: 75.0,
    target_illuminance: 30000.0,
    target_light_hours: 8.0
  },
  "상추": {
    crop_name: "상추",
    min_soil_moisture: 30.0,
    irrigation_depth_mm: 8.0,
    temp_min: 15.0,
    temp_max: 22.0,
    humidity_min: 60.0,
    humidity_max: 80.0,
    target_illuminance: 20000.0,
    target_light_hours: 7.0
  },
  "딸기": {
    crop_name: "딸기",
    min_soil_moisture: 28.0,
    irrigation_depth_mm: 9.0,
    temp_min: 16.0,
    temp_max: 24.0,
    humidity_min: 55.0,
    humidity_max: 75.0,
    target_illuminance: 25000.0,
    target_light_hours: 8.0
  },
  "파프리카": {
    crop_name: "파프리카",
    min_soil_moisture: 27.0,
    irrigation_depth_mm: 10.0,
    temp_min: 20.0,
    temp_max: 27.0,
    humidity_min: 55.0,
    humidity_max: 75.0,
    target_illuminance: 35000.0,
    target_light_hours: 8.0
  }
};

const DEFAULT_SETTINGS = {
  water_unit_price: 450.0,        // 원 / m³
  electricity_unit_price: 140.0,  // 원 / kWh
  equipments: [
    { name: "환기팬 1호", power_watt: 75.0, equipment_type: "fan" },
    { name: "LED 보광등 A", power_watt: 120.0, equipment_type: "light" },
    { name: "온풍난방기", power_watt: 1500.0, equipment_type: "heater" }
  ]
};

const SmartFarmStore = {
  KEYS: {
    USERS: "sf_users",
    ZONES: "sf_zones",
    STANDARDS: "sf_standards",
    SETTINGS: "sf_settings",
    ENVIRONMENTS: "sf_environments",
    PLANS: "sf_plans",
    HISTORIES: "sf_histories",
    SESSION: "sf_session"
  },

  init() {
    // 1. 작물 기준 초기화
    if (!localStorage.getItem(this.KEYS.STANDARDS)) {
      localStorage.setItem(this.KEYS.STANDARDS, JSON.stringify(DEFAULT_CROP_STANDARDS));
    }
    // 2. 단가 및 장비 초기화
    if (!localStorage.getItem(this.KEYS.SETTINGS)) {
      localStorage.setItem(this.KEYS.SETTINGS, JSON.stringify(DEFAULT_SETTINGS));
    }
    // 3. 데모 계정 및 기본 구역 초기화
    if (!localStorage.getItem(this.KEYS.USERS)) {
      const demoUser = [{ user_id: "farmer", password: "123", created_at: "2026-11-19 12:00:00" }];
      localStorage.setItem(this.KEYS.USERS, JSON.stringify(demoUser));

      const demoZones = [
        {
          zone_id: "zone_01",
          user_id: "farmer",
          name: "A구역 (스마트 온실 1)",
          crop_type: "토마토",
          area: 100.0,
          soil_type: "사양토",
          last_watering_date: "2026-11-15"
        },
        {
          zone_id: "zone_02",
          user_id: "farmer",
          name: "B구역 (수직 농장 2)",
          crop_type: "상추",
          area: 60.0,
          soil_type: "양토",
          last_watering_date: "2026-11-17"
        }
      ];
      localStorage.setItem(this.KEYS.ZONES, JSON.stringify(demoZones));

      const demoEnv = [
        {
          record_id: "env_01",
          zone_id: "zone_01",
          user_id: "farmer",
          recorded_at: "2026-11-18 09:00",
          soil_moisture: 26.0,
          temperature: 29.5,
          humidity: 82.0,
          illuminance: 18000.0
        },
        {
          record_id: "env_02",
          zone_id: "zone_01",
          user_id: "farmer",
          recorded_at: "2026-11-19 14:00",
          soil_moisture: 22.0,
          temperature: 28.8,
          humidity: 79.0,
          illuminance: 22000.0
        },
        {
          record_id: "env_03",
          zone_id: "zone_02",
          user_id: "farmer",
          recorded_at: "2026-11-19 14:00",
          soil_moisture: 34.0,
          temperature: 20.5,
          humidity: 68.0,
          illuminance: 21000.0
        }
      ];
      localStorage.setItem(this.KEYS.ENVIRONMENTS, JSON.stringify(demoEnv));
    }
  },

  _get(key, defaultVal) {
    const data = localStorage.getItem(key);
    if (!data) return defaultVal;
    try {
      return JSON.parse(data);
    } catch (e) {
      return defaultVal;
    }
  },

  _set(key, val) {
    localStorage.setItem(key, JSON.stringify(val));
  },

  // Users
  getUsers() { return this._get(this.KEYS.USERS, []); },
  saveUsers(users) { this._set(this.KEYS.USERS, users); },

  // Session
  getSession() { return this._get(this.KEYS.SESSION, null); },
  setSession(user) { this._set(this.KEYS.SESSION, user); },
  clearSession() { localStorage.removeItem(this.KEYS.SESSION); },

  // Zones
  getZones() { return this._get(this.KEYS.ZONES, []); },
  saveZones(zones) { this._set(this.KEYS.ZONES, zones); },

  // Environments
  getEnvironments() { return this._get(this.KEYS.ENVIRONMENTS, []); },
  saveEnvironments(records) { this._set(this.KEYS.ENVIRONMENTS, records); },

  // Plans
  getPlans() { return this._get(this.KEYS.PLANS, []); },
  savePlans(plans) { this._set(this.KEYS.PLANS, plans); },

  // Histories
  getHistories() { return this._get(this.KEYS.HISTORIES, []); },
  saveHistories(histories) { this._set(this.KEYS.HISTORIES, histories); },

  // Settings
  getSettings() { return this._get(this.KEYS.SETTINGS, DEFAULT_SETTINGS); },
  saveSettings(settings) { this._set(this.KEYS.SETTINGS, settings); },

  // Standards
  getStandards() { return this._get(this.KEYS.STANDARDS, DEFAULT_CROP_STANDARDS); },
  saveStandards(stds) { this._set(this.KEYS.STANDARDS, stds); }
};

SmartFarmStore.init();
