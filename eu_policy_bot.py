import requests
import csv
from datetime import datetime
from xml.etree import ElementTree

def fetch_eu_daily_rss_fixed():
    # 1. 오늘 날짜 설정 (데이터가 가장 잘 나오는 시점)
    today = datetime.now().strftime('%Y-%m-%d')
    
    url = "http://publications.europa.eu/webapi/notification/ingestion"
    params = {
        "startDate": today, 
        "type": "CREATE",
        "wemiClasses": "work",
        "pageSize": "100"
    }
    
    headers = {
        "Accept": "application/rss+xml",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Policy-Finder-Agent"
    }

    print(f"📡 [최종 수선] {today} 데이터를 정밀 파싱합니다...", flush=True)
    
    collected_data = []

    try:
        response = requests.get(url, params=params, headers=headers, timeout=60)
        
        if response.status_code == 200:
            # RSS XML 로드
            root = ElementTree.fromstring(response.content)
            # 모든 item 태그 탐색
            items = root.findall('.//item')

            for item in items:
                # [수정 포인트] 제목 태그를 더 정확하게 타격
                title_node = item.find('title')
                title = title_node.text if title_node is not None else "No Title"
                
                # Cellar ID 추출을 위한 네임스페이스 처리
                cellar_id = "N/A"
                for child in item:
                    if 'cellarId' in child.tag:
                        cellar_id = child.text.replace('cellar:', '')
                        break
                
                if cellar_id != "N/A":
                    link = f"https://publications.europa.eu/resource/cellar/{cellar_id}"
                    collected_data.append({
                        "date": today,
                        "title": title,
                        "link": link
                    })
            
            print(f"✅ 수집 성공! {len(collected_data)}건의 제목과 링크를 모두 확보했습니다.", flush=True)
        else:
            print(f"❌ 서버 응답 실패: {response.status_code}", flush=True)

    except Exception as e:
        print(f"❌ 파싱 오류 발생: {e}", flush=True)

    # 결과 저장
    file_name = 'EU_Policy_2025_Full.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
        writer.writeheader()
        if collected_data:
            writer.writerows(collected_data)
        else:
            writer.writerow({"date": today, "title": "No data found for today", "link": "N/A"})

if __name__ == "__main__":
    fetch_eu_daily_rss_fixed()
