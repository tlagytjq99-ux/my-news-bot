import requests
import xml.etree.ElementTree as ET
import csv
from urllib.parse import quote

def crawl_gartner_google_rss():
    # 1. 검색어 설정: site:gartner.com 2026 (URL 인코딩 포함)
    query = quote("site:gartner.com/en/newsroom/press-releases 2026")
    # 구글 뉴스 RSS 공식 주소
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    
    file_name = 'Gartner_Insight_Archive.csv'
    all_data = []

    print(f"📡 구글 RSS 피드 직접 통신 시작...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(rss_url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            # XML 데이터 파싱
            root = ET.fromstring(response.content)
            
            # RSS 내의 각 아이템(뉴스) 순회
            for item in root.findall('.//item')[:15]: # 최신 15개
                title = item.find('title').text
                link = item.find('link').text
                pub_date = item.find('pubDate').text
                
                # 가트너 링크만 필터링 (가끔 광고 섞임 방지)
                if "gartner.com" in link:
                    all_data.append({
                        "date": pub_date,
                        "title": title,
                        "link": link
                    })

            if all_data:
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                    writer.writeheader()
                    writer.writerows(all_data)
                print(f"✅ RSS 우회 성공! 총 {len(all_data)}건 확보 완료.")
                return
            else:
                print("⚠️ RSS 검색 결과가 비어 있습니다.")
        else:
            print(f"❌ RSS 접속 실패 (코드: {response.status_code})")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    # 실패 시 빈 파일 생성
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        f.write("date,title,link\n")

if __name__ == "__main__":
    crawl_gartner_google_rss()
