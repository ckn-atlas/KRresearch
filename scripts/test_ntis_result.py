"""NTIS 성과검색 API 테스트 + 과제↔논문 연결 검증"""
import httpx, re, time

KEY = "53fp665x1847viai1w45"
EP = "https://www.ntis.go.kr/rndopen/openApi/public_result"

def total(text):
    m = re.search(r"<TOTALHITS>(\d+)</TOTALHITS>", text)
    err = re.search(r"<error>(.*?)</error>", text)
    if err: return f"ERROR: {err.group(1)}"
    return m.group(1) if m else "?"

with httpx.Client(timeout=20, follow_redirects=True) as c:
    # 1. 논문 성과검색 기본 동작
    print("=== 1) 논문성과(rpaper) 기본 ===")
    r = c.get(EP, params={"apprvKey":KEY,"query":"건설","collection":"rpaper","displayCnt":1})
    print("  total:", total(r.text))
    time.sleep(1)

    # 2. 특허 성과검색
    print("=== 2) 특허성과(rpatent) ===")
    r = c.get(EP, params={"apprvKey":KEY,"query":"건설","collection":"rpatent","displayCnt":1})
    print("  total:", total(r.text))
    time.sleep(1)

    # 3. ProjectID로 특정 과제의 성과 조회 (검증 핵심)
    print("=== 3) 특정 과제번호로 성과 검색 ===")
    # 과제검색에서 본 ProjectNumber 사용: 1500000595
    for pid in ["1500000595", "1500001124"]:
        r = c.get(EP, params={"apprvKey":KEY,"query":pid,"searchFd":"PI","collection":"rpaper","displayCnt":2})
        print(f"  PI={pid}: {total(r.text)}")
        time.sleep(1)

    # 4. 논문 성과 1건 전체 구조 저장
    print("=== 4) 논문성과 샘플 저장 ===")
    r = c.get(EP, params={"apprvKey":KEY,"query":"스마트건설","collection":"rpaper","displayCnt":1})
    open("data/_raw/ntis_result_sample.xml","w",encoding="utf-8").write(r.text)
    print(f"  saved {len(r.text)} chars")
