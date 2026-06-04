"""
한국 대학 목록 수집 (OpenAlex)
저장: data/_raw/universities_raw.json  (GitHub X)
      data/universities.json           (GitHub O)
"""

import json
import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.openalex.org"
EMAIL = os.getenv("OPENALEX_EMAIL", "")
HEADERS = {"User-Agent": f"KRResearchAtlas/1.0 (mailto:{EMAIL})" if EMAIL else "KRResearchAtlas/1.0"}

RAW_DIR = Path("data/_raw")
OUT_DIR = Path("data")
RAW_FILE = RAW_DIR / "universities_raw.json"
OUT_FILE = OUT_DIR / "universities.json"


def fetch_all_kr_universities() -> list[dict]:
    """OpenAlex에서 한국 대학 전체 수집 (페이지네이션)."""
    results = []
    cursor = "*"
    page = 1

    with httpx.Client(headers=HEADERS, timeout=30) as client:
        while True:
            params = {
                "filter": "country_code:KR,type:education",
                "per_page": 200,
                "cursor": cursor,
                "select": (
                    "id,display_name,display_name_alternatives,"
                    "ror,country_code,type,"
                    "works_count,cited_by_count,"
                    "summary_stats,x_concepts"
                ),
            }
            resp = client.get(f"{BASE_URL}/institutions", params=params)
            resp.raise_for_status()
            data = resp.json()

            items = data.get("results", [])
            results.extend(items)

            meta = data.get("meta", {})
            next_cursor = meta.get("next_cursor")
            total = meta.get("count", 0)

            print(f"  페이지 {page}: {len(items)}개 수집 (누계 {len(results)}/{total})")

            if not next_cursor or not items:
                break

            cursor = next_cursor
            page += 1
            time.sleep(0.1)

    return results


def extract_top_concepts(x_concepts: list, top_n: int = 5) -> list[dict]:
    sorted_c = sorted(x_concepts, key=lambda c: c.get("score", 0), reverse=True)
    return [
        {"name": c["display_name"], "score": round(c["score"], 1)}
        for c in sorted_c[:top_n]
    ]


def build_university_record(raw: dict) -> dict:
    stats = raw.get("summary_stats") or {}
    return {
        "id": raw["id"].split("/")[-1],          # OpenAlex ID (I로 시작)
        "name": raw["display_name"],
        "name_alt": raw.get("display_name_alternatives", []),
        "ror": raw.get("ror", ""),
        "works_count": raw.get("works_count", 0),
        "cited_by_count": raw.get("cited_by_count", 0),
        "h_index": stats.get("h_index", 0),
        "i10_index": stats.get("i10_index", 0),
        "fwci": round(stats.get("2yr_mean_citedness", 0), 3),
        "top_concepts": extract_top_concepts(raw.get("x_concepts") or []),
    }


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=== 한국 대학 수집 시작 (OpenAlex) ===")
    raw_list = fetch_all_kr_universities()

    # 원시 데이터 저장 (GitHub X)
    RAW_FILE.write_text(json.dumps(raw_list, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"원시 데이터 저장: {RAW_FILE} ({len(raw_list)}개)")

    # 가공 데이터 생성
    universities = [build_university_record(r) for r in raw_list]

    # works_count 기준 내림차순
    universities.sort(key=lambda u: u["works_count"], reverse=True)

    out = {
        "updated": "",           # build_data.py에서 채움
        "count": len(universities),
        "universities": universities,
    }
    OUT_FILE.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"가공 데이터 저장: {OUT_FILE} ({len(universities)}개)")
    print("\n상위 10개 대학:")
    for i, u in enumerate(universities[:10], 1):
        print(f"  {i:2d}. {u['name']} | works={u['works_count']:,} cited={u['cited_by_count']:,}")


if __name__ == "__main__":
    main()
