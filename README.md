# 🌿 스마트팜 운영비 절감 프로그램 (SmartFarm Cost Optimizer)
> **11주차 객체지향프로그래밍 팀프로젝트**  
> 온실 센서 환경 분석 기반 최적 관개(급수) 및 장비(환기·보광·난방) 에너지 비용 절감 시스템

---

## 🌐 1. 플랫폼 및 배포 안내 (2가지 실행 환경 지원)

본 프로젝트는 요구사항 1~38번의 모든 기능을 100% 동일하게 제공하면서 **2가지 방식**으로 자유롭게 실행 및 배포할 수 있습니다:

1. **순수 프론트엔드 웹 앱 (GitHub Pages 지원, 무설치 웹 접속)**
   - 백엔드 서버 없이 브라우저 자체(`localStorage`)로 영속화되는 반응형 웹 애플리케이션
   - `index.html` 파일을 더블 클릭하여 로컬에서 바로 열거나, GitHub Pages로 무료 호스팅 가능!
2. **Python 데스크톱 GUI 애플리케이션 (`main.py`)**
   - Python 표준 내장 라이브러리(`tkinter`)만 사용하여 추가 외부 패키지 설치 없이 `python main.py` 한 줄로 구동

---

## 🚀 2. GitHub Pages 호스팅 및 웹 실행 방법

### 방법 A. 로컬에서 바로 실행 (무설치)
- 탐색기에서 `index.html` 파일을 더블 클릭하여 크롬/엣지/사파리 등의 웹 브라우저로 바로 실행합니다.

### 방법 B. GitHub Pages에서 무료 웹 호스팅 (팀원 & 교수님 공유용)
1. 현재 프로젝트를 GitHub 저장소(`main` 브랜치)에 푸시합니다:
   ```bash
   git add .
   git commit -m "feat: complete smart farm cost optimizer web app"
   git push origin main
   ```
2. GitHub 저장소 페이지의 **Settings** → 좌측 **Pages** 메뉴로 이동합니다.
3. **Build and deployment** 항목에서:
   - **Source**: `Deploy from a branch` 선택
   - **Branch**: `main` / `/(root)` 선택 후 **Save** 클릭
4. 1~2분 후 생성되는 웹 URL(`https://<사용자이름>.github.io/<저장소이름>/`)로 접속하면 전 세계 어디서든 웹 브라우저로 바로 실행됩니다!

---

## 🐍 3. Python 데스크톱 앱 실행 방법

```powershell
python main.py
```
- 추가 `pip install`이 전혀 필요하지 않습니다.

---

## 👤 4. 테스트용 데모 계정 (빠른 체험)

- **아이디**: `farmer`
- **비밀번호**: `123`
- *첫 화면의 `⚡ 체험용 데모 계정으로 바로 시작` 버튼을 누르면 1초 만에 로그인되어 등록된 A구역(토마토), B구역(상추) 데이터를 바로 확인하실 수 있습니다.*

---

## 🏛 5. 객체지향 설계 (OOP Architecture)

본 프로그램은 **단일 책임 원칙(SRP)**, **관심사의 분리(Separation of Concerns)**, **다형성(Polymorphism)** 및 **계층형 아키텍처(Layered Architecture)**를 철저히 준수하여 설계되었습니다.

