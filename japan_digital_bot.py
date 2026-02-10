import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

def crawl_japan_digital_agency():
    # 일문 보도자료 페이지 (가장 빠르고 정확함)
    url = "https://www.digital.go.jp/news/press"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    print(f"🚀 [일본 디지털청] 2025년 정책 수집 시작: {datetime.now()}")

    try:
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')

        # 보도자료 아이템 추출 (디지털청 특유의 리스트 구조 반영)
        # 각 기사는 보통 ecl-card 또는 특정 리스트 클래스 안에 있습니다.
        articles = soup.select('a.ecl-link') 

        policy_data = []
        for article in articles:
            # 제목 추출
            title_tag = article.find(['h2', 'h3'])
            if not title_tag: continue
            title = title_tag.get_text(strip=True)

            # 링크 추출
            link = article['href']
            if not link.startswith('http'):
                link = "https://www.digital.go.jp" + link

            # 날짜 추출 (일본은 2025년 또는 令和7年으로 표기됨)
            date_tag = article.find('time') or article.find('span', class_='date')
            date_text = date_tag.get_text(strip=True) if date_tag else ""

            # 2025년 데이터 필터링 (서기 2025년 또는 일본 연호 令和7年/R7 확인)
            if "2025" in date_text or "令和7" in date_text or "R7" in date_text:
                policy_data.append({
                    "date": date_text,
                    "title": title,
                    "link": link,
                    "collected_at": datetime.now().strftime("%Y-%m-%d")
                })

        # 데이터 저장 (기존 데이터와 병합하거나 새로 쓰기)
        if policy_data:
            keys = policy_data[0].keys()
            with open('Japan_Digital_Policy_2025.csv', 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(policy_data)
            print(f"✅ 성공: {len(policy_data)}건의 정책을 저장했습니다.")
        else:
            print("⚠️ 새로운 2025년 정책을 찾지 못했습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    crawl_japan_digital_agency()
