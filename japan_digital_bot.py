import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime

def crawl_digital_agency_final():
    url = "https://www.digital.go.jp/news/press"
    file_name = 'Japan_Digital_Policy_2025.csv'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    print(f"🎯 [정밀 스캔] {datetime.now().year}년 최신 정책 데이터를 낚아챕니다...")

    try:
        res = requests.get(url, headers=headers, timeout=20)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')

        # 디지털청의 실제 기사 리스트는 'article' 태그로 감싸져 있습니다.
        articles = soup.find_all('article')
        
        policy_data = []
        for item in articles:
            # 1. 제목과 링크 찾기
            link_tag = item.find('a')
            if not link_tag: continue
            
            title = link_tag.get_text(strip=True)
            href = link_tag.get('href', '')
            link = "https://www.digital.go.jp" + href if href.startswith('/') else href

            # 2. 날짜 찾기 (time 태그 혹은 특정 클래스)
            date_tag = item.find('time')
            date_text = date_tag.get_text(strip=True) if date_tag else ""

            # 3. 2025년 혹은 2026년 데이터인지 검증
            # 일본 연호(令和7, 令和8)와 서기를 모두 체크합니다.
            target_years = ['2025', '2026', '令和7', '令和8', 'R7', 'R8']
            if any(yr in date_text or yr in title for yr in target_years):
                policy_data.append({
                    "date": date_text,
                    "title": title,
                    "link": link
                })

        # 결과 저장
        if policy_data:
            # 중복 제거 (링크 기준)
            unique_data = list({v['link']: v for v in policy_data}.values())
            
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                writer.writeheader()
                writer.writerows(unique_data)
            print(f"✅ 드디어 성공! {len(unique_data)}건의 데이터를 확보했습니다.")
            print(f"📌 샘플 제목: {unique_data[0]['title'][:30]}...")
        else:
            # 데이터가 없을 경우, 깃 에러 방지를 위해 헤더만 있는 파일 생성
            print("⚠️ 조건에 맞는 데이터가 없습니다. 필터를 완화하여 빈 파일을 유지합니다.")
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                writer.writeheader()

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        # 파일이 아예 안 만들어지면 Git Push가 깨지므로 빈 파일 강제 생성
        if not os.path.exists(file_name):
            with open(file_name, 'w', encoding='utf-8-sig') as f:
                f.write("date,title,link\n")

if __name__ == "__main__":
    crawl_digital_agency_final()
