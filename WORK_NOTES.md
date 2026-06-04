# KR Research Atlas — 작업 노트

## 프로젝트 개요
한국 대학 연구자의 국가과제 수행 현황 및 연구 성과 분석 플랫폼.

**경로:** `D:\0_PycharmProject\pythonProject\029_KR_ResearchAtlas`

---

## GitHub / 배포

| 항목 | 업로드 |
|---|---|
| index.html, scripts/, data/*.json | ✅ O |
| .env (API 키) | ❌ X |
| data/_raw/, data/_cache/ | ❌ X |
| .env.example | ✅ O (키 없는 템플릿) |

---

## 데이터 소스

| 소스 | 내용 | 상태 |
|---|---|---|
| OpenAlex API | 대학별 연구자 논문·피인용 성과 | 즉시 사용 가능 |
| NTIS API | 국가과제 + 연구자 참여 정보 | 키 발급 필요 |

---

## 폴더 구조

```
029_KR_ResearchAtlas/
├── index.html
├── requirements.txt
├── .env.example
├── .gitignore
├── WORK_NOTES.md
├── scripts/
│   ├── collect_universities.py   — 한국 대학 목록 (OpenAlex)
│   ├── collect_authors.py        — 대학별 연구자
│   ├── collect_works.py          — 연구자별 논문
│   ├── collect_ntis.py           — NTIS 국가과제 (2단계)
│   └── build_data.py             — data/*.json 생성
└── data/
    ├── universities.json          ← GitHub O
    ├── authors.json               ← GitHub O
    ├── works.json                 ← GitHub O
    ├── _raw/                      ← GitHub X (API 원시 응답)
    └── _cache/                    ← GitHub X (중간 캐시)
```

---

## 단계별 계획

### 1단계 (OpenAlex, 현재)
1. `collect_universities.py` — 한국 대학 목록 수집 (ROR 기반)
2. `collect_authors.py` — 대학별 상위 연구자 수집
3. `collect_works.py` — 연구자별 논문 수집
4. `build_data.py` — 집계 JSON 생성
5. `index.html` — 시각화 프론트엔드

### 2단계 (NTIS 키 발급 후)
- `collect_ntis.py` — 과제 수집 + 연구자 이름 매칭
- 과제-논문 연결 로직 추가
- 프론트엔드 과제 탭 추가

---

## 실행 방법

```powershell
# 환경 설정
copy .env.example .env
# .env 파일에 이메일 등 입력

# 패키지 설치
pip install -r requirements.txt

# 데이터 수집 (순서 중요)
python scripts/collect_universities.py
python scripts/collect_authors.py
python scripts/collect_works.py
python scripts/build_data.py

# 로컬 서버
python -m http.server 8765
```

---

## NTIS API 신청
- 신청: https://www.ntis.go.kr/apim/
- 소요: 1~3일
- 필요 API: 과제검색, 성과검색
