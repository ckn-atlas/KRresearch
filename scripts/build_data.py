"""
캐시된 대학별 연구자 데이터 → data/authors.json 생성
수집 완료 후 실행

실행: python scripts/build_data.py
"""

import json
from datetime import datetime
from pathlib import Path

CACHE_DIR = Path("data/_raw/authors")
UNI_FILE  = Path("data/universities.json")
OUT_FILE  = Path("data/authors.json")


def main():
    # 캐시 파일 로드
    cache_files = sorted(CACHE_DIR.glob("*.json"))
    print(f"캐시 파일: {len(cache_files)}개")

    all_authors: list[dict] = []
    for f in cache_files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            all_authors.extend(data)
        except Exception as e:
            print(f"  skip {f.name}: {e}")

    # 피인용 기준 정렬
    all_authors.sort(key=lambda a: a.get("cited_by_count", 0), reverse=True)

    # 상태 요약
    statuses = [a["status"] for a in all_authors]
    print(f"총 연구자: {len(all_authors)}명")
    print(f"  active  : {statuses.count('active')}")
    print(f"  moved   : {statuses.count('moved')}")
    print(f"  inactive: {statuses.count('inactive')}")

    # universities.json updated 날짜 갱신
    if UNI_FILE.exists():
        uni_data = json.loads(UNI_FILE.read_text(encoding="utf-8"))
        uni_data["updated"] = datetime.now().strftime("%Y-%m-%d")
        UNI_FILE.write_text(json.dumps(uni_data, ensure_ascii=False, indent=2), encoding="utf-8")

    # authors.json 저장
    out = {
        "updated": datetime.now().strftime("%Y-%m-%d"),
        "count": len(all_authors),
        "authors": all_authors,
    }
    OUT_FILE.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    size_mb = OUT_FILE.stat().st_size / 1024 / 1024
    print(f"\n저장 완료: {OUT_FILE} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
