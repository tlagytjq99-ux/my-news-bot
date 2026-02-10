import requests
from bs4 import BeautifulSoup
import csv
import xml.etree.ElementTree as ET
from datetime import datetime

def crawl_digital_agency_policy_only():
    # 정책(Category=1) 필터가 적용된 주소
    policy_url = "https://www.digital.go.jp/press?category=1"
    file_name = 'Japan_Digital_Policy_2025.csv'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    policy_results = []
    print(f"🎯 [정책 파트 정밀 추출] {policy_url} 스캔 시작...")

    try:
        # 1. 웹 페이지 스캐닝 (과거~현재 정책 리스트)
        res = requests.get(policy_url, headers=headers, timeout=20)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')

        # 디지털청 보도자료 리스트 아이템 추출
        # 기사는 보통 article 태그나 특정 리스트 구조 안에 있습니다.
        articles = soup.find_all(['article', 'div'], class_=lambda x: x and 'ecl-card' in x) or soup.find_all('a', href=True)

        for item in articles:
            href = item.get('href') if item.name == 'a' else (item.find('a')['href'] if item.find('a') else None)
            if not href or '/press/' not in href: continue

            title = item.get_text(strip=True)
            # 메뉴나 불필요한 텍스트 필터링
            if len(title) < 10 or "一覧" in title: continue

            full_link = "https://www.digital.go.jp" + href if href.startswith('/') else href
            
            policy_results.append({
                "date": datetime.now().strftime("%Y-%m-%d"), # 페이지엔 연도 표기가 생략될 수 있어 수집일 기준
                "title": title,
                "link": full_link
            })

        # 2. RSS 피드 교차 검증 (최신성 확보)
        try:
            rss_res = requests.get("https://www.digital.go.jp/rss/news.xml", timeout=10)
            root = ET.fromstring(rss_res.content)
            for entry in root.findall('.//item'):
                rss_link = entry.find('link').text
                # RSS 데이터 중 정책(press) 관련 링크만 선별
                if '/press/' in rss_link:
                    policy_results.append({
                        "date": "RSS_Latest",
                        "title": entry.find('title').text,
                        "link": rss_link
                    })
        except:
            print("⚠️ RSS 교차 검증은 건너뜁니다.")

        # 3. 데이터 정제 및 저장
        if policy_results:
            # 링크 기준 중복 제거
            unique_policies = list({v['link']: v for v in policy_results}.values())
            
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                writer.writeheader()
                writer.writerows(unique_policies)
            print(f"✅ 추출 성공! 총 {len(unique_policies)}건의 정책 데이터를 확보했습니다.")
        else:
            # 빈 파일 생성 (Git 에러 방지)
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                f.write("date,title,link\n")
            print("⚠️ 조건에 맞는 정책이 발견되지 않았습니다.")

    except Exception as e:
        print(f"❌ 중명 오류: {e}")
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            f.write("date,title,link\n")

if __name__ == "__main__":
    crawl_digital_agency_policy_only()
