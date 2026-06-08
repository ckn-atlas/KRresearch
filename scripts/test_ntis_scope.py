"""전체 수집 규모 파악"""
import httpx, re, time

KEY = "53fp665x1847viai1w45"
EP = "https://www.ntis.go.kr/rndopen/openApi/public_project"

def total(text):
    m = re.search(r"<TOTALHITS>(\d+)</TOTALHITS>", text)
    return int(m.group(1)) if m else -1

with httpx.Client(timeout=20, follow_redirects=True) as c:
    tests = [
        ("연도 PY=2024", {"query":"2024","searchFd":"PY","collection":"project","displayCnt":1}),
        ("서울대 OG", {"query":"서울대학교","searchFd":"OG","collection":"project","displayCnt":1}),
        ("경북대 OG", {"query":"경북대학교","searchFd":"OG","collection":"project","displayCnt":1}),
        ("AI 키워드 KW", {"query":"인공지능","searchFd":"KW","collection":"project","displayCnt":1}),
    ]
    for label, p in tests:
        r = c.get(EP, params={"apprvKey":KEY, **p})
        print(f"{label}: {total(r.text):,}건")
        time.sleep(1)
