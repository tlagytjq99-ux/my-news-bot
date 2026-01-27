import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from googletrans import Translator
import time

def crawl_whitehouse_via_google():
    print("1. 구글을 통한 백악관 AI 뉴스 검색 시작...")
    # 구글에서 백악관 사이트 내 AI 키워드 검색 (최신순 정렬 시도)
    url = "https://www.google.com/search?q=site:whitehouse.gov+AI+news&tbs=qdr:m" # 최근 1개월 데이터
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    translator = Translator()
    collect_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        print("2. 구글 검색 결과 로드 성공!")
    except Exception as e:
        print(f"❌ 접속 실패: {e}")
        return

    news_items = []
    # 구글 검색 결과에서 링크와 제목 추출
    search_results = soup.select('.tF2Cxc') # 구글 검색 결과의 일반적인 클래스

    print(f"3. 검색된 {len(search_results)}개 항목 분석 중...")

    for res in search_results[:10]:
        title_tag = res.select_one('h3')
        link_tag = res.select_one('a')
        
        if not title_tag or not link_tag: continue
        
        title_en = title_tag.get_text()
        link = link_tag['href']
        
        # 백악관 브리핑룸 링크인지 최종 확인
        if 'whitehouse.gov/briefing-room' in link:
            try:
                print(f"   [발견] {title_en[:40]}...")
                title_ko = translator.translate(title_en, src='en', dest='ko').text
                time.sleep(1.2)
            except:
                title_ko = title_en

            news_items.append({
                "수집일": collect_date,
                "발행일": "최근",
                "기관": "White House (via Google)",
                "원문 제목": title_en,
                "한글 번역 제목": title_ko,
                "링크": link
            })

    df = pd.DataFrame(news_items) if news_items else pd.DataFrame(columns=["수집일", "발행일", "기관", "원문 제목", "한글 번역 제목", "링크"])
    df.to_excel("whitehouse_news.xlsx", index=False)
    print(f"4. 완료! 최종 {len(news_items)}건 저장됨.")

if __name__ == "__main__":
    crawl_whitehouse_via_google()
