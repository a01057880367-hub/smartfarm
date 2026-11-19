/**
 * js/services.js
 * 스마트팜 핵심 비즈니스 로직 및 계산 알고리즘 서비스
 */

const AuthService = {
  register(userId, password, passwordConfirm) {
    userId = (userId || "").trim();
    password = (password || "").trim();
    passwordConfirm = (passwordConfirm || "").trim();

    if (!userId) return { success: false, message: "아이디를 입력해 주세요." };
    if (!password) return { success: false, message: "비밀번호를 입력해 주세요." };
    if (!passwordConfirm) return { success: false, message: "비밀번호 확인을 입력해 주세요." };
    if (password !== passwordConfirm) {
      return { success: false, message: "두 비밀번호가 일치하지 않습니다. 다시 확인해 주세요." };
    }

    const users = SmartFarmStore.getUsers();
    if (users.some(u => u.user_id.toLowerCase() === userId.toLowerCase())) {
      return { success: false, message: `이미 등록된 아이디 '${userId}' 입니다. 다른 아이디를 사용해 주세요.` };
    }

    const newUser = {
      user_id: userId,
      password: password,
      created_at: new Date().toISOString().replace('T', ' ').substring(0, 19)
    };
    users.push(newUser);
    SmartFarmStore.saveUsers(users);

    return { success: true, message: "회원가입이 완료되었습니다. 로그인해 주세요." };
  },

  login(userId, password) {
    userId = (userId || "").trim();
    password = (password || "").trim();

    if (!userId || !password) {
      return { success: false, message: "아이디와 비밀번호를 모두 입력해 주세요." };
    }

    const users = SmartFarmStore.getUsers();
    const user = users.find(u => u.user_id === userId);
    if (!user) {
      return { success: false, message: "등록되지 않은 아이디입니다. 아이디를 확인하거나 회원가입을 진행해 주세요." };
    }

    if (user.password !== password) {
      return { success: false, message: "비밀번호가 일치하지 않습니다. 다시 확인해 주세요." };
    }

    SmartFarmStore.setSession({ user_id: user.user_id });
    return { success: true, message: "로그인에 성공하였습니다.", user };
  },

  logout() {
    SmartFarmStore.clearSession();
  },

  getCurrentUser() {
    return SmartFarmStore.getSession();
  }
};

const ZoneService = {
  getUserZones(userId) {
    const all = SmartFarmStore.getZones();
    return all.filter(z => z.user_id === userId);
  },

  hasUserZones(userId) {
    return this.getUserZones(userId).length > 0;
  },

  getZoneById(zoneId) {
    const all = SmartFarmStore.getZones();
    return all.find(z => z.zone_id === zoneId) || null;
  },

  addZone(userId, name, cropType, area, soilType, lastWateringDate = null) {
    name = (name || "").trim();
    cropType = (cropType || "").trim();
    soilType = (soilType || "").trim();
    const areaNum = parseFloat(area);

    if (!name) return { success: false, message: "구역 이름을 입력해 주세요." };
    if (!cropType) return { success: false, message: "작물 종류를 선택해 주세요." };
    if (isNaN(areaNum) || areaNum <= 0) return { success: false, message: "재배면적은 0보다 큰 숫자여야 합니다." };
    if (!soilType) return { success: false, message: "토양 종류를 입력해 주세요." };

    const newZone = {
      zone_id: "zone_" + Math.random().toString(36).substring(2, 8),
      user_id: userId,
      name,
      crop_type: cropType,
      area: areaNum,
      soil_type: soilType,
      last_watering_date: lastWateringDate || null
    };

    const all = SmartFarmStore.getZones();
    all.push(newZone);
    SmartFarmStore.saveZones(all);

    return { success: true, message: `'${name}' 구역이 등록되었습니다.`, zone: newZone };
  },

  updateZone(zoneId, name, cropType, area, soilType, lastWateringDate = null) {
    const all = SmartFarmStore.getZones();
    const zone = all.find(z => z.zone_id === zoneId);
    if (!zone) return { success: false, message: "해당 구역을 찾을 수 없습니다." };

    const areaNum = parseFloat(area);
    if (!name.trim() || !cropType.trim() || isNaN(areaNum) || areaNum <= 0) {
      return { success: false, message: "올바른 구역 정보를 입력해 주세요." };
    }

    zone.name = name.trim();
    zone.crop_type = cropType.trim();
    zone.area = areaNum;
    zone.soil_type = soilType.trim();
    if (lastWateringDate !== undefined) {
      zone.last_watering_date = lastWateringDate;
    }

    SmartFarmStore.saveZones(all);
    return { success: true, message: "구역 정보가 수정되었습니다." };
  },

  updateLastWateringDate(zoneId, dateStr) {
    const all = SmartFarmStore.getZones();
    const zone = all.find(z => z.zone_id === zoneId);
    if (zone) {
      zone.last_watering_date = dateStr;
      SmartFarmStore.saveZones(all);
      return true;
    }
    return false;
  },

  deleteZone(zoneId) {
    const all = SmartFarmStore.getZones();
    const filtered = all.filter(z => z.zone_id !== zoneId);
    if (filtered.length !== all.length) {
      SmartFarmStore.saveZones(filtered);
      return true;
    }
    return false;
  }
};

