import requests
import csv
import os
from xml.etree import ElementTree
from datetime import datetime

def fetch_eu_publications_rss():
    # 1. 대표님이 주신 EU 간행물 RSS 피드 링크
    rss_url = "http://op.europa.eu/o/opportal-service/rss/savedQuery?queryid=128956&hash=MTAxNTc7MTAxODQ7MTc3MDYyMDgwNzc4MA=="
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print("📡 EU 간행물 RSS 피드 분석 중...", flush=True)
    collected_data = []

    try:
        response = requests.get(rss_url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"❌ 접속 실패: {response.status_code}", flush=True)
            return

        # XML 파싱
        root = ElementTree.fromstring(response.content)
        # RSS 피드 내의 모든 item 태그 찾기
        items = root.findall('.//item')

        for item in items:
            title = item.find('title').text if item.find('title') is not None else "No Title"
            link = item.find('link').text if item.find('link') is not None else ""
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
            
            # [핵심] 2025년도 자료만 필터링
            # pubDate 형식 예: "Wed, 05 Feb 2025 10:00:00 GMT"
            if "2025" in pub_date:
                # 날짜 형식을 깔끔하게 변환 (예: 2025-02-05)
                try:
                    date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                    clean_date = date_obj.strftime('%Y-%m-%d')
                except:
                    clean_date = pub_date # 변환 실패시 원본 유지

                collected_data.append({
                    "date": clean_date,
                    "title": title.strip(),
                    "link": link.strip()
                })

        print(f"✅ 2025년 간행물 {len(collected_data)}건 발견!", flush=True)

    except Exception as e:
        print(f"❌ 오류 발생: {e}", flush=True)

    # 2. 결과 저장 (CSV)
    save_to_csv(collected_data)

def save_to_csv(data):
    # 파일명은 대표님 설정에 맞춰 유지
    file_name = 'EU_Policy_2025_Full.csv'
    
    if not data:
        print("ℹ️ 저장할 2025년 데이터가 없습니다.", flush=True)
        return

    # 저장 (덮어쓰기 모드 - 전수 조사용)
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
        writer.writeheader()
        writer.writerows(data)
    
    print(f"💾 '{file_name}'에 최종 저장 완료!", flush=True)

if __name__ == "__main__":
    fetch_eu_publications_rss()
