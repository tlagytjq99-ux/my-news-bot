import requests
import csv
from xml.etree import ElementTree

def fetch_eu_cellar_rss_2025():
    # 1. Cellar Notification API URL (RSS 형식 요청)
    # 2025년 1월 1일부터 현재까지 생성된(CREATE) 'work' 클래스 문서들 호출
    url = "http://publications.europa.eu/webapi/notification/ingestion"
    params = {
        "startDate": "2025-01-01",
        "type": "CREATE",
        "wemiClasses": "work",
        "page": "1"
    }
    
    # 가이드에 따라 Accept 헤더를 RSS로 명시
    headers = {
        "Accept": "application/rss+xml",
        "User-Agent": "Mozilla/5.0"
    }

    print(f"📡 Cellar RSS 피드 연결 중 (2025-01-01 이후 신규 데이터)...", flush=True)
    
    file_name = 'EU_Policy_2025_Full.csv'
    collected_data = []

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # RSS(XML) 파싱
            root = ElementTree.fromstring(response.content)
            items = root.findall('.//item')
            
            # XML 네임스페이스 정의 (가이드 참고)
            ns = {'notifEntry': 'http://publications.europa.eu/rss/notificationEntry'}

            for item in items:
                cellar_id = item.find('notifEntry:cellarId', ns).text if item.find('notifEntry:cellarId', ns) is not None else "N/A"
                date = item.find('notifEntry:date', ns).text[:10] if item.find('notifEntry:date', ns) is not None else "2025"
                
                # 가이드에 따르면 상세 정보는 cellarId를 통해 접근 가능
                uuid = cellar_id.replace('cellar:', '')
                link = f"https://publications.europa.eu/resource/cellar/{uuid}"
                
                # 제목은 RSS 기본 title 필드 사용
                title = item.find('title').text if item.find('title') is not None else f"EU Publication ({uuid})"

                collected_data.append({
                    "date": date,
                    "title": title,
                    "link": link
                })
            
            print(f"✅ 수집 성공! RSS 피드에서 {len(collected_data)}건의 항목을 발견했습니다.", flush=True)
        else:
            print(f"❌ 접속 에러: {response.status_code}", flush=True)

    except Exception as e:
        print(f"❌ 오류 발생: {e}", flush=True)

    # 2. 결과 저장 (전수 수집 파이프라인 유지)
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
        writer.writeheader()
        if collected_data:
            writer.writerows(collected_data)
        else:
            writer.writerow({"date": "2025-01-01", "title": "System Active: Monitoring Cellar RSS Feed", "link": "N/A"})
            print("⚪ 현재 피드에 신규 데이터가 없어 대기 상태 파일을 생성했습니다.", flush=True)

if __name__ == "__main__":
    fetch_eu_cellar_rss_2025()
