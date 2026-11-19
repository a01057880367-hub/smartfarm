/**
 * js/app.js
 * 스마트팜 프론트엔드 UI 컨트롤러 및 애플리케이션 진입점
 */

const App = {
  currentPlan: null,
  currentCandidates: [],
  selectedPeriod: "all",

  init() {
    this.bindEvents();

    const session = AuthService.getCurrentUser();
    if (session) {
      this.showApp();
    } else {
      this.showAuth();
    }
  },

  bindEvents() {
    // 1. 네비게이션 버튼들
    document.querySelectorAll(".nav-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const view = btn.getAttribute("data-view");
        this.navigateTo(view);
      });
    });

    // 로그아웃
    document.getElementById("btnLogout").addEventListener("click", () => {
      if (confirm("로그아웃하시고 첫 화면으로 돌아가시겠습니까?")) {
        AuthService.logout();
        this.showAuth();
      }
    });

    // 2. 인증 관련 이벤트
    document.getElementById("btnGoLogin").addEventListener("click", () => this.showAuthBox("login"));
    document.getElementById("btnGoRegister").addEventListener("click", () => this.showAuthBox("register"));
    document.getElementById("btnQuickDemo").addEventListener("click", () => {
      AuthService.login("farmer", "123");
      this.showApp();
    });

    document.getElementById("linkLoginToWelcome").addEventListener("click", (e) => { e.preventDefault(); this.showAuthBox("welcome"); });
    document.getElementById("linkLoginToReg").addEventListener("click", (e) => { e.preventDefault(); this.showAuthBox("register"); });
    document.getElementById("linkRegToWelcome").addEventListener("click", (e) => { e.preventDefault(); this.showAuthBox("welcome"); });

    // 로그인 폼 제출
    document.getElementById("formLogin").addEventListener("submit", (e) => {
      e.preventDefault();
      const uid = document.getElementById("loginId").value.trim();
      const pw = document.getElementById("loginPw").value.trim();
      const errEl = document.getElementById("loginError");

      const res = AuthService.login(uid, pw);
      if (!res.success) {
        errEl.textContent = res.message;
        errEl.style.display = "block";
        return;
      }

      errEl.style.display = "none";
      if (!ZoneService.hasUserZones(uid)) {
        this.showInitialZoneModal(uid);
      } else {
        this.showApp();
      }
    });

    // 회원가입 폼 제출
    document.getElementById("formRegister").addEventListener("submit", (e) => {
      e.preventDefault();
      const uid = document.getElementById("regId").value.trim();
      const pw = document.getElementById("regPw").value.trim();
      const pwc = document.getElementById("regPwc").value.trim();
      const errEl = document.getElementById("regError");

      const res = AuthService.register(uid, pw, pwc);
      if (!res.success) {
        errEl.textContent = res.message;
        errEl.style.display = "block";
        return;
      }

      errEl.style.display = "none";
      alert("회원가입이 완료되었습니다. 로그인해 주세요.");
      this.showAuthBox("login");
      document.getElementById("loginId").value = uid;
      document.getElementById("loginPw").focus();
    });

    // 최초 구역 등록 모달 폼 제출
    document.getElementById("formInitialZone").addEventListener("submit", (e) => {
      e.preventDefault();
      const session = AuthService.getCurrentUser();
      if (!session) return;

      const name = document.getElementById("initZoneName").value.trim();
      const crop = document.getElementById("initZoneCrop").value;
      const area = document.getElementById("initZoneArea").value;
      const soil = document.getElementById("initZoneSoil").value.trim();
      const errEl = document.getElementById("initZoneError");

      const res = ZoneService.addZone(session.user_id, name, crop, area, soil);
      if (!res.success) {
        errEl.textContent = res.message;
        errEl.style.display = "block";
        return;
      }

      errEl.style.display = "none";
      document.getElementById("modalInitialZone").classList.remove("active");
      alert(`'${name}' 구역이 등록되었습니다.\n대시보드로 이동합니다.`);
      this.showApp();
    });

    // 3. 환경 입력 이벤트
    document.getElementById("envZoneSelect").addEventListener("change", () => this.onEnvZoneSelected());
    document.getElementById("formEnvInput").addEventListener("submit", (e) => this.handleSaveEnv(e));

    // 4. 저비용 운영 계획 이벤트
    document.getElementById("btnCalculatePlan").addEventListener("click", () => this.handleCalculatePlan());

    // 5. 사용량 및 실적 이벤트
    document.getElementById("histPlanSelect").addEventListener("change", () => this.onHistPlanSelected());
    document.getElementById("formHistory").addEventListener("submit", (e) => this.handleSaveHistory(e));

    // 기간 필터 버튼들
    document.querySelectorAll("[data-period]").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll("[data-period]").forEach(b => b.classList.remove("active", "btn-primary"));
        btn.classList.add("active", "btn-primary");
        this.selectedPeriod = btn.getAttribute("data-period");
        this.renderHistoryView();
      });
    });

    // 6. 설정 서브 탭 이벤트
    document.getElementById("tabBtnZones").addEventListener("click", () => this.switchSettingsTab("zones"));
    document.getElementById("tabBtnUnits").addEventListener("click", () => this.switchSettingsTab("units"));
    document.getElementById("tabBtnCrops").addEventListener("click", () => this.switchSettingsTab("crops"));

    document.getElementById("formSettingZone").addEventListener("submit", (e) => this.handleSaveSettingZone(e));
    document.getElementById("btnResetZoneForm").addEventListener("click", () => this.resetSettingZoneForm());
    document.getElementById("formSettingUnits").addEventListener("submit", (e) => this.handleSaveSettingUnits(e));
  },

  // ==========================================
  // 인증 화면 제어
  // ==========================================
  showAuth() {
    document.getElementById("mainNavbar").style.display = "none";
    document.querySelectorAll(".view-section").forEach(s => s.classList.remove("active"));
    document.getElementById("view-auth").classList.add("active");
    this.showAuthBox("welcome");
  },

  showAuthBox(type) {
    document.getElementById("authWelcomeBox").style.display = type === "welcome" ? "block" : "none";
    document.getElementById("authLoginBox").style.display = type === "login" ? "block" : "none";
    document.getElementById("authRegisterBox").style.display = type === "register" ? "block" : "none";
    document.getElementById("loginError").style.display = "none";
    document.getElementById("regError").style.display = "none";
  },

  showInitialZoneModal(userId) {
    document.getElementById("modalInitialZone").classList.add("active");
  },

  showApp() {
    document.getElementById("mainNavbar").style.display = "flex";
    const user = AuthService.getCurrentUser();
    if (user) {
      document.getElementById("navUserBadge").textContent = `👤 ${user.user_id} 농가님`;
    }
    this.navigateTo("home");
  },

  // ==========================================
  // 뷰 라우팅
  // ==========================================
  navigateTo(viewName) {
    document.querySelectorAll(".view-section").forEach(s => s.classList.remove("active"));
    document.querySelectorAll(".nav-btn").forEach(b => {
      if (b.getAttribute("data-view") === viewName) {
        b.classList.add("active");
      } else {
        b.classList.remove("active");
      }
    });

    const target = document.getElementById(`view-${viewName}`);
    if (target) {
      target.classList.add("active");
    }

    // 각 뷰별 렌더링 갱신
    if (viewName === "home") this.renderHomeView();
    if (viewName === "env") this.renderEnvView();
    if (viewName === "plan") this.renderPlanView();
    if (viewName === "history") this.renderHistoryView();
    if (viewName === "settings") this.renderSettingsView();

    window.scrollTo({ top: 0, behavior: "smooth" });
  },

  // ==========================================
  // [A-8] Home 대시보드 렌더링
  // ==========================================
  renderHomeView() {
    const user = AuthService.getCurrentUser();
    if (!user) return;

    document.getElementById("homeWelcomeTitle").textContent = `🌿 ${user.user_id} 농가님의 스마트팜 관제 대시보드`;

    const container = document.getElementById("homeZonesContainer");
    container.innerHTML = "";

    const zones = ZoneService.getUserZones(user.user_id);
    if (zones.length === 0) {
      container.innerHTML = `
        <div class="card" style="text-align: center; padding: 2rem; color: var(--text-muted);">
          등록된 재배 구역이 없습니다. [설정] 메뉴에서 새 구역을 등록해 주세요.
        </div>
      `;
      return;
    }

    zones.forEach(zone => {
      const latest = EnvironmentService.getLatestRecord(zone.zone_id);

      let envContent = "";
      if (latest) {
        const moistureColor = latest.soil_moisture >= 25 ? "var(--primary)" : "var(--danger)";
        envContent = `
          <div class="grid-4" style="background: var(--surface-alt); padding: 0.75rem; border-radius: var(--radius-sm); margin-bottom: 0.5rem;">
            <div>
              <div style="font-size: 0.75rem; color: var(--text-muted);">토양 수분</div>
              <div style="font-weight: 700; color: ${moistureColor};">${latest.soil_moisture.toFixed(1)}%</div>
            </div>
            <div>
              <div style="font-size: 0.75rem; color: var(--text-muted);">현재 기온</div>
              <div style="font-weight: 700;">${latest.temperature.toFixed(1)} ℃</div>
            </div>
            <div>
              <div style="font-size: 0.75rem; color: var(--text-muted);">공기 습도</div>
              <div style="font-weight: 700;">${latest.humidity.toFixed(1)} %RH</div>
            </div>
            <div>
              <div style="font-size: 0.75rem; color: var(--text-muted);">현재 조도</div>
              <div style="font-weight: 700;">${latest.illuminance.toLocaleString()} lx</div>
            </div>
          </div>
          <div style="text-align: right; font-size: 0.75rem; color: var(--text-muted);">최근 측정: ${latest.recorded_at}</div>
        `;
      } else {
        envContent = `
          <div class="stat-box" style="font-size: 0.85rem; color: var(--text-muted);">
            아직 측정된 환경 센서 기록이 없습니다. [구역별 환경 입력]에서 첫 측정값을 등록해 주세요.
          </div>
        `;
      }

      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <h4 style="font-size: 1.15rem; font-weight: 700;">${zone.name}</h4>
            <span class="badge badge-success">${zone.crop_type}</span>
          </div>
          <div style="font-size: 0.85rem; color: var(--text-muted);">
            면적: ${zone.area.toFixed(1)} m² | 토양: ${zone.soil_type} | 최근 급수일: <strong>${zone.last_watering_date || '기록 없음'}</strong>
          </div>
        </div>
        ${envContent}
      `;
      container.appendChild(card);
    });
  },

  // ==========================================
  // [B] 메뉴 1: 환경 입력 렌더링
  // ==========================================
  renderEnvView() {
    const user = AuthService.getCurrentUser();
    if (!user) return;

    const select = document.getElementById("envZoneSelect");
    select.innerHTML = "";

    const zones = ZoneService.getUserZones(user.user_id);
    zones.forEach(z => {
      const opt = document.createElement("option");
      opt.value = z.zone_id;
      opt.textContent = `${z.name} (${z.crop_type})`;
      select.appendChild(opt);
    });

    // 현재 시각 자동 채움
    const now = new Date();
    const nowStr = now.toISOString().replace('T', ' ').substring(0, 16);
    document.getElementById("envRecordedAt").value = nowStr;

    if (zones.length > 0) {
      this.onEnvZoneSelected();
    }
  },

  onEnvZoneSelected() {
    const zoneId = document.getElementById("envZoneSelect").value;
    const zone = ZoneService.getZoneById(zoneId);
    if (!zone) return;

    document.getElementById("envZoneInfoText").innerHTML = `
      • 작물 종류: <strong>${zone.crop_type}</strong><br>
      • 재배면적: <strong>${zone.area.toFixed(1)} m²</strong><br>
      • 토양 종류: <strong>${zone.soil_type}</strong>
    `;

    document.getElementById("envLastWaterDate").value = zone.last_watering_date || "";
    document.getElementById("envFeedbackMsg").style.display = "none";
  },

  handleSaveEnv(e) {
    e.preventDefault();
    const user = AuthService.getCurrentUser();
    if (!user) return;

    const zoneId = document.getElementById("envZoneSelect").value;
    const recordedAt = document.getElementById("envRecordedAt").value.trim();
    const moisture = document.getElementById("envMoisture").value.trim();
    const temp = document.getElementById("envTemp").value.trim();
    const hum = document.getElementById("envHumidity").value.trim();
    const lux = document.getElementById("envLux").value.trim();
    const customWater = document.getElementById("envLastWaterDate").value.trim();
    const msgEl = document.getElementById("envFeedbackMsg");

    const res = EnvironmentService.recordEnvironment(
      user.user_id, zoneId, recordedAt, moisture, temp, hum, lux, customWater
    );

    if (!res.success) {
      msgEl.textContent = res.message;
      msgEl.style.color = "var(--danger)";
      msgEl.style.display = "block";
      return;
    }

    if (customWater) {
      ZoneService.updateLastWateringDate(zoneId, customWater);
    }

    msgEl.textContent = res.message;
    msgEl.style.color = "var(--success)";
    msgEl.style.display = "block";

    // 우측 변화 추이 렌더링
    const container = document.getElementById("envChangeContainer");
    if (res.changeSummary) {
      container.innerHTML = `
        <div class="stat-box" style="border: 1px solid var(--primary-border); background: var(--surface);">
          <div style="font-weight: 700; color: var(--primary); margin-bottom: 0.5rem;">
            ✔ 방금 등록된 측정값 (${res.record.recorded_at})
          </div>
          <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.5rem;">
            이전 측정(${res.changeSummary.prev_time}) 대비 변화:
          </div>
          <ul style="list-style: none; padding: 0; line-height: 1.8; font-size: 0.9rem;">
            <li>• ${res.changeSummary.moisture}</li>
            <li>• ${res.changeSummary.temp}</li>
            <li>• ${res.changeSummary.hum}</li>
            <li>• ${res.changeSummary.lux}</li>
          </ul>
        </div>
      `;
    } else {
      container.innerHTML = `
        <div class="stat-box">
          <div style="font-weight: 700; color: var(--primary); margin-bottom: 0.25rem;">✔ 첫 번째 측정값 등록 완료</div>
          <p style="font-size: 0.85rem; color: var(--text-muted);">
            이 구역의 첫 번째 측정 기록입니다. 다음 측정값부터 변화량이 자동 분석됩니다.
          </p>
        </div>
      `;
    }

    alert("환경 측정값이 성공적으로 저장되었습니다.");
  },

  // ==========================================
  // [C] 메뉴 2: 저비용 운영 계획 렌더링 & 계산
  // ==========================================
  renderPlanView() {
    const user = AuthService.getCurrentUser();
    if (!user) return;

    const select = document.getElementById("planZoneSelect");
    select.innerHTML = "";

    const zones = ZoneService.getUserZones(user.user_id);
    zones.forEach(z => {
      const opt = document.createElement("option");
      opt.value = z.zone_id;
      opt.textContent = `${z.name} (${z.crop_type})`;
      select.appendChild(opt);
    });

    // 전체 구역 관개 요약 표 렌더링 (요구사항 18)
    this.renderWaterSummaryTable(zones);
  },

  renderWaterSummaryTable(zones) {
    const tbody = document.querySelector("#tableWaterSummary tbody");
    tbody.innerHTML = "";

    const standards = SmartFarmStore.getStandards();
    const settings = SmartFarmStore.getSettings();

    let totalWaterL = 0;
    let totalWaterCost = 0;

    zones.forEach(zone => {
      const latest = EnvironmentService.getLatestRecord(zone.zone_id);
      const curMoisture = latest ? latest.soil_moisture : 24.0;
      const std = standards[zone.crop_type] || DEFAULT_CROP_STANDARDS["토마토"];

      const status = curMoisture < std.min_soil_moisture ? "급수 필요" : "급수 보류";
      const waterL = status === "급수 필요" ? Math.round(std.irrigation_depth_mm * zone.area * 10) / 10 : 0.0;
      const wCost = Math.round((waterL / 1000.0) * settings.water_unit_price);

      totalWaterL += waterL;
      totalWaterCost += wCost;

      const badgeClass = status === "급수 필요" ? "badge-danger" : "badge-success";

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${zone.name}</strong></td>
        <td>${zone.crop_type}</td>
        <td>${curMoisture.toFixed(1)}%</td>
        <td><span class="badge ${badgeClass}">${status}</span></td>
        <td>${zone.last_watering_date || '급수 기록 없음'}</td>
        <td><strong>${waterL.toLocaleString()} L</strong></td>
        <td>${wCost.toLocaleString()} 원</td>
      `;
      tbody.appendChild(tr);
    });

    document.getElementById("lblTotalWaterSummary").textContent =
      `전체 권장 급수량 합계: ${totalWaterL.toLocaleString()} L (예상 물 비용: ${totalWaterCost.toLocaleString()} 원)`;
  },

  handleCalculatePlan() {
    const zoneId = document.getElementById("planZoneSelect").value;
    const zone = ZoneService.getZoneById(zoneId);
    if (!zone) {
      alert("분석할 구역을 선택해 주세요.");
      return;
    }

    const latest = EnvironmentService.getLatestRecord(zoneId);
    const standards = SmartFarmStore.getStandards();
    const settings = SmartFarmStore.getSettings();

    const lightHoursInput = document.getElementById("planLightHours").value;
    const lightH = lightHoursInput ? parseFloat(lightHoursInput) : null;

    const { optimalPlan, candidates } = OptimizationService.calculatePlanForZone(
      zone, latest, standards, settings, lightH
    );

    this.currentPlan = optimalPlan;
    this.currentCandidates = candidates;

    // 1. 최적 추천 계획 카드 렌더링 (26, 27)
    this.renderOptimalPlanCard(optimalPlan);

    // 2. 후보군 상세 비교 테이블 렌더링 (28)
    this.renderCandidatesTable(candidates);
  },

  renderOptimalPlanCard(plan) {
    const card = document.getElementById("optimalPlanCard");
    const badgeClass = plan.meets_criteria ? "badge-success" : "badge-warning";

    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <h3 style="font-size: 1.25rem; font-weight: 700; color: var(--primary);">⭐ 추천 최저비용 운영 계획</h3>
          <span class="badge ${badgeClass}">${plan.unmet_issues}</span>
        </div>
        <button class="btn btn-primary btn-sm" id="btnSaveThisPlan">💾 이 계획 저장하기</button>
      </div>

      <div style="background: var(--primary-subtle); border: 1px solid var(--primary-border); border-radius: var(--radius-sm); padding: 0.75rem 1rem; margin-bottom: 1rem; font-size: 0.95rem;">
        <strong>📋 권장 작업 순서:</strong> ${plan.action_sequence}
      </div>

      <div class="grid-4">
        <div class="stat-box">
          <div class="stat-label">권장 급수량</div>
          <div class="stat-value">${plan.recommended_water_liter.toLocaleString()} L</div>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
            판단: ${plan.moisture_status} (최근 급수: ${plan.last_watering_date})
          </div>
        </div>
        <div class="stat-box">
          <div class="stat-label">조절 후 예상 기온/습도</div>
          <div class="stat-value" style="color: var(--text-main); font-size: 1.2rem;">${plan.predicted_temp.toFixed(1)}℃ / ${plan.predicted_humidity.toFixed(1)}%</div>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">장비 가동 후 환경 수렴치</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">추가 보광 시간</div>
          <div class="stat-value" style="color: var(--text-main);">${plan.additional_light_hours.toFixed(1)} 시간</div>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">LED 식물생장등 기준</div>
        </div>
        <div class="stat-box highlight">
          <div class="stat-label">총 예상 운영비 (물+전기)</div>
          <div class="stat-value">${plan.total_cost.toLocaleString()} 원</div>
          <div style="font-size: 0.75rem; color: #92400E; margin-top: 0.25rem;">
            물 ${plan.water_cost.toLocaleString()}원 + 전기 ${plan.electricity_cost.toLocaleString()}원
          </div>
        </div>
      </div>
    `;

    document.getElementById("btnSaveThisPlan").addEventListener("click", () => {
      OptimizationService.savePlan(plan);
      alert(`'${plan.zone_name}'의 운영 계획이 성공적으로 저장되었습니다.\n[사용량·비용 이력] 메뉴에서 이 계획을 불러와 실제 작업 결과를 기록할 수 있습니다.`);
    });
  },

  renderCandidatesTable(candidates) {
    const tbody = document.querySelector("#tableCandidates tbody");
    tbody.innerHTML = "";

    candidates.forEach(c => {
      const fanOp = c.operations.find(o => o.type === "fan");
      const fanText = fanOp ? `${fanOp.duration_minutes}분` : "0분";
      const lightText = c.additional_light_hours > 0 ? `${c.additional_light_hours.toFixed(1)}시간` : "0시간";
      const meetsBadge = c.meets_criteria
        ? `<span class="badge badge-success">✔ 적합</span>`
        : `<span class="badge badge-warning" title="${c.unmet_issues}">⚠ 미달</span>`;

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${c.candidate_name}</strong></td>
        <td>${fanText}</td>
        <td>${lightText}</td>
        <td>${c.predicted_temp.toFixed(1)}℃</td>
        <td>${c.predicted_humidity.toFixed(1)}%</td>
        <td>${c.total_kwh.toFixed(3)} kWh</td>
        <td>${c.electricity_cost.toLocaleString()}원</td>
        <td><strong>${c.total_cost.toLocaleString()}원</strong></td>
        <td>${meetsBadge}</td>
      `;
      tbody.appendChild(tr);
    });
  },

  // ==========================================
  // [D] 메뉴 3: 사용량 및 실적 이력 렌더링
  // ==========================================
  renderHistoryView() {
    const user = AuthService.getCurrentUser();
    if (!user) return;

    // 구역 셀렉트
    const zoneSelect = document.getElementById("histZoneSelect");
    zoneSelect.innerHTML = "";
    const zones = ZoneService.getUserZones(user.user_id);
    zones.forEach(z => {
      const opt = document.createElement("option");
      opt.value = z.zone_id;
      opt.textContent = `${z.name} (${z.crop_type})`;
      zoneSelect.appendChild(opt);
    });

    // 계획 셀렉트 (요구사항 29)
    const planSelect = document.getElementById("histPlanSelect");
    planSelect.innerHTML = `<option value="">(계획 없이 직접 입력)</option>`;

    const allPlans = SmartFarmStore.getPlans();
    const userZoneIds = zones.map(z => z.zone_id);
    const userPlans = allPlans.filter(p => userZoneIds.includes(p.zone_id));

    userPlans.forEach(p => {
      const opt = document.createElement("option");
      opt.value = p.plan_id;
      opt.textContent = `[${p.created_at.substring(0, 10)}] ${p.zone_name} (권장: ${p.recommended_water_liter.toLocaleString()}L / ${p.total_cost.toLocaleString()}원)`;
      planSelect.appendChild(opt);
    });

    // 오늘 일자 기본값
    document.getElementById("histDate").value = new Date().toISOString().substring(0, 10);

    // 실적 목록 및 통계 집계 렌더링 (33, 34, 35)
    this.renderHistoryStatsAndTable(user.user_id);
  },

  onHistPlanSelected() {
    const planId = document.getElementById("histPlanSelect").value;
    const hint = document.getElementById("histPlanHint");
    if (!planId) {
      hint.textContent = "직접 실적을 입력합니다.";
      return;
    }

    const plans = SmartFarmStore.getPlans();
    const plan = plans.find(p => p.plan_id === planId);
    if (!plan) return;

    document.getElementById("histZoneSelect").value = plan.zone_id;
    document.getElementById("histWater").value = plan.recommended_water_liter;
    document.getElementById("histLightH").value = plan.additional_light_hours;

    const fanOp = plan.operations.find(o => o.type === "fan");
    document.getElementById("histFanMin").value = fanOp ? fanOp.duration_minutes : 0;

    hint.textContent = `✔ 계획 연동됨 (권장 급수: ${plan.recommended_water_liter.toLocaleString()}L, 예상비용: ${plan.total_cost.toLocaleString()}원)`;
  },

  handleSaveHistory(e) {
    e.preventDefault();
    const user = AuthService.getCurrentUser();
    if (!user) return;

    const zoneId = document.getElementById("histZoneSelect").value;
    const zone = ZoneService.getZoneById(zoneId);
    if (!zone) return;

    const planId = document.getElementById("histPlanSelect").value;
    const plans = SmartFarmStore.getPlans();
    const associatedPlan = plans.find(p => p.plan_id === planId) || null;

    const dateStr = document.getElementById("histDate").value;
    const waterL = document.getElementById("histWater").value;
    const lightH = document.getElementById("histLightH").value;
    const fanM = document.getElementById("histFanMin").value;
    const heaterM = document.getElementById("histHeaterMin").value;
    const measuredKwh = document.getElementById("histMeasuredKwh").value;

    const settings = SmartFarmStore.getSettings();

    const res = HistoryService.saveActualRecord(
      user.user_id,
      zoneId,
      zone.name,
      zone.crop_type,
      dateStr,
      waterL,
      lightH,
      fanM,
      heaterM,
      measuredKwh,
      settings,
      associatedPlan
    );

    if (res.success) {
      alert("실적 데이터가 성공적으로 저장되었습니다.\n실제 급수량이 있을 경우 해당 구역의 최근 급수일에 즉시 반영되었습니다.");
      this.renderHistoryStatsAndTable(user.user_id);
    }
  },

  renderHistoryStatsAndTable(userId) {
    const histories = HistoryService.filterHistories(userId, this.selectedPeriod);
    const stats = HistoryService.calculateStatistics(histories);

    // 통계 지표 업데이트 (34)
    document.getElementById("statTotalWater").textContent = `${stats.total_water_liter.toLocaleString()} L`;
    document.getElementById("statTotalLight").textContent = `${stats.total_light_hours.toFixed(1)} h`;
    document.getElementById("statTotalKwh").textContent = `${stats.total_kwh.toFixed(2)} kWh`;
    document.getElementById("statTotalCost").textContent = `${stats.total_cost.toLocaleString()} 원`;

    // 비교 테이블 업데이트 (35)
    const tbody = document.querySelector("#tableHistories tbody");
    tbody.innerHTML = "";

    if (histories.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted);">해당 기간에 저장된 실적 기록이 없습니다.</td></tr>`;
      return;
    }

    histories.forEach(h => {
      const waterComp = h.recommended_water_liter > 0
        ? `${h.recommended_water_liter.toLocaleString()}L / <strong>${h.actual_water_liter.toLocaleString()}L</strong>`
        : `- / <strong>${h.actual_water_liter.toLocaleString()}L</strong>`;

      const costComp = h.planned_total_cost > 0
        ? `${h.planned_total_cost.toLocaleString()}원 / <strong>${h.total_cost.toLocaleString()}원</strong>`
        : `- / <strong>${h.total_cost.toLocaleString()}원</strong>`;

      const kwhText = `${h.total_kwh.toFixed(2)} kWh ${h.is_estimated_kwh ? '<span style="color:var(--text-muted); font-size:0.75rem;">(추정)</span>' : '<span style="color:var(--primary); font-size:0.75rem;">(실측)</span>'}`;

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${h.date}</td>
        <td><strong>${h.zone_name}</strong></td>
        <td>${h.crop_type}</td>
        <td>${waterComp}</td>
        <td>${h.light_duration_hours.toFixed(1)}h</td>
        <td>${kwhText}</td>
        <td>${costComp}</td>
      `;
      tbody.appendChild(tr);
    });
  },

  // ==========================================
  // [E] 설정 렌더링 & 제어 (36)
  // ==========================================
  renderSettingsView() {
    this.switchSettingsTab("zones");
    this.renderSettingsZonesTable();
    this.renderSettingsUnitsForm();
    this.renderCropStandardsTable();
  },

  switchSettingsTab(tab) {
    document.getElementById("tabBtnZones").className = tab === "zones" ? "btn btn-sm btn-primary" : "btn btn-sm btn-secondary";
    document.getElementById("tabBtnUnits").className = tab === "units" ? "btn btn-sm btn-primary" : "btn btn-sm btn-secondary";
    document.getElementById("tabBtnCrops").className = tab === "crops" ? "btn btn-sm btn-primary" : "btn btn-sm btn-secondary";

    document.getElementById("tabContentZones").style.display = tab === "zones" ? "block" : "none";
    document.getElementById("tabContentUnits").style.display = tab === "units" ? "block" : "none";
    document.getElementById("tabContentCrops").style.display = tab === "crops" ? "block" : "none";
  },

  renderSettingsZonesTable() {
    const user = AuthService.getCurrentUser();
    if (!user) return;

    const tbody = document.querySelector("#tableSettingsZones tbody");
    tbody.innerHTML = "";

    const zones = ZoneService.getUserZones(user.user_id);
    zones.forEach(z => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${z.name}</strong></td>
        <td>${z.crop_type}</td>
        <td>${z.area.toFixed(1)}</td>
        <td>${z.soil_type}</td>
        <td>
          <button class="btn btn-sm btn-secondary" onclick="App.editSettingZone('${z.zone_id}')">수정</button>
          <button class="btn btn-sm btn-danger" onclick="App.deleteSettingZone('${z.zone_id}')">삭제</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  },

  editSettingZone(zoneId) {
    const zone = ZoneService.getZoneById(zoneId);
    if (!zone) return;

    document.getElementById("settingZoneId").value = zone.zone_id;
    document.getElementById("settingZoneName").value = zone.name;
    document.getElementById("settingZoneCrop").value = zone.crop_type;
    document.getElementById("settingZoneArea").value = zone.area;
    document.getElementById("settingZoneSoil").value = zone.soil_type;

    document.getElementById("zoneFormTitle").textContent = "구역 정보 수정";
    document.getElementById("btnResetZoneForm").style.display = "inline-block";
  },

  deleteSettingZone(zoneId) {
    const zone = ZoneService.getZoneById(zoneId);
    if (!zone) return;

    if (confirm(`'${zone.name}' 구역을 삭제하시겠습니까?`)) {
      ZoneService.deleteZone(zoneId);
      this.renderSettingsZonesTable();
    }
  },

  resetSettingZoneForm() {
    document.getElementById("settingZoneId").value = "";
    document.getElementById("settingZoneName").value = "";
    document.getElementById("settingZoneArea").value = "";
    document.getElementById("settingZoneSoil").value = "";
    document.getElementById("zoneFormTitle").textContent = "새 구역 추가";
    document.getElementById("btnResetZoneForm").style.display = "none";
  },

  handleSaveSettingZone(e) {
    e.preventDefault();
    const user = AuthService.getCurrentUser();
    if (!user) return;

    const zoneId = document.getElementById("settingZoneId").value;
    const name = document.getElementById("settingZoneName").value.trim();
    const crop = document.getElementById("settingZoneCrop").value;
    const area = document.getElementById("settingZoneArea").value;
    const soil = document.getElementById("settingZoneSoil").value.trim();

    if (zoneId) {
      const res = ZoneService.updateZone(zoneId, name, crop, area, soil);
      alert(res.message);
    } else {
      const res = ZoneService.addZone(user.user_id, name, crop, area, soil);
      alert(res.message);
    }

    this.resetSettingZoneForm();
    this.renderSettingsZonesTable();
  },

  renderSettingsUnitsForm() {
    const s = SmartFarmStore.getSettings();
    document.getElementById("setWaterPrice").value = s.water_unit_price;
    document.getElementById("setElecPrice").value = s.electricity_unit_price;

    const fan = s.equipments.find(e => e.equipment_type === "fan") || { power_watt: 75 };
    const light = s.equipments.find(e => e.equipment_type === "light") || { power_watt: 120 };
    const heater = s.equipments.find(e => e.equipment_type === "heater") || { power_watt: 1500 };

    document.getElementById("setFanPower").value = fan.power_watt;
    document.getElementById("setLightPower").value = light.power_watt;
    document.getElementById("setHeaterPower").value = heater.power_watt;
  },

  handleSaveSettingUnits(e) {
    e.preventDefault();
    const s = SmartFarmStore.getSettings();
    s.water_unit_price = parseFloat(document.getElementById("setWaterPrice").value) || 450;
    s.electricity_unit_price = parseFloat(document.getElementById("setElecPrice").value) || 140;

    const fan = s.equipments.find(e => e.equipment_type === "fan");
    if (fan) fan.power_watt = parseFloat(document.getElementById("setFanPower").value) || 75;

    const light = s.equipments.find(e => e.equipment_type === "light");
    if (light) light.power_watt = parseFloat(document.getElementById("setLightPower").value) || 120;

    const heater = s.equipments.find(e => e.equipment_type === "heater");
    if (heater) heater.power_watt = parseFloat(document.getElementById("setHeaterPower").value) || 1500;

    SmartFarmStore.saveSettings(s);
    alert("단가 및 장비 소비전력 설정이 저장되었습니다.");
  },

  renderCropStandardsTable() {
    const tbody = document.querySelector("#tableCropStandards tbody");
    tbody.innerHTML = "";

    const stds = SmartFarmStore.getStandards();
    Object.values(stds).forEach(std => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${std.crop_name}</strong></td>
        <td>&lt; ${std.min_soil_moisture.toFixed(1)}%</td>
        <td>${std.irrigation_depth_mm.toFixed(1)} mm</td>
        <td>${std.temp_min.toFixed(1)} ~ ${std.temp_max.toFixed(1)} ℃</td>
        <td>${std.humidity_min.toFixed(1)} ~ ${std.humidity_max.toFixed(1)} %</td>
        <td>${std.target_illuminance.toLocaleString()} lx</td>
        <td>${std.target_light_hours.toFixed(1)} 시간</td>
      `;
      tbody.appendChild(tr);
    });
  }
};

// DOM 로드 완료 후 실행
document.addEventListener("DOMContentLoaded", () => {
  App.init();
});