```
smartfarm/
│
├── index.html                  # [GitHub Pages] 무설치 순수 프론트엔드 웹 앱 메인
├── css/
│   └── style.css               # 모던 스마트팜 그린/슬레이트 반응형 웹 스타일시트
├── js/
│   ├── store.js                # localStorage 기반 데이터 영속화 & 데모 데이터 시딩
│   ├── services.js             # 계산 알고리즘 (관개량, 시뮬레이션, 최적화, 통계, 인증)
│   └── app.js                  # UI 컨트롤러, 네비게이션 라우터, 이벤트 핸들러
│
├── main.py                     # [Python GUI] 데스크톱 애플리케이션 엔트리포인트
│
├── models/                     # [Python 도메인 모델 계층 (Domain Entities)]
│   ├── user.py                 # User (사용자 계정)
│   ├── zone.py                 # Zone (재배 구역: 작물, 면적, 토양, 급수일)
│   ├── environment.py          # EnvironmentRecord (환경 센서 측정값)
│   ├── equipment.py            # Equipment (장비 추상 클래스 & 환기팬, 보광등, 난방기)
│   ├── crop_standard.py        # CropStandard (작물별 적정 생육 기준치)
│   ├── cost_plan.py            # CostPlan & EquipmentOperation (비용 계획 및 시뮬레이션)
│   ├── usage_history.py        # UsageHistory (작업 실적 및 통계 이력)
│   └── settings.py             # SystemSettings (물·전기 단가 설정)
│
├── services/                   # [Python 비즈니스 로직 계층 (Service Layer)]
│   ├── storage_service.py      # JSON 파일 영속성 및 기본값 시딩 관리
│   ├── auth_service.py         # 회원가입, 로그인 검증, 사용자 세션 관리
│   ├── zone_service.py         # 구역 등록, 수정, 삭제, 최근 급수일 갱신
│   ├── environment_service.py  # 측정값 유효성 검사 및 직전 대비 변화량 분석
│   ├── optimization_service.py # 관개량 계산, 후보 시뮬레이션, 최저비용 추천 엔진
│   └── history_service.py      # 실적 기록, 기간별 집계 통계, 계획 vs 실적 비교
│
└── ui/                         # [Python Tkinter Presentation Layer]
    ├── styles.py               # 전역 컬러 팔레트, 폰트, ttk 위젯 스타일
    ├── components/             # 커스텀 컴포넌트 (nav_bar, stat_card)
    └── views/                  # 화면별 View (auth, home, env, plan, history, settings)
```

---

## 📋 6. 요구사항 (자연어 구성 1~38) 완벽 반영 매핑

