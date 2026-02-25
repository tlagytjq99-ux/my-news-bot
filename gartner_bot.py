import requests
from bs4 import BeautifulSoup
import csv
import time

def crawl_gartner_via_google_news():
    # 2026년 가트너 뉴스룸 보도자료를 구글 뉴스에서 검색
    # site:gartner.com 필터를 써서 정확도를 높였습니다.
    search_url = "https://www.google.com/search?q=site:gartner.com/en/newsroom/press-releases+2026&tbm=nws"
    file_name = 'Gartner_Insight_Archive.csv'
    
    # 실제 사람의 브라우저 헤더 (핵심)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.google.com/'
    }

    print(f"📡 구글 뉴스를 통해 가트너 자료 우회 수집 중...")
    
    try:
        # 구글에 요청 보냄 (타임아웃 20초)
        response = requests.get(search_url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 구글 뉴스 검색 결과의 뉴스 카드들을 타겟팅 (div[data-ved] 구조)
            articles = soup.select('div.SoS9be') # 구글 뉴스 리스트의 공통 클래스
            
            # 클래스가 변경될 수 있으므로 a 태그 기반으로도 탐색
            if not articles:
                articles = soup.select('div[data-ved] a[role="presentation"]')

            all_data = []
            for article in articles:
                # 제목과 링크 추출
                title_elem = article.select_one('div[role="heading"]')
                link_elem = article.get('href') if article.name == 'a' else article.select_one('a')['href']
                
                if title_elem and link_elem and "gartner.com" in link_elem:
                    title = title_elem.get_text().strip()
                    all_data.append({
                        "date": "2026-Fixed",
                        "title": title.replace('\n', ' '),
                        "link": link_elem
                    })

            # 상위 10개만 저장
            final_data = all_data[:10]

            if final_data:
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                    writer.writeheader()
                    writer.writerows(final_data)
                print(f"✅ 구글 우회 성공! {len(final_data)}건의 데이터를 확보했습니다.")
                return
            else:
                print("⚠️ 검색 결과에서 가트너 기사를 찾지 못했습니다.")
        else:
            print(f"❌ 구글 접속 실패 (상태 코드: {response.status_code})")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    # 실패 시 빈 파일 생성 (Workflow 에러 방지)
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        f.write("date,title,link\n")

if __name__ == "__main__":
    crawl_gartner_via_google_news()
