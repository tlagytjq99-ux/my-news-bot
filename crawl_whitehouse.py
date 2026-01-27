import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
from googletrans import Translator
import time

def crawl_whitehouse_ai():
    print("1. 백악관 뉴스 수집 시작...")
    # 백악관 보도자료 RSS (가장 공식적인 채널)
    url = "https://www.whitehouse.go/briefing-room/statements-releases/feed/"
    headers = {"User-Agent": "Mozilla/5.0"}
    translator = Translator()
    
    collect_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        root = ET.fromstring(response.content)
    except Exception as e:
        print(f"접속 에러: {e}")
        return

    news_items = []
    items = root.findall(".//item")
    
    # AI 관련 뉴스만 필터링 (최신 50개 중 검색)
    count = 0
    for item in items[:50]:
        title_en = item.find("title").text
        link = item.find("link").text
        pub_date_raw = item.find("pubDate").text # 예: Tue, 27 Jan 2026...

        # AI 관련 키워드가 있는지 확인 (필터링)
        keywords = ["AI", "Artificial Intelligence", "Technology", "Tech", "Cyber", "Quantum"]
        if any(kw.lower() in title_en.lower() for kw in keywords):
            
            # 날짜 변환
            try:
                date_obj = datetime.strptime(pub_date_raw[5:16], "%d %b %Y")
                pub_date = date_obj.strftime("%Y-%m-%d")
            except:
                pub_date = pub_date_raw

            # 한글 번역
            try:
                title_ko = translator.translate(title_en, src='en', dest='ko').text
                time.sleep(1)
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
            count += 1
            if count >= 10: break # 최신 AI 뉴스 10개만

    if news_items:
        df = pd.DataFrame(news_items)
        df.to_excel("whitehouse_news.xlsx", index=False)
        print(f"✅ 백악관 뉴스 {len(news_items)}건 수집 완료!")
    else:
        print("🔎 최근 AI 관련 백악관 뉴스가 없습니다.")

if __name__ == "__main__":
    crawl_whitehouse_ai()
