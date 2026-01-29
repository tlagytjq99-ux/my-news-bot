import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
from urllib.parse import urljoin

def main():
    # 🎯 타겟: 내각부 보도발표(News Release) 전용 페이지
    # 이곳은 구조가 비교적 일정해서 뉴스만 골라내기 좋습니다.
    target_url = "https://www.cao.go.jp/houdou/houdou.html"
    file_name = 'japan_ai_report.csv'
    
    print(f"📡 [일본 내각부] 보도자료 정밀 수집 시작...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=20)
        response.encoding = 'utf-8' 
        soup = BeautifulSoup(response.text, 'html.parser')

        # 💡 [핵심] 뉴스 아이템은 보통 'main_list' 클래스의 <li> 안에 있습니다.
        # 혹은 <dt>(날짜) <dd>(제목) 구조를 찾습니다.
        new_data = []
        existing_titles = set()
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader: existing_titles.add(row['제목'])

        # 뉴스 본문 영역 찾기
        content_area = soup.find('div', id='main_list') or soup.find('div', id='contents')
        
        if content_area:
            # 💡 뉴스 리스트의 <a> 태그들만 추출
            items = content_area.find_all('a', href=True)
            
            count = 0
            for a in items:
                title = a.get_text().strip()
                link = urljoin(target_url, a['href'])
                
                # 💡 [필터링]
                # 1. 제목에 '내각부' 같은 단순 사이트명 제외
                # 2. 이미 수집한 제목 제외
                # 3. 주소에 houdou(보도)나 기사 형식이 포함된 것
                if len(title) > 15 and title not in existing_titles:
                    if 'index.html' not in link[-10:]: # 단순 메인페이지 링크 제외
                        
                        print(f"   🆕 뉴스 발견: {title[:40]}...")
                        new_data.append({
                            "기관": "일본 내각부(CAO)",
                            "발행일": datetime.now().strftime("%Y-%m-%d"),
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
            print(f"✅ 성공! {len(new_data)}건의 보도자료 수집 완료.")
        else:
            print("❌ 실제 뉴스 영역을 찾는 데 실패했습니다. 타겟을 다시 조정합니다.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    main()
