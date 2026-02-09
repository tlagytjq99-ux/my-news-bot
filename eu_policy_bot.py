import requests
import csv
from datetime import datetime
from xml.etree import ElementTree
from bs4 import BeautifulSoup
import time

def fetch_eu_clean_data():
    today = datetime.now().strftime('%Y-%m-%d')
    # 2025년 데이터를 위해 날짜 범위를 살짝 넓히거나 특정 시점 타겟팅
    url = "http://publications.europa.eu/webapi/notification/ingestion"
    params = {"startDate": today, "type": "CREATE", "wemiClasses": "work", "pageSize": "20"}
    headers = {"Accept": "application/rss+xml", "User-Agent": "Mozilla/5.0"}

    print(f"📡 데이터 정화 작업 시작 (사람이 볼 수 있는 링크로 변환)...", flush=True)
    collected_data = []

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        root = ElementTree.fromstring(response.content)
        items = root.findall('.//item')

        for item in items:
            cellar_id = "N/A"
            for child in item:
                if 'cellarId' in child.tag:
                    cellar_id = child.text.replace('cellar:', '')
                    break
            
            if cellar_id != "N/A":
                # [수정 1] 사람이 보기 편한 상세 페이지 주소로 생성
                # 이 주소는 브라우저에서 열면 해당 문서의 요약 페이지로 연결됩니다.
                display_link = f"https://publications.europa.eu/en/publication-detail/-/publication/{cellar_id}"
                
                # [수정 2] 제목 역추적 (상세 페이지에서 추출)
                try:
                    time.sleep(1)
                    detail_res = requests.get(display_link, headers=headers, timeout=10)
                    if detail_res.status_code == 200:
                        soup = BeautifulSoup(detail_res.text, 'html.parser')
                        
                        # 웹페이지 구조에 따라 제목 위치가 다를 수 있으므로 우선순위 설정
                        title = "No Title"
                        if soup.title:
                            title = soup.title.string.split(' - ')[0].replace('Publication detail', '').strip()
                        
                        # 만약 제목이 너무 짧거나 이상하면 다른 태그 탐색
                        if len(title) < 5 and soup.find('h1'):
                            title = soup.find('h1').get_text(strip=True)

                        collected_data.append({
                            "date": today,
                            "title": title,
                            "link": display_link
                        })
                        print(f"✅ 수집완료: {title[:40]}...", flush=True)
                except:
                    continue

    except Exception as e:
        print(f"❌ 오류 발생: {e}", flush=True)

    # 저장
    file_name = 'EU_Policy_2025_Full.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
        writer.writeheader()
        if collected_data:
            writer.writerows(collected_data)
        else:
            writer.writerow({"date": today, "title": "Searching...", "link": "N/A"})

if __name__ == "__main__":
    fetch_eu_clean_data()
