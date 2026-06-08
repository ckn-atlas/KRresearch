"""
대학별 연구자 수집 + 연구 프로필 생성 (OpenAlex)

전략:
- last_known_institution 기준으로 현재 소속 대학에 귀속
- 연구 프로필은 전체 커리어 논문 기반 (이직 전 포함)
- 효율을 위해 Author 객체의 x_concepts 활용 (전체 이력 기반 pre-computed)
- 최근 트렌드는 최근 3년 논문 별도 조회

저장:
  data/_raw/authors/          ← GitHub X
  data/authors.json           ← GitHub O
"""

import json
import os
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.openalex.org"
EMAIL = os.getenv("OPENALEX_EMAIL", "")
HEADERS = {"User-Agent": f"KRResearchAtlas/1.0 (mailto:{EMAIL})" if EMAIL else "KRResearchAtlas/1.0"}

RAW_DIR = Path("data/_raw/authors")
OUT_FILE = Path("data/authors.json")
UNI_FILE = Path("data/universities.json")

# 대학당 수집할 최대 연구자 수 (cited_by_count 상위)
MAX_AUTHORS_PER_UNI = 50
# 최근 활동 기준 연도 (이 연도 이후 논문이 없으면 inactive)
ACTIVE_SINCE = 2022
# 수집 대상 최소 논문 수
MIN_WORKS = 5


def _get_with_retry(client: httpx.Client, url: str, params: dict, max_retry: int = 5) -> dict:
    """429 발생 시 exponential backoff 재시도."""
    for attempt in range(max_retry):
        resp = client.get(url, params=params)
        if resp.status_code == 429:
            wait = 60 * (attempt + 1)
            print(f"  429 rate limit — {wait}초 대기 후 재시도...")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()
    raise Exception("최대 재시도 횟수 초과")


def fetch_authors_for_institution(inst_id: str, client: httpx.Client) -> list[dict]:
    """특정 기관 소속 연구자 목록 수집."""
    params = {
        "filter": f"last_known_institutions.id:{inst_id},works_count:>{MIN_WORKS}",
        "sort": "cited_by_count:desc",
        "per_page": MAX_AUTHORS_PER_UNI,
        "select": (
            "id,display_name,display_name_alternatives,"
            "works_count,cited_by_count,summary_stats,"
            "last_known_institutions,affiliations,x_concepts,"
            "counts_by_year"
        ),
    }
    return _get_with_retry(client, f"{BASE_URL}/authors", params).get("results", [])


def fetch_recent_concepts(author_id: str, client: httpx.Client) -> list[dict]:
    """최근 3년 논문 기반 개념 추출 (트렌드 파악용)."""
    params = {
        "filter": f"author.id:{author_id},publication_year:>{ACTIVE_SINCE - 1}",
        "per_page": 50,
        "select": "concepts,publication_year",
    }
    works = _get_with_retry(client, f"{BASE_URL}/works", params).get("results", [])

    # 개념 빈도 집계
    concept_score: dict[str, float] = {}
    for w in works:
        for c in w.get("concepts") or []:
            name = c["display_name"]
            concept_score[name] = concept_score.get(name, 0) + c.get("score", 0)

    sorted_c = sorted(concept_score.items(), key=lambda x: x[1], reverse=True)
    return [{"name": n, "score": round(s, 1)} for n, s in sorted_c[:8]]


def determine_status(author: dict, inst_id: str) -> str:
    """연구자 현재 상태 판별."""
    counts = {c["year"]: c["works_count"] for c in (author.get("counts_by_year") or [])}
    recent_active = any(counts.get(y, 0) > 0 for y in range(ACTIVE_SINCE, 2026))

    last_insts = [i["id"] for i in (author.get("last_known_institutions") or [])]
    at_current = any(inst_id in lid for lid in last_insts)

    if not recent_active:
        return "inactive"
    if not at_current:
        return "moved"
    return "active"


