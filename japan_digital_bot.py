import os
import csv
import re
from datetime import datetime

# 라이브러리 설치 확인 (에러 방지용)
try:
    import requests
    import xml.etree.ElementTree as ET
except ImportError:
    print("❌ 에러: requests 라이브러리가 없습니다. YAML 파일에서 pip install requests를 수행했는지 확인하세요.")
    exit(1)

def crawl_japan_digital_final():
    file_name = 'Japan_Digital_Policy_2025.csv'
    # 정책 카테고리 (Category 1)
    url = "https://www.digital.go.jp/press?category=1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    print("🚀 [최종 점검] 디지털청 정책 데이터를 수집합니다...")
    policy_data = []

    try:
        # 1. RSS 피드 먼저 시도 (가장 깔끔한 데이터 소스)
        print("📡 RSS 피드 분석 중...")
        rss_res = requests.get("https://www.digital.go.jp/rss/news.xml", timeout=15)
        if rss_res.status_code == 200:
            root = ET.fromstring(rss_res.content)
            for item in root.findall('.//item'):
                link = item.find('link').text
                if '/press/' in link:
                    policy_data.append({
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "title": item.find('title').text,
                        "link": link
                    })

        # 2. 웹 페이지 소스에서 직접 패턴 낚아채기 (RSS에 없는 과거 데이터용)
        print("🎯 웹 페이지 아카이브 스캔 중...")
        web_res = requests.get(url, headers=headers, timeout=15)
        # 정규표현식으로 링크와 제목 강제 추출 (HTML 구조가 깨져도 작동)
        matches = re.findall(r'href="(/press/[^"]+)"[^>]*>(.*?)</a>', web_res.text)
        
        for link, title in matches:
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            if len(clean_title) > 10:
                policy_data.append({
                    "date": "2025-Policy",
                    "title": clean_title,
                    "link": "https://www.digital.go.jp" + link
                })

        # 3. 데이터 저장 (중복 제거)
        if policy_data:
            unique_data = list({v['link']: v for v in policy_data}.values())
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                writer.writeheader()
                writer.writerows(unique_data)
            print(f"✅ 대성공! {len(unique_data)}건의 정책 데이터를 파일에 담았습니다.")
        else:
            # 빈 파일 생성 (Git Push 에러 방지용)
            print("⚠️ 수집된 데이터가 없어 빈 파일을 생성합니다.")
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                f.write("date,title,link\n")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        if not os.path.exists(file_name):
            with open(file_name, 'w', encoding='utf-8-sig') as f:
                f.write("date,title,link\n")

if __name__ == "__main__":
    crawl_japan_digital_final()