const EnvironmentService = {
  getRecordsByZone(zoneId) {
    const all = SmartFarmStore.getEnvironments();
    return all.filter(r => r.zone_id === zoneId).sort((a, b) => a.recorded_at.localeCompare(b.recorded_at));
  },

  getLatestRecord(zoneId) {
    const records = this.getRecordsByZone(zoneId);
    return records.length > 0 ? records[records.length - 1] : null;
  },

  recordEnvironment(userId, zoneId, recordedAt, moistureStr, tempStr, humStr, luxStr, customWateringDate = null) {
    const moisture = parseFloat(moistureStr);
    const temp = parseFloat(tempStr);
    const hum = parseFloat(humStr);
    const lux = parseFloat(luxStr);

    if (isNaN(moisture) || isNaN(temp) || isNaN(hum) || isNaN(lux)) {
      return { success: false, message: "측정값은 모두 유효한 숫자 형식이어야 합니다." };
    }

    if (moisture < 0 || moisture > 100) return { success: false, message: "토양 수분은 0%에서 100% 사이여야 합니다." };
    if (temp < -20 || temp > 60) return { success: false, message: "기온은 -20℃에서 60℃ 사이여야 합니다." };
    if (hum < 0 || hum > 100) return { success: false, message: "공기 상대습도는 0%에서 100% 사이여야 합니다." };
    if (lux < 0) return { success: false, message: "조도는 0 lx 이상이어야 합니다." };

    if (customWateringDate && customWateringDate.trim()) {
      const recDate = recordedAt.substring(0, 10);
      if (customWateringDate > recDate) {
        return {
          success: false,
          message: `최근 급수일(${customWateringDate})은 측정 일자(${recDate})보다 미래일 수 없습니다.`
        };
      }
    }

    const prevRecord = this.getLatestRecord(zoneId);

    const newRecord = {
      record_id: "env_" + Math.random().toString(36).substring(2, 9),
      zone_id: zoneId,
      user_id: userId,
      recorded_at: recordedAt,
      soil_moisture: Math.round(moisture * 10) / 10,
      temperature: Math.round(temp * 10) / 10,
      humidity: Math.round(hum * 10) / 10,
      illuminance: Math.round(lux)
    };

    const all = SmartFarmStore.getEnvironments();
    all.push(newRecord);
    SmartFarmStore.saveEnvironments(all);

    let changeSummary = null;
    if (prevRecord) {
      const mDiff = newRecord.soil_moisture - prevRecord.soil_moisture;
      const tDiff = newRecord.temperature - prevRecord.temperature;
      const hDiff = newRecord.humidity - prevRecord.humidity;
      const lDiff = newRecord.illuminance - prevRecord.illuminance;

      changeSummary = {
        moisture: `토양 수분: ${prevRecord.soil_moisture.toFixed(1)}% → ${newRecord.soil_moisture.toFixed(1)}% (${mDiff >= 0 ? '+' : ''}${mDiff.toFixed(1)}%p)`,
        temp: `기온: ${prevRecord.temperature.toFixed(1)}℃ → ${newRecord.temperature.toFixed(1)}℃ (${tDiff >= 0 ? '+' : ''}${tDiff.toFixed(1)}℃)`,
        hum: `상대습도: ${prevRecord.humidity.toFixed(1)}% → ${newRecord.humidity.toFixed(1)}% (${hDiff >= 0 ? '+' : ''}${hDiff.toFixed(1)}%p)`,
        lux: `조도: ${prevRecord.illuminance.toLocaleString()} lx → ${newRecord.illuminance.toLocaleString()} lx (${lDiff >= 0 ? '+' : ''}${lDiff.toLocaleString()} lx)`,
        prev_time: prevRecord.recorded_at
      };
    }

    return {
      success: true,
      message: "환경 측정값이 성공적으로 저장되었습니다.",
      record: newRecord,
      changeSummary
    };
  }
};

