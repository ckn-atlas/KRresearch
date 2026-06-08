# KR Research Atlas — 작업 노트

## 프로젝트 개요
한국 국가 R&D **과제 중심** 성과 파생 및 유지관리 분석 플랫폼.

**경로:** `D:\0_PycharmProject\pythonProject\029_KR_ResearchAtlas`
**GitHub:** https://github.com/ckn-atlas/KRresearch
**배포 예정:** Cloudflare Pages (krresearch.pages.dev)

> ⚠️ 방향 전환 (2026-06-05): "연구자 중심" → **"과제 중심"**으로 피벗.
> 이유: OpenAlex 영문명 동명이인 과병합(중국인 혼입) 문제. 국가연구자번호는
> 공개 API 미제공. 과제(NTIS)는 집계 단위라 동명이인 무관 + 한글명 확보 가능.

---

## 핵심 컨셉: 과제 → 성과 파생 → 유지관리

```
        NTIS 과제검색 (public_project)  ★ProjectNumber = 중심키
                 │
    ┌────────────┼────────────┬──────────────┐
    ▼            ▼            ▼              ▼
 rpaper       rpatent      requip      KCI(NRF_YN)
 논문성과      특허성과     연구장비      국내논문
                 │
                 ▼ (특허번호)
            KIPRIS → 유지관리 추적
            (생존율/피인용/패밀리/권리자변동)
```

분석 축:
1. **파생(산출):** 과제당 논문·특허 밀도, 대학별 생산성, 분야별 성과유형
2. **유지관리(확산):** 특허 생존율, 피인용, 해외패밀리, 기술이전(권리자변동)
3. **생애주기:** 과제종료→성과발생 시차, 특허 생존곡선, 장기영향력

---

## API 현황 (2026-06-05)

### ✅ 작동 확인
| API | 엔드포인트 | 인증/검색 |
|---|---|---|
| NTIS 과제검색 | `https://www.ntis.go.kr/rndopen/openApi/public_project` | apprvKey / query+searchFd |
| KCI 논문/저자/학술지 | `https://apis.data.go.kr/B552540/KCIOpenApi/artiInfo/...` | serviceKey |

### ⏳ 승인 대기 (1~3일)
| API | 소스 | 비고 |
|---|---|---|
| NTIS 성과검색 | public_result | rpaper/rpatent/requip, ProjectID 연결 |
| NTIS 수행기관 현황조회 | - | 대학별 집계 |
| NTIS 위탁/공동연구(기관용) | - | 개인 승인 불확실 |
| KIPRIS 특허 8종 | plus.kipris.or.kr | 월 1,000건 한도 |

### 인증키 (.env 에 저장, GitHub X)
- NTIS 통합인증키: 과제검색 승인됨 (성과검색 승인 시 동일키 사용 추정)
- data.go.kr 키: KCI 공통
- KIPRIS: 승인 후 발급

---

## 검증된 NTIS 과제검색 사용법

```
GET https://www.ntis.go.kr/rndopen/openApi/public_project
  apprvKey={KEY}
  collection=project
  query={검색어}
  searchFd={필드코드}   # 생략시 전체(BI)
  displayCnt=100        # 최대 100
  startPosition=1       # 페이징 (깊은 페이지 OK)
```

### 검색 필드 코드
| 코드 | 의미 | 코드 | 의미 |
|---|---|---|---|
| BI | 전체(기본) | CN | 과제고유번호 |
| TI | 과제명 | PY | 연구년도 |
| AU | 연구책임자명 | KW | 키워드 |
| OG | 수행기관명 | AB | 초록 |
| PB | 부처/전문기관 | | |

연산자: AND(공백) / OR(`\|`) / NOT(`!`) / 구문(`"..."`)

