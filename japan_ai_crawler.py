import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
from urllib.parse import urljoin

def main():
    # 🎯 타겟 주소 (보도발표/뉴스 페이지)
    target_url = "https://www8.cao.go.jp/cstp/stmain/index.html"
    file_name = 'japan_ai_report.csv'
    
    print(f"📡 [일본 내각부] 데이터 수집 강제 모드 시작...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=20)
        response.encoding = response.apparent_encoding 
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. 텍스트가 있는 모든 링크(a)를 다 가져옵니다.
        all_links = soup.find_all('a', href=True)
        
        new_data = []
        existing_titles = set()
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader: existing_titles.add(row['제목'])

        count = 0
        for a in all_links:
            title = a.get_text().strip()
            link = urljoin(target_url, a['href'])
            
            # 💡 [필터 조건] 
            # - 제목이 너무 짧지 않아야 함 (메뉴 버튼 방지)
            # - 링크 주소에 .html이나 .pdf가 포함되어야 함 (실제 문서/기사)
            # - 특정 제외 키워드가 없어야 함
            if len(title) > 10 and any(ext in link for ext in ['.html', '.pdf']):
                if 'javascript' not in link and title not in existing_titles:
                    
                    print(f"   🆕 뉴스 발견: {title[:40]}...")
                    new_data.append({
                        "기관": "일본 내각부(CAO)",
                        "발행일": datetime.now().strftime("%Y-%m-%d"),
                        "제목": title,
                        "링크": link,
                        "수집일": datetime.now().strftime("%Y-%m-%d")
                    })
                    count += 1
                    if count >= 10: break # 테스트를 위해 10개까지 수집

        # 💾 결과 저장
        if new_data:
            file_exists = os.path.exists(file_name)
            with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "링크", "수집일"])
                if not file_exists: writer.writeheader()
                writer.writerows(new_data)
            print(f"✅ 성공! {len(new_data)}건의 데이터를 엑셀에 기록했습니다.")
        else:
            print("❌ 페이지에서 뉴스 형태의 링크를 찾지 못했습니다. 구조 확인이 필요합니다.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    main()
