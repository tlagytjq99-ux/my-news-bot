import requests
import csv
from datetime import datetime
from xml.etree import ElementTree
from bs4 import BeautifulSoup
import time
import os

def fetch_eu_today_policy():
    # 1. 오늘 날짜 설정 (2026-02-09)
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 2. EU 알림 서비스 API 호출 (오늘 생성된 모든 문서 대상)
    url = "http://publications.europa.eu/webapi/notification/ingestion"
    params = {
        "startDate": today,
        "type": "CREATE",
        "pageSize": "100" 
    }
    headers = {"Accept": "application/rss+xml", "User-Agent": "Mozilla/5.0"}

    print(f"🕵️ [오늘의 정책 탐색] {today}자 문서를 분석 중입니다...", flush=True)
    policy_data = []

    try:
        response = requests.get(url, params=params, headers=headers, timeout=60)
        root = ElementTree.fromstring(response.content)
        items = root.findall('.//item')

        for item in items:
            cellar_id = "N/A"
            for child in item:
                if 'cellarId' in child.tag:
                    cellar_id = child.text.replace('cellar:', '')
                    break
            
            if cellar_id != "N/A":
                # 사람이 읽을 수 있는 요약 페이지
                display_link = f"https://publications.europa.eu/en/publication-detail/-/publication/{cellar_id}"
                
                try:
                    # 서버 부하 방지 및 정밀 파싱
                    time.sleep(0.5)
                    detail_res = requests.get(display_link + "?language=en", headers=headers, timeout=10)
                    soup = BeautifulSoup(detail_res.text, 'html.parser')
                    
                    # 제목 추출 (h1 태그 또는 title 태그)
                    title = ""
                    h1_title = soup.find('h1', class_='document-title')
                    if h1_title:
                        title = h1_title.get_text(strip=True)
                    elif soup.title:
                        title = soup.title.string.split(' - ')[0].replace('Publication detail', '').strip()

                    # 3. [중요] 정책 필터링 로직
                    # '법(Law)'보다는 '방향성(Policy)'을 나타내는 단어들
                    policy_keywords = ["Report", "Communication", "Strategy", "Proposal", "Action Plan", "Working Document", "COM(", "SWD(", "Opinion", "Notice"]
                    # 단순 절차성 법령/오타 수정은 제외
                    exclude_keywords = ["Rettifica", "Berichtigung", "Rectificatif", "Decision of the Court"]

                    is_policy = any(pk.lower() in title.lower() for pk in policy_keywords)
                    is_excluded = any(ek.lower() in title.lower() for ek in exclude_keywords)

                    if is_policy and not is_excluded:
                        policy_data.append({
                            "date": today,
                            "title": title,
                            "link": display_link
                        })
                        print(f"🎯 정책 발견: {title[:60]}...", flush=True)
                except:
                    continue
                    
    except Exception as e:
        print(f"❌ 수집 중 오류: {e}", flush=True)

    # 4. 결과 저장 (Append 모드)
    save_to_csv(policy_data)

def save_to_csv(new_data):
    file_name = 'EU_Today_Policy_Test.csv'
    file_exists = os.path.isfile(file_name)
    
    with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
        if not file_exists:
            writer.writeheader()
        if new_data:
            writer.writerows(new_data)
            print(f"💾 총 {len(new_data)}건의 오늘자 정책 리스트가 저장되었습니다.", flush=True)
        else:
            print("ℹ️ 오늘 새로 발행된 정책 문서가 아직 없습니다.", flush=True)

if __name__ == "__main__":
    fetch_eu_today_policy()
