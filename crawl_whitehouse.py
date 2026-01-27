import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from googletrans import Translator
import time

def crawl_whitehouse_search():
    print("1. 백악관 검색 엔진 공략 시작 (키워드: AI)...")
    # AI로 검색했을 때의 결과 페이지 URL
    url = "https://www.whitehouse.gov/?s=AI"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    translator = Translator()
    collect_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        print("2. 검색 결과 페이지 로드 성공!")
    except Exception as e:
        print(f"❌ 접속 실패: {e}")
        return

    news_items = []
    # 검색 결과 리스트 추출
    # 검색 결과는 보통 'article' 태그나 특정 클래스의 'div'에 담깁니다.
    results = soup.find_all('h2', class_='result__title') or soup.find_all('article')
    
    print(f"3. 검색 결과 {len(results)}개 분석 중...")

    for res in results[:10]: # 최신 검색 결과 10개만
        link_tag = res.find('a')
        if not link_tag: continue
        
        title_en = link_tag.get_text(strip=True)
        link = link_tag['href']
        
        # 실제 뉴스 기사(briefing-room)인 것만 필터링
        if '/briefing-room/' in link:
            try:
                print(f"   [검색발견] {title_en[:40]}...")
                title_ko = translator.translate(title_en, src='en', dest='ko').text
                time.sleep(1.2)
            except:
                title_ko = title_en

            news_items.append({
                "수집일": collect_date,
                "발행일": "검색결과",
                "기관": "White House (Search)",
                "원문 제목": title_en,
                "한글 번역 제목": title_ko,
                "링크": link
            })

    df = pd.DataFrame(news_items) if news_items else pd.DataFrame(columns=["수집일", "발행일", "기관", "원문 제목", "한글 번역 제목", "링크"])
    df.to_excel("whitehouse_news.xlsx", index=False)
    print(f"4. 완료! 검색 결과 {len(news_items)}건 저장됨.")

if __name__ == "__main__":
    crawl_whitehouse_search()
