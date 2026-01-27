import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from googletrans import Translator
import time

def crawl_whitehouse_ai():
    print("1. 백악관 뉴스룸 웹 크롤링 시작...")
    url = "https://www.whitehouse.gov/news/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    translator = Translator()
    collect_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        print("2. 페이지 로드 성공!")
    except Exception as e:
        print(f"❌ 접속 실패: {e}")
        # 실패 시 빈 엑셀 생성하여 워크플로우 중단 방지
        pd.DataFrame(columns=["수집일", "발행일", "기관", "원문 제목", "한글 번역 제목", "링크"]).to_excel("whitehouse_news.xlsx", index=False)
        return

    news_items = []
    # 백악관 뉴스룸의 기사 제목과 링크 추출 (현재 사이트 구조 기준)
    # <a> 태그 중 /briefing-room/ 경로를 포함하는 기사 링크들을 찾습니다.
    articles = soup.find_all('a', href=True)
    
    ai_keywords = ["AI", "Artificial Intelligence", "Technology", "Cyber", "Quantum", "Semiconductor", "Digital", "Security"]
    seen_titles = set()
    
    print(f"3. AI 관련 뉴스 필터링 시작...")

    for article in articles:
        title_en = article.get_text(strip=True)
        link = article['href']
        
        # 기사 제목이 너무 짧거나 중복된 경우 제외
        if len(title_en) < 20 or title_en in seen_titles:
            continue
        
        # AI 관련 키워드 확인 및 브리핑룸 링크인지 확인
        if any(kw.lower() in title_en.lower() for kw in ai_keywords) and '/briefing-room/' in link:
            if not link.startswith('http'):
                link = f"https://www.whitehouse.gov{link}"
            
            seen_titles.add(title_en)
            pub_date = collect_date # 목록 페이지에는 날짜 형식이 다양하므로 수집일로 대체

            try:
                print(f"   [발견] {title_en[:50]}...")
                title_ko = translator.translate(title_en, src='en', dest='ko').text
                time.sleep(1.2)
            except:
                title_ko = title_en

            news_items.append({
                "수집일": collect_date,
                "발행일": pub_date,
                "기관": "White House",
                "원문 제목": title_en,
                "한글 번역 제목": title_ko,
                "링크": link
            })
            if len(news_items) >= 10: break

    # 엑셀 저장
    df = pd.DataFrame(news_items) if news_items else pd.DataFrame(columns=["수집일", "발행일", "기관", "원문 제목", "한글 번역 제목", "링크"])
    df.to_excel("whitehouse_news.xlsx", index=False)
    print(f"4. 완료! 수집 건수: {len(news_items)}")

if __name__ == "__main__":
    crawl_whitehouse_ai()
