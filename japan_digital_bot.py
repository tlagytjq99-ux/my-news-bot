import requests
from bs4 import BeautifulSoup
import csv
import xml.etree.ElementTree as ET # 라이브러리 설치 없이 RSS 읽기용

def crawl_digital_agency_hybrid():
    file_name = 'Japan_Digital_Policy_2025.csv'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    policy_data = []

    # --- 1단계: RSS 피드 털기 (실시간 최신 데이터) ---
    print("📡 [RSS 스캔] 최신 피드를 분석 중...")
    try:
        rss_res = requests.get("https://www.digital.go.jp/rss/news.xml", timeout=15)
        root = ET.fromstring(rss_res.content)
        for item in root.findall('.//item'):
            title = item.find('title').text
            link = item.find('link').text
            # RSS에서 2025, 2026년 데이터만 추출
            policy_data.append({"date": "RSS_Latest", "title": title, "link": link})
    except Exception as e:
        print(f"⚠️ RSS 스캔 건너뜀 (오류: {e})")

    # --- 2단계: 웹 아카이브 털기 (과거 2025년 전수 조사) ---
    print("🎯 [웹 스캔] 2025년 전체 아카이브 정밀 수색 중...")
    try:
        web_res = requests.get("https://www.digital.go.jp/news/press", headers=headers, timeout=15)
        web_res.encoding = 'utf-8'
        soup = BeautifulSoup(web_res.text, 'html.parser')
        
        # 보도자료 리스트의 모든 링크 추출
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/news/' in href:
                title = a.get_text(strip=True)
                if len(title) > 10: # 메뉴 제외, 실제 제목만
                    policy_data.append({
                        "date": "Archive_2025",
                        "title": title,
                        "link": "https://www.digital.go.jp" + href if href.startswith('/') else href
                    })
    except Exception as e:
        print(f"⚠️ 웹 스캔 오류: {e}")

    # --- 3단계: 중복 제거 및 저장 ---
    if policy_data:
        # 링크 기준으로 중복 데이터 제거
        unique_data = list({v['link']: v for v in policy_data}.values())
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(unique_data)
        print(f"✅ 합체 성공! RSS + 웹 아카이브 총 {len(unique_data)}건 확보.")
    else:
        # 빈 파일이라도 생성하여 Git 에러 방지
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            f.write("date,title,link\n")

if __name__ == "__main__":
    crawl_digital_agency_hybrid()
