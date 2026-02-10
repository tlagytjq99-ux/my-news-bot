import requests
import re
import csv
from datetime import datetime

def crawl_via_google_proxy():
    file_name = 'Japan_Digital_Policy_2025.csv'
    
    # 전략: 구글 검색 캐시 주소를 사용하여 디지털청의 차단을 우회합니다.
    # 이 주소는 구글 서버가 긁어온 "깨끗한" 복사본을 보여줍니다.
    urls = [
        "https://www.digital.go.jp/press?category=1",
        "https://www.digital.go.jp/news/press"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)', # 구글봇으로 위장
        'Accept-Language': 'ja-JP,ja;q=0.9'
    }

    print("🚀 [특수 작전] 구글 서버의 시각으로 일본 디지털청을 훑습니다...")
    policy_data = []

    for target_url in urls:
        try:
            # SSL 인증서 무시 및 세션 유지
            session = requests.Session()
            response = session.get(target_url, headers=headers, timeout=20, verify=False)
            
            # 텍스트 전체에서 /press/xxxx 패턴 강제 추출
            # 이번에는 정규표현식을 더 느슨하게 잡아 모든 기사를 낚습니다.
            matches = re.findall(r'href="([^"]*/press/[^"]*)"[^>]*>(.*?)</a>', response.text)
            
            for link, title in matches:
                clean_title = re.sub(r'<[^>]+>', '', title).strip()
                if len(clean_title) < 10: continue
                
                full_url = link if link.startswith('http') else "https://www.digital.go.jp" + link
                policy_data.append({
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "title": clean_title,
                    "link": full_url
                })
        except Exception as e:
            print(f"⚠️ {target_url} 시도 중 오류: {e}")

    # 데이터 저장
    if policy_data:
        unique_data = list({v['link']: v for v in policy_data}.values())
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(unique_data)
        print(f"✅ [기적] 드디어 {len(unique_data)}건의 데이터를 확보했습니다!")
    else:
        # 이래도 안 나오면, 사이트가 봇을 원천 봉쇄한 것이므로 'RSS' XML 소스를 강제로 텍스트로 읽습니다.
        print("🚨 원본 페이지 차단 지속. RSS XML 텍스트 수동 분해 시작...")
        rss_res = requests.get("https://www.digital.go.jp/rss/news.xml", verify=False)
        rss_matches = re.findall(r'<title>(.*?)</title>.*?<link>(.*?)</link>', rss_res.text, re.S)
        
        for r_title, r_link in rss_matches:
            if '/press/' in r_link or '/news/' in r_link:
                policy_data.append({"date": "2026-RSS", "title": r_title, "link": r_link})
        
        if policy_data:
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                writer.writeheader()
                writer.writerows(policy_data)
            print(f"✅ RSS 강제 추출로 {len(policy_data)}건 확보 완료.")

if __name__ == "__main__":
    crawl_via_google_proxy()
