import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
from urllib.parse import urljoin

def main():
    target_url = "https://www.cao.go.jp/new/index.html"
    file_name = 'japan_ai_report.csv'
    
    print(f"📡 [일본 내각부] 데이터 수집 테스트 시작...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=20)
        response.encoding = response.apparent_encoding 
        soup = BeautifulSoup(response.text, 'html.parser')

        # 페이지 내 모든 링크 추출
        links = soup.find_all('a', href=True)
        
        new_data = []
        existing_titles = set()
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader: existing_titles.add(row['제목'])

        count = 0
        for a in links:
            title = a.get_text().strip()
            link = urljoin(target_url, a['href'])
            
            # 💡 [테스트 핵심] 키워드 검사 생략! 
            # 제목이 15자 이상인 '진짜 뉴스'처럼 보이는 것 5개만 무조건 가져옵니다.
            if len(title) > 15 and title not in existing_titles:
                # 메뉴나 공통 공지 제외
                if any(x in title for x in ['お問い合わせ', 'サイトマップ', 'アクセシビリティ']): 
                    continue
                    
                print(f"   🆕 뉴스 수집 중: {title[:40]}...")
                new_data.append({
                    "기관": "일본 내각부(CAO)",
                    "발행일": datetime.now().strftime("%Y-%m-%d"),
                    "제목": title,
                    "링크": link,
                    "수집일": datetime.now().strftime("%Y-%m-%d")
                })
                count += 1
                if count >= 5: break

        if new_data:
            file_exists = os.path.exists(file_name)
            with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "링크", "수집일"])
                if not file_exists: writer.writeheader()
                writer.writerows(new_data)
            print(f"✅ 성공! 테스트 데이터 {len(new_data)}건 수집 완료.")
        else:
            print("❌ 여전히 데이터를 찾지 못했습니다. 구조 확인이 필요합니다.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    main()
