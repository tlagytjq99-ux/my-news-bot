import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
from urllib.parse import urljoin

def main():
    # 🎯 타겟: 내각부 전체 신착 정보 (가장 데이터가 많은 페이지)
    target_url = "https://www.cao.go.jp/new/index.html"
    file_name = 'japan_ai_report.csv'
    
    print(f"📡 [일본 내각부] AI 키워드 탐색 모드 가동...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=20)
        response.encoding = response.apparent_encoding 
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. 페이지 내 모든 링크(a)를 다 긁어모읍니다.
        links = soup.find_all('a', href=True)
        
        new_data = []
        existing_titles = set()
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader: existing_titles.add(row['제목'])

        # 💡 [핵심] 일본 정부가 AI 정책에 쓰는 핵심 단어들
        # 人工知能(인공지능), 戦略(전략), デジタル(디지털), 報告(보고), 決定(결정)
        # 테스트를 위해 AI가 포함된 '전략'이나 '기술' 키워드도 포함합니다.
        ai_keywords = ['AI', '人工知能', '戦略', '技術', 'デジタル', '会議']

        count = 0
        for a in links:
            title = a.get_text().strip()
            link = urljoin(target_url, a['href'])
            
            # 2. 필터링: 제목에 키워드가 있고, 너무 짧지 않으며, 중복이 아닐 때
            if any(kw in title.upper() for kw in ai_keywords):
                if len(title) > 10 and title not in existing_titles:
                    
                    # 일본 사이트 특유의 날짜 패턴을 제목에서 찾거나 오늘 날짜 사용
                    print(f"   🆕 새 정책 소식 발견: {title[:40]}...")
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
            print(f"✅ 성공! 일본 AI 관련 데이터 {len(new_data)}건 수집 완료.")
        else:
            print("💡 현재 일본 내각부 최신 소식 중 AI 관련 키워드가 포함된 기사가 없습니다.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    main()