const OptimizationService = {
  calculatePlanForZone(zone, latestEnv, standardsMap, settings, todayLightHours = null) {
    const cropStd = standardsMap[zone.crop_type] || DEFAULT_CROP_STANDARDS["토마토"];

    const curMoisture = latestEnv ? latestEnv.soil_moisture : 24.0;
    const curTemp = latestEnv ? latestEnv.temperature : 26.0;
    const curHum = latestEnv ? latestEnv.humidity : 70.0;
    const curLux = latestEnv ? latestEnv.illuminance : 20000.0;

    // 1. 관개 판단 (16, 17)
    const moistureStatus = curMoisture < cropStd.min_soil_moisture ? "급수 필요" : "급수 보류";
    const waterLiters = moistureStatus === "급수 필요" ? Math.round(cropStd.irrigation_depth_mm * zone.area * 10) / 10 : 0.0;
    const waterCost = Math.round((waterLiters / 1000.0) * settings.water_unit_price);

    // 2. 조도 필요 시간 (20, 21)
    let neededLightHours = 0.0;
    if (todayLightHours !== null && todayLightHours !== undefined && !isNaN(todayLightHours)) {
      neededLightHours = Math.max(0.0, Math.round((cropStd.target_light_hours - todayLightHours) * 10) / 10);
    } else {
      neededLightHours = curLux < cropStd.target_illuminance ? 2.0 : 0.0;
    }

    // 장비 사양
    const fanEq = settings.equipments.find(e => e.equipment_type === "fan") || { power_watt: 75.0, name: "환기팬" };
    const lightEq = settings.equipments.find(e => e.equipment_type === "light") || { power_watt: 120.0, name: "LED 보광등" };
    const heaterEq = settings.equipments.find(e => e.equipment_type === "heater") || { power_watt: 1500.0, name: "온풍난방기" };

    // 3. 후보군 시뮬레이션
    const candidateConfigs = [
      { name: "후보 1 (최소 가동 / 기본 유지)", fanMin: 0, lightH: 0, heaterMin: 0, actionSeq: "장비 미가동 (자연 환기 및 자연광 유지)" },
      { name: "후보 2 (표준 환기 10분 + 보광)", fanMin: 10, lightH: neededLightHours, heaterMin: 0, actionSeq: "환기팬 10분 가동 → 기온 재확인 → 필요시 보광등 가동" },
      { name: "후보 3 (집중 환기 20분 + 충분 보광)", fanMin: 20, lightH: neededLightHours > 0 ? neededLightHours : 1.0, heaterMin: 0, actionSeq: "환기팬 20분 집중 환기 → 습도 저감 후 보광등 가동" }
    ];

    if (curTemp < cropStd.temp_min) {
      candidateConfigs.push({
        name: "후보 4 (저온 대비 온풍 난방 15분)",
        fanMin: 0,
        lightH: neededLightHours,
        heaterMin: 15,
        actionSeq: "온풍난방기 15분 가동으로 설정 온도 회복"
      });
    }

    const candidates = [];
    const nowStr = new Date().toISOString().replace('T', ' ').substring(0, 16);
    const lastWaterText = zone.last_watering_date || "급수 기록 없음";

    candidateConfigs.forEach((cfg, idx) => {
      let totalKwh = 0.0;
      let totalElecCost = 0.0;
      const operations = [];

      // 환기팬
      if (cfg.fanMin > 0) {
        const kwh = (fanEq.power_watt * (cfg.fanMin / 60.0)) / 1000.0;
        const cost = kwh * settings.electricity_unit_price;
        totalKwh += kwh;
        totalElecCost += cost;
        operations.push({ name: fanEq.name, type: "fan", duration_minutes: cfg.fanMin, kwh, cost });
      }

      // 난방기
      if (cfg.heaterMin > 0) {
        const kwh = (heaterEq.power_watt * (cfg.heaterMin / 60.0)) / 1000.0;
        const cost = kwh * settings.electricity_unit_price;
        totalKwh += kwh;
        totalElecCost += cost;
        operations.push({ name: heaterEq.name, type: "heater", duration_minutes: cfg.heaterMin, kwh, cost });
      }

      // 보광등
      if (cfg.lightH > 0) {
        const kwh = (lightEq.power_watt * cfg.lightH) / 1000.0;
        const cost = kwh * settings.electricity_unit_price;
        totalKwh += kwh;
        totalElecCost += cost;
        operations.push({ name: lightEq.name, type: "light", duration_minutes: cfg.lightH * 60, kwh, cost });
      }

      // 환경 시뮬레이션
      let simTemp = curTemp;
      let simHum = curHum;
      if (cfg.fanMin > 0) {
        const factor = cfg.fanMin / 10.0;
        simTemp = simTemp > 22.0 ? Math.max(22.0, simTemp - (1.2 * factor)) : simTemp;
        simHum = simHum > 55.0 ? Math.max(55.0, simHum - (3.5 * factor)) : simHum;
      }
      if (cfg.heaterMin > 0) {
        const factor = cfg.heaterMin / 10.0;
        simTemp += 2.0 * factor;
        simHum = Math.max(30.0, simHum - (2.0 * factor));
      }
      if (cfg.lightH > 0) {
        simTemp += (cfg.lightH * 0.2);
      }

      simTemp = Math.round(simTemp * 10) / 10;
      simHum = Math.round(simHum * 10) / 10;

      // 기준 충족 여부 검사
      const issues = [];
      if (simTemp < cropStd.temp_min) issues.push(`기온 미달(${simTemp}℃ < ${cropStd.temp_min}℃)`);
      if (simTemp > cropStd.temp_max) issues.push(`온도 상한 초과(${simTemp}℃ > ${cropStd.temp_max}℃)`);
      if (simHum > cropStd.humidity_max) issues.push(`습도 과다(${simHum}% > ${cropStd.humidity_max}%)`);
      if (simHum < cropStd.humidity_min) issues.push(`습도 부족(${simHum}% < ${cropStd.humidity_min}%)`);
      if (neededLightHours > 0 && cfg.lightH < neededLightHours) {
        issues.push(`보광 부족(${(neededLightHours - cfg.lightH).toFixed(1)}시간 부족)`);
      }

      const meetsCriteria = issues.length === 0;
      const totalCost = Math.round(waterCost + totalElecCost);

      candidates.push({
        plan_id: "plan_" + Math.random().toString(36).substring(2, 9),
        zone_id: zone.zone_id,
        zone_name: zone.name,
        crop_type: zone.crop_type,
        created_at: nowStr,
        candidate_name: cfg.name,
        moisture_status: moistureStatus,
        last_watering_date: lastWaterText,
        recommended_water_liter: waterLiters,
        water_cost: waterCost,
        predicted_temp: simTemp,
        predicted_humidity: simHum,
        additional_light_hours: cfg.lightH,
        operations,
        total_kwh: Math.round(totalKwh * 1000) / 1000,
        electricity_cost: Math.round(totalElecCost),
        total_cost: totalCost,
        meets_criteria: meetsCriteria,
        unmet_issues: issues.length > 0 ? issues.join(", ") : "모든 생육 기준 충족",
        action_sequence: cfg.actionSeq
      });
    });

    // 최저비용 추천안 도출
    const validCandidates = candidates.filter(c => c.meets_criteria);
    let optimalPlan;
    if (validCandidates.length > 0) {
      optimalPlan = validCandidates.reduce((min, c) => c.total_cost < min.total_cost ? c : min, validCandidates[0]);
    } else {
      optimalPlan = candidates.reduce((min, c) => c.total_cost < min.total_cost ? c : min, candidates[0]);
    }

    return { optimalPlan, candidates };
  },

  savePlan(plan) {
    const plans = SmartFarmStore.getPlans();
    plans.push(plan);
    SmartFarmStore.savePlans(plans);
    return true;
  }
};

