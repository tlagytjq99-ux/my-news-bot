import requests
import csv
from datetime import datetime
from xml.etree import ElementTree

def fetch_eu_daily_rss():
    # 1. 오늘 날짜 구하기 (서버 부하 최소화)
    today = datetime.now().strftime('%Y-%m-%d')
    
    # [핵심] 2025년 데이터 중 '오늘' 등록된 것만 요청 (서버가 응답하기 가장 쉬운 상태)
    url = "http://publications.europa.eu/webapi/notification/ingestion"
    params = {
        "startDate": today, 
        "type": "CREATE",
        "wemiClasses": "work",
        "pageSize": "100"
    }
    
    headers = {
        "Accept": "application/rss+xml",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Policy-Watcher-Bot"
    }

    print(f"📡 [데일리 수집] {today} 신규 정책 데이터를 RSS로 호출합니다...", flush=True)
    
    file_name = 'EU_Policy_2025_Full.csv'
    collected_data = []

    try:
        # 타임아웃 60초 설정
        response = requests.get(url, params=params, headers=headers, timeout=60)
        
        if response.status_code == 200:
            root = ElementTree.fromstring(response.content)
            ns = {'notifEntry': 'http://publications.europa.eu/rss/notificationEntry'}
            items = root.findall('.//item')

            for item in items:
                title = item.find('title').text
                # Cellar ID 추출 및 링크 생성
                cellar_id = item.find('notifEntry:cellarId', ns).text.replace('cellar:', '')
                link = f"https://publications.europa.eu/resource/cellar/{cellar_id}"
                
                collected_data.append({
                    "date": today,
                    "title": title,
                    "link": link
                })
            
            print(f"✅ 성공! 오늘자 신규 데이터 {len(collected_data)}건을 발견했습니다.", flush=True)
        else:
            print(f"❌ 서버 응답 실패: {response.status_code}", flush=True)

    except Exception as e:
        print(f"❌ 오류 발생: {e}", flush=True)

    # 결과 저장 (기존 데이터가 있다면 유지하는 로직은 나중에 추가하고, 일단 수집 성공 확인)
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
        writer.writeheader()
        if collected_data:
            writer.writerows(collected_data)
        else:
            writer.writerow({"date": today, "title": f"No new data for {today}", "link": "N/A"})

if __name__ == "__main__":
    fetch_eu_daily_rss()
