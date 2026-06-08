"""NTIS 페이징/조회 한계 확인 (최소 호출)"""
import httpx, re, time

KEY = "53fp665x1847viai1w45"
EP = "https://www.ntis.go.kr/rndopen/openApi/public_project"

def info(text):
    th = re.search(r"<TOTALHITS>(\d+)</TOTALHITS>", text)
    hits = re.search(r"<HITS>(\d+)</HITS>", text)
    nhit = len(re.findall(r"<HIT NO=", text))
    return (th.group(1) if th else "?", hits.group(1) if hits else "?", nhit)

with httpx.Client(timeout=20, follow_redirects=True) as c:
    # displayCnt 100 가능한지
    r = c.get(EP, params={"apprvKey":KEY,"query":"건설","collection":"project","displayCnt":100,"startPosition":1})
    print("displayCnt=100:", info(r.text))
    time.sleep(1)

    # startPosition 깊은 페이지 가능한지
    r = c.get(EP, params={"apprvKey":KEY,"query":"건설","collection":"project","displayCnt":100,"startPosition":10000})
    print("startPosition=10000:", info(r.text))
    time.sleep(1)

    # 연도 필터 가능한지 (특정 필드 검색)
    r = c.get(EP, params={"apprvKey":KEY,"query":"PY=2024","collection":"project","displayCnt":2})
    print("query=PY=2024:", info(r.text))