| 영역 | 항목 번호 | 세부 구현 내용 | 웹(JS) 구현 | 파이썬 구현 |
|:---|:---:|:---|:---|:---|
| **A. 시작, 가입 & 로그인** | 1 | 첫 화면에서 안내 문구와 [회원가입], [로그인] 선택 | `App.showAuthBox('welcome')` | `AuthView.show_welcome()` |
| | 2 | 회원가입 시 아이디, 비밀번호, 비밀번호 확인 입력 | `authRegisterBox` | `AuthView.show_register()` |
| | 3 | 아이디 중복, 공백, 비밀번호 불일치 유효성 검사 및 안내 | `AuthService.register()` | `AuthService.register()` |
| | 4 | 가입 성공 메시지 표시 후 로그인 화면으로 자동 전환 | `App.bindEvents (register submit)` | `AuthView._handle_register()` |
| | 5 | 로그인 화면에서 아이디/비밀번호 입력 | `authLoginBox` | `AuthView.show_login()` |
| | 6 | 계정 검증 및 구역/측정/급수 기록 세션 로드 | `AuthService.login()` | `AuthService.login()` |
| | 7 | 등록 구역 없는 신규 사용자는 최초 1회 구역 등록 다이얼로그 표시 | `App.showInitialZoneModal()` | `AuthView._show_initial_zone_modal()` |
| | 8 | Home 화면에 프로그램 이름, 구역 목록, 3대 메뉴 및 시스템 버튼 표시 | `App.renderHomeView()` | `HomeView`, `TopNavBar` |
| **B. 메뉴 1: 구역별 환경 입력** | 9 | 구역 선택 시 작물 종류, 재배면적, 토양 종류 자동 표시 | `App.onEnvZoneSelected()` | `EnvInputView._on_zone_selected()` |
| | 10 | 최근 실제 급수일 자동 로드 및 직접 수정 입력 지원 | `envLastWaterDate` | `EnvInputView.ent_last_water` |
| | 11 | 측정 일시, 토양수분(%), 기온(℃), 습도(%RH), 조도(lx) 입력 | `formEnvInput` | `EnvInputView._build_ui()` |
| | 12 | 입력값 숫자 검사, 0~100% 범위 검사, 미래 급수일 방지 검사 | `EnvironmentService.recordEnvironment()` | `EnvironmentRecord.validate_inputs()` |
| | 13 | 저장 및 직전 기록과의 변화량(예: 26% → 22%) 실시간 비교 표시 | `res.changeSummary` | `EnvironmentService.record_environment()` |
| | 14 | 다른 구역 연속 입력 및 [운영 계획 보기] 바로가기 연계 | `App.navigateTo('plan')` | `EnvInputView.plan_cta` |
| **C. 메뉴 2: 저비용 운영 계획** | 15 | [계획 계산] 시 최신 측정값, 기준치, 장비 소비전력, 유틸리티 단가 로드 | `OptimizationService.calculatePlanForZone()` | `OptimizationService.calculate_plan_for_zone()` |
| | 16 | 토양 수분 vs 기준 비교: '급수 필요' / '급수 보류' 및 최근 급수일 표시 | `moistureStatus` | `CropStandard.evaluate_moisture()` |
| | 17 | 관개요구량(mm) × 면적(m²) = 권장 급수량(L) 자동 계산 | `waterLiters` | `CropStandard.calculate_water_liters()` |
| | 18 | 구역별 권장 급수량 표 표시 및 전체 합산 집계 | `App.renderWaterSummaryTable()` | `PlanView._populate_all_zones_summary()` |
| | 19 | 기온·습도 적정 범위 비교 ('낮음' / '적정' / '높음') | `simTemp, simHum vs std` | `CropStandard.evaluate_temperature()` |
| | 20, 21 | 조도 비교 및 누적 일조 부족 시간 산출 안내 | `neededLightHours` | `OptimizationService.calculate_plan_for_zone()` |
| | 22 | 장비 가동 후보군(최소 가동, 표준 10분, 집중 20분 등) 시뮬레이션 | `candidateConfigs` | `OptimizationService.candidates` |
| | 23 | 예상 온습도 및 작업 순서 안내 ('환기 10분 → 기온 재확인 → 보광') | `actionSeq` | `CostPlan.action_sequence` |
| | 24 | 장비별 소비전력(W) × 가동시간(h) = 예상 전력량(kWh) | `totalKwh` | `Equipment.calculate_kwh()` |
| | 25 | 물 비용(m³×단가) + 전기 비용(kWh×단가) = 총 예상 운영비 | `totalCost` | `CostPlan.total_cost` |
| | 26 | 재배환경 기준 충족 후보 중 **최저 비용 계획** 자동 판정 및 추천 | `optimalPlan` | `OptimizationService.min(valid, key=cost)` |
| | 27 | 급수 권장량, 가동 시간, 예상 온습도, 전력량, 항목별 비용 결과 카드 | `App.renderOptimalPlanCard()` | `PlanView._render_optimal_plan()` |
| | 28 | [후보 비교] 상세 테이블 제공 및 [계획 저장] | `App.renderCandidatesTable()` | `PlanView._save_current_plan()` |
| **D. 메뉴 3: 사용량·비용 이력** | 29 | 작업 후 저장된 운영 계획 불러오기 연동 | `App.onHistPlanSelected()` | `HistoryView._on_plan_selected()` |
| | 30 | 실제 급수량, 장비별 가동 시간, 직접 실측 전력량 입력 | `formHistory` | `HistoryView._build_ui()` |
| | 31 | 실측값 없을 시 소비전력 기준 전력량 추정 및 '(추정)' 표시 | `isEstimated` | `UsageHistory.is_estimated_kwh` |
| | 32 | [실적 저장] 및 실제 급수량 > 0 시 최근 급수일 자동 갱신 | `HistoryService.saveActualRecord()` | `HistoryService.save_actual_record()` |
| | 33 | 조회 기간 필터 (오늘, 7일, 30일, 전체) 및 구역/작물 필터 | `HistoryService.filterHistories()` | `HistoryService.filter_histories()` |
| | 34 | 기간별 총 물 사용량, 보광 시간, 전력량, 물·전기·총비용 집계 | `HistoryService.calculateStatistics()` | `HistoryService.calculate_statistics()` |
| | 35 | 계획 대비 실제 작업량 및 비용 차이 비교 (권장 vs 실제) | `tableHistories` | `HistoryView.tree_history` |
| **E. 설정, 로그아웃 & 종료** | 36 | 구역 수정/추가/삭제, 작물 기준, 장비 소비전력, 물·전기 단가 설정 | `App.renderSettingsView()` | `SettingsView` |
| | 37 | [홈] 누르면 이동, [로그아웃] 시 확인 후 첫 화면 복귀 | `App.navigateTo('home')`, `btnLogout` | `SmartFarmApplication.on_logout()` |
| | 38 | [종료] 시 미저장 확인 대화상자 후 안전 종료 | `window.confirm` | `SmartFarmApplication.on_exit()` |