const HistoryService = {
  saveActualRecord(userId, zoneId, zoneName, cropType, dateStr, actualWaterLiter, lightHours, fanMinutes, heaterMinutes, measuredKwhInput, settings, associatedPlan = null) {
    const waterL = parseFloat(actualWaterLiter) || 0;
    const lightH = parseFloat(lightHours) || 0;
    const fanM = parseFloat(fanMinutes) || 0;
    const heaterM = parseFloat(heaterMinutes) || 0;

    let isEstimated = true;
    let totalKwh = 0.0;

    if (measuredKwhInput && measuredKwhInput.trim()) {
      const val = parseFloat(measuredKwhInput.trim());
      if (!isNaN(val) && val >= 0) {
        totalKwh = Math.round(val * 1000) / 1000;
        isEstimated = false;
      }
    }

    if (isEstimated) {
      const fanPower = (settings.equipments.find(e => e.equipment_type === "fan") || { power_watt: 75.0 }).power_watt;
      const lightPower = (settings.equipments.find(e => e.equipment_type === "light") || { power_watt: 120.0 }).power_watt;
      const heaterPower = (settings.equipments.find(e => e.equipment_type === "heater") || { power_watt: 1500.0 }).power_watt;

      const fanKwh = (fanPower * (fanM / 60.0)) / 1000.0;
      const lightKwh = (lightPower * lightH) / 1000.0;
      const heaterKwh = (heaterPower * (heaterM / 60.0)) / 1000.0;

      totalKwh = Math.round((fanKwh + lightKwh + heaterKwh) * 1000) / 1000;
    }

    const waterM3 = waterL / 1000.0;
    const waterCost = Math.round(waterM3 * settings.water_unit_price);
    const electricityCost = Math.round(totalKwh * settings.electricity_unit_price);
    const totalCost = waterCost + electricityCost;

    const history = {
      history_id: "hist_" + Math.random().toString(36).substring(2, 9),
      user_id: userId,
      zone_id: zoneId,
      zone_name: zoneName,
      crop_type: cropType,
      date: dateStr,
      actual_water_liter: waterL,
      light_duration_hours: lightH,
      fan_duration_minutes: fanM,
      heater_duration_minutes: heaterM,
      total_kwh: totalKwh,
      is_estimated_kwh: isEstimated,
      water_cost: waterCost,
      electricity_cost: electricityCost,
      total_cost: totalCost,
      plan_id: associatedPlan ? associatedPlan.plan_id : null,
      recommended_water_liter: associatedPlan ? associatedPlan.recommended_water_liter : 0.0,
      planned_total_cost: associatedPlan ? associatedPlan.total_cost : 0.0
    };

    const all = SmartFarmStore.getHistories();
    all.push(history);
    SmartFarmStore.saveHistories(all);

    // 실제 급수량 > 0 시 최근 급수일 자동 반영 (요구사항 32)
    if (waterL > 0) {
      ZoneService.updateLastWateringDate(zoneId, dateStr);
    }

    return { success: true, message: "실적 데이터가 성공적으로 저장되었습니다.", history };
  },

  filterHistories(userId, periodType = "all") {
    const all = SmartFarmStore.getHistories().filter(h => h.user_id === userId);
    const todayStr = new Date().toISOString().substring(0, 10);
    const now = new Date();

    const filtered = all.filter(h => {
      const hDate = new Date(h.date);
      if (periodType === "today") {
        return h.date === todayStr;
      } else if (periodType === "week") {
        const diffDays = (now - hDate) / (1000 * 60 * 60 * 24);
        return diffDays <= 7;
      } else if (periodType === "month") {
        const diffDays = (now - hDate) / (1000 * 60 * 60 * 24);
        return diffDays <= 30;
      }
      return true;
    });

    return filtered.sort((a, b) => b.date.localeCompare(a.date));
  },

  calculateStatistics(histories) {
    const totalWater = histories.reduce((sum, h) => sum + h.actual_water_liter, 0);
    const totalLightH = histories.reduce((sum, h) => sum + h.light_duration_hours, 0);
    const totalKwh = histories.reduce((sum, h) => sum + h.total_kwh, 0);
    const totalCost = histories.reduce((sum, h) => sum + h.total_cost, 0);

    return {
      count: histories.length,
      total_water_liter: Math.round(totalWater * 10) / 10,
      total_light_hours: Math.round(totalLightH * 10) / 10,
      total_kwh: Math.round(totalKwh * 100) / 100,
      total_cost: Math.round(totalCost)
    };
  }
};