def extract_affiliation_history(affiliations: list) -> list[dict]:
    """소속 이력 정리."""
    history = []
    for aff in (affiliations or []):
        inst = aff.get("institution") or {}
        years = aff.get("years") or []
        if inst.get("display_name"):
            history.append({
                "institution": inst["display_name"],
                "institution_id": inst.get("id", "").split("/")[-1],
                "years": sorted(years),
            })
    return sorted(history, key=lambda x: min(x["years"]) if x["years"] else 0)


def extract_top_concepts(x_concepts: list, top_n: int = 10) -> list[dict]:
    """전체 커리어 연구 개념 추출."""
    sorted_c = sorted(x_concepts or [], key=lambda c: c.get("score", 0), reverse=True)
    return [{"name": c["display_name"], "score": round(c["score"], 1)} for c in sorted_c[:top_n]]


def build_author_record(raw: dict, inst_id: str, inst_name: str, recent_concepts: list) -> dict:
    stats = raw.get("summary_stats") or {}
    counts = raw.get("counts_by_year") or []

    # 최근 5년 논문수 추이
    yearly = {c["year"]: c["works_count"] for c in counts}
    recent_yearly = {y: yearly.get(y, 0) for y in range(2020, 2026)}

    return {
        "id": raw["id"].split("/")[-1],
        "name": raw["display_name"],
        "name_alt": raw.get("display_name_alternatives") or [],
        "institution_id": inst_id,
        "institution_name": inst_name,
        "status": determine_status(raw, inst_id),
        "works_count": raw.get("works_count", 0),
        "cited_by_count": raw.get("cited_by_count", 0),
        "h_index": stats.get("h_index", 0),
        "i10_index": stats.get("i10_index", 0),
        "fwci": round(stats.get("2yr_mean_citedness", 0), 3),
        "research_profile": {
            "all_time": extract_top_concepts(raw.get("x_concepts")),
            "recent": recent_concepts,
        },
        "affiliation_history": extract_affiliation_history(raw.get("affiliations")),
        "yearly_works": recent_yearly,
    }


def load_cache(inst_id: str) -> list | None:
    path = RAW_DIR / f"{inst_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def save_cache(inst_id: str, data: list):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{inst_id}.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def main():
    unis_data = json.loads(UNI_FILE.read_text(encoding="utf-8"))
    universities = unis_data["universities"]
    print(f"대상 대학: {len(universities)}개")

    all_authors: list[dict] = []

    with httpx.Client(headers=HEADERS, timeout=30) as client:
        for idx, uni in enumerate(universities):
            inst_id = uni["id"]
            inst_name = uni["name"]

            # 캐시 확인 (재실행 시 이미 수집한 대학 스킵)
            cached = load_cache(inst_id)
            if cached is not None:
                all_authors.extend(cached)
                print(f"[{idx+1}/{len(universities)}] {inst_name} |캐시 ({len(cached)}명)")
                continue

            try:
                raw_authors = fetch_authors_for_institution(inst_id, client)
                time.sleep(0.15)

                processed = []
                for author in raw_authors:
                    author_id = author["id"].split("/")[-1]
                    recent = fetch_recent_concepts(author_id, client)
                    time.sleep(0.1)

                    record = build_author_record(author, inst_id, inst_name, recent)
                    processed.append(record)

                save_cache(inst_id, processed)
                all_authors.extend(processed)

                active = sum(1 for a in processed if a["status"] == "active")
                moved = sum(1 for a in processed if a["status"] == "moved")
                print(f"[{idx+1}/{len(universities)}] {inst_name} | {len(processed)} (active={active}, moved={moved})")

            except Exception as e:
                print(f"[{idx+1}] {inst_name} 오류: {e}")
                time.sleep(1)

    # 최종 저장
    out = {
        "updated": "",
        "count": len(all_authors),
        "authors": all_authors,
    }
    OUT_FILE.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n완료: {len(all_authors)}명 저장 -> {OUT_FILE}")

    # 상태 요약
    statuses = [a["status"] for a in all_authors]
    print(f"  active : {statuses.count('active')}")
    print(f"  moved  : {statuses.count('moved')}")
    print(f"  inactive: {statuses.count('inactive')}")


if __name__ == "__main__":
    main()
