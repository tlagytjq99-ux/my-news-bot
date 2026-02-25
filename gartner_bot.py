import requests
import xml.etree.ElementTree as ET
import csv
from urllib.parse import quote

def crawl_gartner_final():
    # 1. 검색 키워드 최적화: 가트너 공식 보도자료 위주
    # 2026년 가트너 AI 및 테크 관련 키워드 조합
    query = quote('Gartner "Press Release" AI ICT 2026')
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    
    file_name = 'Gartner_Insight_Archive.csv'
    all_data = []

    print(f"📡 구글 RSS 인텔리전스 가동: {query}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }

    try:
        # RSS 피드 요청
        response = requests.get(rss_url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            # RSS 아이템 순회 (최신 10~15개)
            for item in root.findall('.//item')[:15]:
                title = item.find('title').text
                link = item.find('link').text
                pub_date = item.find('pubDate').text
                
                # 가트너 공식 도메인이 포함된 결과만 엄선
                if "gartner.com" in link.lower() or "gartner" in title.lower():
                    all_data.append({
                        "date": pub_date,
                        "title": title.split(' - ')[0], # 제목 뒤의 언론사명 제거
                        "link": link
                    })

            if all_data:
                # CSV 저장 (엑셀 깨짐 방지 utf-8-sig)
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                    writer.writeheader()
                    writer.writerows(all_data)
                print(f"✅ 수집 성공! 총 {len(all_data)}건의 가트너 인사이트 확보.")
                return
            else:
                print("⚠️ 조건에 맞는 최신 가트너 뉴스를 찾지 못했습니다.")
        else:
            print(f"❌ 접속 실패 (코드: {response.status_code})")

    except Exception as e:
        print(f"❌ 실행 중 오류: {e}")

    # 실패 시 빈 파일 생성 (워크플로우 에러 방지)
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        f.write("date,title,link\n")

if __name__ == "__main__":
    crawl_gartner_final()
