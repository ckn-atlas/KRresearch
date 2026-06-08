"""NTIS 과제검색 - 올바른 검색 파라미터 찾기"""
import httpx
import re

KEY = "53fp665x1847viai1w45"
EP = "https://www.ntis.go.kr/rndopen/openApi/public_project"

def hits(text):
    m = re.search(r"<TOTALHITS>(\d+)</TOTALHITS>", text)
    return m.group(1) if m else "?"

# 검색어 파라미터 후보
variants = [
    {"apprvKey": KEY, "query": "건설", "collection": "project"},
    {"apprvKey": KEY, "searchKeyword": "건설", "collection": "project"},
    {"apprvKey": KEY, "SRWR": "건설", "collection": "project"},
    {"apprvKey": KEY, "PJT": "건설"},
    {"apprvKey": KEY, "query": "건설"},
    {"apprvKey": KEY, "search": "건설"},
    # 검색어 없이 전체
    {"apprvKey": KEY, "collection": "project", "displayCnt": 2},
    {"apprvKey": KEY, "displayCnt": 2},
]

with httpx.Client(timeout=20, follow_redirects=True) as c:
    for p in variants:
        try:
            r = c.get(EP, params=p)
            h = hits(r.text)
            keys = [k for k in p if k != "apprvKey"]
            print(f"hits={h:>6} | {keys}")
            if h not in ("0", "?"):
                open("data/_raw/ntis_sample.xml","w",encoding="utf-8").write(r.text)
                print(f"  *** SAVED (params={p}) ***")
        except Exception as e:
            print(f"ERR {list(p.keys())}: {e}")
