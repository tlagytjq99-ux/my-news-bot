import requests
import csv
import xml.etree.ElementTree as ET

def fetch_eu_latest_feed():
    # EU 간행물처의 '최신 발행물' RSS 피드 주소
    # DB 인덱싱보다 훨씬 빠르게 업데이트되는 통로입니다.
    feed_url = "https://op.europa.eu/en/web/general-publications/publications?p_p_id=eu_europa_publications_portlet_search_search_results_display_WAR_eu_europa_publications_portlet&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_eu_europa_publications_portlet_search_search_results_display_WAR_eu_europa_publications_portlet_format=rss"
    
    file_name = 'EU_Policy_2025_Final.csv'
    all_records = []
    
    print("📡 [피드 수집] 실시간 최신 문서 스트림에서 2025년 자료를 낚아챕니다...", flush=True)

    try:
        response = requests.get(feed_url, timeout=30)
        if response.status_code == 200:
            # RSS(XML) 파싱
            root = ET.fromstring(response.content)
            items = root.findall('.//item')
            
            for item in items:
                title = item.find('title').text
                link = item.find('link').text
                # RSS 피드에는 보통 발행일이 pubDate 태그에 있음
                date = item.find('pubDate').text if item.find('pubDate') is not None else "2025-XX-XX"
                
                # 2025년 데이터만 필터링 (텍스트 검사)
                if "2025" in date or "2025" in title:
                    all_records.append({
                        "date": date,
                        "title": title,
                        "link": link
                    })

            if all_records:
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                    writer.writeheader()
                    writer.writerows(all_records)
                print(f"✅ [성공] 최신 피드에서 {len(all_records)}건을 긴급 확보했습니다!", flush=True)
            else:
                print("⚠️ 최신 피드에도 2025년 표기 데이터가 아직 없습니다. (현재 서버 점검 가능성 높음)", flush=True)
        else:
            print(f"❌ 피드 접속 실패: {response.status_code}", flush=True)

    except Exception as e:
        print(f"❌ 시스템 오류: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_latest_feed()