### 과제 응답 주요 필드
ProjectNumber(과제번호), ProjectTitle, Manager.Name(연구책임자),
ResearchAgency.Name(수행기관), GovernmentFunds/TotalFunds(연구비),
ProjectYear, ProjectPeriod, Ministry, OrderAgency, Keyword, Abstract,
Goal, Effect, ScienceClass(분류), SixTechnology(6T), DevelopmentPhases,
PerformAgent(대학/기업/출연연), ManCount/WomanCount(연구인력)

### NAVIGATION (집계 내장)
검색결과에 기관별/연도별/부처별/분야별 COUNT가 자동 집계되어 옴
→ 대학별 과제수 등은 별도 계산 없이 추출 가능

### 수집 전략
- 연도별(PY) 전수 수집이 가장 확실 (연 ~1.8만건, 2002~2026)
- OG(기관) 직접검색은 매칭 부정확 → 수집후 ResearchAgency로 그룹핑
- displayCnt=100 × startPosition 페이징

### 검증된 규모
- "건설" 전체: 68,936건
- PY=2024: 18,785건
- 인공지능 KW: 35,938건

---

## NTIS 성과검색 (승인 후 사용 예정)
```
GET https://www.ntis.go.kr/rndopen/openApi/public_result
  collection=rpaper | rpatent | requip
  query={검색어}
  searchFd=PI 등
```
성과 응답에 **ProjectID** 포함 → 과제↔성과 직접 연결 가능
- rpaper(논문) "나노" 샘플: 107,821건 확인됨

---

## KIPRIS 신청 8종 (특허 유지관리)
1. 특허·실용 공개·등록공보 — 서지(과제번호 포함)
2. 특허·실용 행정처리 이력 — 출원→등록 전환율 (M6a)
3. 법적 상태 이력(ST.27) — 특허 생존율 (M12c)
4. 한국특허영문초록(KPA) — 특허내용
5. 기계번역용 국문초록 — 특허내용
6. 특허·실용 피인용문헌 — 피인용수 (M6b)
7. 특허 패밀리 — 해외확장 (M6c)
8. 권리자 변동 이력 — 기술이전 (M12a)

⚠️ 월 1,000건 한도 → 특허 1건당 ~6회 조회 → 월 ~160개 추적 가능
→ 전수 불가, 대표 과제 중심 심층추적

---

## 폴더 구조 / 배포 규칙

```
029_KR_ResearchAtlas/
├── index.html              ← GitHub O
├── data/
│   ├── universities.json   ← GitHub O (370개 대학 + 한국명 175개)
│   ├── authors.json        ← (구버전, 연구자중심, 65MB) 재검토 필요
│   ├── _raw/               ← GitHub X
│   └── _cache/             ← GitHub X
├── scripts/                ← GitHub O
│   ├── collect_universities.py
│   ├── ko_names.py         ← 영문→한글 대학명 매핑
│   ├── test_ntis*.py       ← NTIS API 테스트
│   └── ...
├── .env                    ← GitHub X (API 키)
└── .env.example            ← GitHub O
```

---

## 다음 단계

### 즉시 가능 (과제검색 작동 중)
1. NTIS 과제 연도별 전수 수집 스크립트 작성
2. ResearchAgency로 대학 그룹핑 + 한글명 매핑
3. 과제 중심 index.html 재설계 (현황/대학별/분야/검색)

### API 승인 후
4. 성과검색으로 과제↔논문/특허 연결
5. KIPRIS로 대표과제 특허 유지관리 추적

### 미해결 / 재검토
- 기존 authors.json(연구자중심, OpenAlex) 활용 여부 — 과제중심 피벗으로 보조자료화
- OpenAlex는 국제논문 피인용 추이 보조용으로만

---

## 참고: 기존 자료 위치
- NTIS 매뉴얼: `D:\...\022_NTIS_SmartConstruction_Monitor\`
  - `01.통합OpenAPI_국가R&D 과제검색(전체용)_매뉴얼_2025.pdf`
  - `05. 통합OpenAPI_국가R&D 성과검색(전체용)_매뉴얼_2024.pdf`
  - KIPRIS 가이드, M1~M12 지표체계 docs/
