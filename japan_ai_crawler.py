import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
from urllib.parse import urljoin

def main():
    # 🎯 내각부 과학기술(AI 포함) 보도자료 리스트 페이지
    target_url = "https://www8.cao.go.jp/cstp/stmain/index.html"
    file_name = 'japan_ai_report.csv'
    
    print(f"📡 [일본 내각부] 뉴스룸 정밀 스캔 시작...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=20)
        response.encoding = 'utf-8' 
        soup = BeautifulSoup(response.text, 'html.parser')

        # 💡 [핵심] 일본 내각부 뉴스는 'main_list'라는 클래스나 'contents' 영역 안에 있습니다.
        # 가장 확실한 타겟 영역을 지정합니다.
        news_section = soup.find('div', id='contents') or soup.find('main')
        
        new_data = []
        existing_titles = set()
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader: existing_titles.add(row['제목'])

        if news_section:
            # 💡 <dt>(날짜)와 <dd>(제목/링크) 쌍을 찾습니다.
            dts = news_section.find_all('dt')
            
            count = 0
            for dt in dts:
                # 1. 날짜 추출
                date_text = dt.get_text().strip()
                
                # 2. 바로 다음 dd 태그에서 제목과 링크 추출
                dd = dt.find_next_sibling('dd')
                if not dd: continue
                
                a_tag = dd.find('a')
                if not a_tag: continue
                
                title = a_tag.get_text().strip()
                link = urljoin(target_url, a_tag['href'])
                
                # 3. 메뉴 링크 제외 로직 (최소 10자 이상, 특정 단어 제외)
                if len(title) > 10 and title not in existing_titles:
                    print(f"   🆕 뉴스 발견: [{date_text}] {title[:40]}...")
                    new_data.append({
                        "기관": "일본 내각부(CAO)",
                        "발행일": date_text,
                        "제목": title,
                        "링크": link,
                        "수집일": datetime.now().strftime("%Y-%m-%d")
                    })
                    count += 1
                    if count >= 5: break

        # 💾 결과 저장
        if new_data:
            file_exists = os.path.exists(file_name)
            with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "링크", "수집일"])
                if not file_exists: writer.writeheader()
                writer.writerows(new_data)
            print(f"✅ 성공! 진짜 뉴스 {len(new_data)}건을 저장했습니다.")
        else:
            print("❌ 뉴스 영역을 찾았으나 유효한 기사가 없습니다.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    main()
