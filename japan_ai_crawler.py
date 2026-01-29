import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
from urllib.parse import urljoin

def main():
    # 🎯 타겟: 일본 내각부 과학기술혁신(AI/신기술) 소식 페이지
    target_url = "https://www8.cao.go.jp/cstp/stmain/index.html"
    file_name = 'japan_ai_report.csv'
    
    print(f"📡 [일본 내각부] AI 정책 데이터 수집을 시작합니다...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=20)
        response.encoding = response.apparent_encoding # 일본어 인코딩 처리
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 일본 사이트 구조 분석 (최신 뉴스 리스트 영역)
        news_list = soup.find('dl', class_='top_news') or soup.find('dl')

        new_data = []
        existing_titles = set()

        # 기존에 저장된 데이터가 있다면 중복 수집 방지
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_titles.add(row['제목'])

        # AI 및 기술 관련 일본어 핵심 키워드
        # AI(인공지능), 人工知能(인공지능), デジタル(디지털), 戦略(전략), 技術(기술)
        ai_keywords = ['AI', '人工知能', 'デジタル', '戦略', '技術', '데이터']

        count = 0
        dts = news_list.find_all('dt') if news_list else []
        
        for dt in dts:
            if count >= 5: break
            
            # 날짜 추출
            date_text = dt.get_text().strip()
            # 제목 및 링크 추출
            dd = dt.find_next_sibling('dd')
            if not dd: continue
            
            a_tag = dd.find('a')
            if not a_tag: continue
            
            title = a_tag.get_text().strip()
            link = urljoin(target_url, a_tag['href'])
            
            # 필터링: 제목에 키워드가 있고, 기존에 없던 새로운 제목일 때만 저장
            if any(kw in title.upper() for kw in ai_keywords):
                if title not in existing_titles:
                    print(f"   🆕 새 정책 발견: {title[:40]}...")
                    new_data.append({
                        "기관": "일본 내각부(CAO)",
                        "발행일": date_text.replace('年', '-').replace('月', '-').replace('日', '').strip(),
                        "제목": title,
                        "링크": link,
                        "수집일": datetime.now().strftime("%Y-%m-%d")
                    })
                    count += 1

        # 💾 결과 저장 (기존 데이터 뒤에 추가하는 Append 모드)
        if new_data:
            file_exists = os.path.exists(file_name)
            with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "링크", "수집일"])
                if not file_exists:
                    writer.writeheader()
                writer.writerows(new_data)
            print(f"✅ 성공! 일본 정책 데이터 {len(new_data)}건이 업데이트되었습니다.")
        else:
            print("💡 새로운 일본 AI 정책 소식이 없습니다.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    main()
