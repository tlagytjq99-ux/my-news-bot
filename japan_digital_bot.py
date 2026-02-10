import requests
import re
import csv
from datetime import datetime

def crawl_japan_digital_ultimate():
    file_name = 'Japan_Digital_Policy_2025.csv'
    # 데이터 소스 다각화 (전체 뉴스 + 보도자료)
    sources = [
        "https://www.digital.go.jp/rss/news.xml",
        "https://www.digital.go.jp/press?category=1" # 정책 카테고리
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    print("🦾 [데이터 확장] 정책 및 뉴스 데이터를 통합 수집합니다...")
    policy_data = []

    for url in sources:
        try:
            # SSL 검증 무시로 차단 확률 최소화
            res = requests.get(url, headers=headers, timeout=20, verify=False)
            content = res.text

            # 1. RSS 형식 분석 (xml 패턴)
            rss_items = re.findall(r'<item>.*?<title>(.*?)</title>.*?<link>(.*?)</link>', content, re.S)
            for t, l in rss_items:
                policy_data.append({"date": "RSS_Latest", "title": t, "link": l})

            # 2. 일반 HTML 형식 분석 (href 패턴)
            # /press/ 혹은 /news/ 가 포함된 모든 2025-2026 정책 링크 추출
            web_items = re.findall(r'href="([^"]*/(?:press|news)/[^"]*)"[^>]*>(.*?)</a>', content)
            for l, t in web_items:
                clean_title = re.sub(r'<[^>]+>', '', t).strip()
                if len(clean_title) > 10:
                    full_url = l if l.startswith('http') else "https://www.digital.go.jp" + l
                    policy_data.append({
                        "date": "2025-Policy",
                        "title": clean_title,
                        "link": full_url
                    })
        except:
            continue

    # 데이터 정제 및 저장
    if policy_data:
        # 중복 제거 (링크 기준)
        unique_data = list({v['link']: v for v in policy_data}.values())
        
        # 2025년/2026년 키워드 필터링 (선택 사항)
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(unique_data)
        print(f"✨ [성공] 총 {len(unique_data)}건의 정책/뉴스 리스트를 확보했습니다!")
    else:
        print("⚠️ 추가 데이터를 찾지 못했습니다.")

if __name__ == "__main__":
    crawl_japan_digital_ultimate()
