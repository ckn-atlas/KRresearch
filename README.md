# 🇰🇷 KR Research Atlas

**한국 대학 연구자 성과 지도** — 국내 대학별 연구자의 논문 성과, 연구 분야, 소속 이력을 한눈에 분석하는 오픈 데이터 플랫폼

🌐 **라이브 사이트:** https://krresearch.pages.dev

---

## 주요 기능

- 🏫 **370개 한국 대학** 연구 현황 집계 (논문 수 · 피인용 수 · h-index · FWCI)
- 🔬 **연구자 프로필** — 전체 커리어 기반 연구 분야 분석 (이직 전 논문 포함)
- 📈 **연구 트렌드** — 전체 커리어 vs 최근 3년 연구 주제 변화 비교
- 🔄 **소속 이력 추적** — OpenAlex Author ID 기반 이직·퇴직 감지
- 🔍 **통합 검색** — 대학명·연구자명·연구분야 실시간 필터링
- 📱 **모바일 지원** — 반응형 레이아웃

## 데이터 소스

| 소스 | 내용 |
|---|---|
| [OpenAlex](https://openalex.org) | 대학·연구자·논문 데이터 (무료 오픈API) |
| [KCI](https://www.kci.go.kr) | 국내 KCI 등재 논문 (한국연구재단) |
| [NTIS](https://www.ntis.go.kr) | 국가 R&D 과제 정보 (추가 예정) |

## 기술 스택

- **Frontend** — Vanilla JS, CSS Grid (의존성 없음)
- **Data** — Python (httpx, OpenAlex API)
- **Hosting** — Cloudflare Pages

## 로컬 실행

```bash
# 패키지 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일에 이메일 입력 (OpenAlex polite pool용)

# 데이터 수집
python scripts/collect_universities.py
python scripts/collect_authors.py
python scripts/build_data.py

# 로컬 서버
python -m http.server 8765
# → http://localhost:8765
```

## 프로젝트 구조

```
├── index.html                  # 프론트엔드 (단일 파일)
├── data/
│   ├── universities.json       # 대학 목록 + 집계
│   └── authors.json            # 연구자 + 연구 프로필
└── scripts/
    ├── collect_universities.py # 대학 수집 (OpenAlex)
    ├── collect_authors.py      # 연구자 수집 (OpenAlex)
    └── build_data.py           # JSON 생성
```

## 업데이트 주기

데이터는 월 1회 갱신됩니다.

---

> 데이터 출처: [OpenAlex](https://openalex.org) · [KCI](https://www.kci.go.kr) · [NTIS](https://www.ntis.go.kr)  
> 문의: cknatlas48@gmail.com
