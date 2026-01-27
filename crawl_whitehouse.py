import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
from googletrans import Translator
import time

def crawl_whitehouse_ai():
    print("1. 백악관 뉴스 수집 시작...")
    # 백악관 브리핑룸 RSS 피드
    url = "https://www.whitehouse.gov/briefing-room/statements-releases/feed/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    translator = Translator()
    
    collect_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        root = ET.fromstring(response.content)
        print("2. RSS 데이터 가져오기 성공")
    except Exception as e:
        print(f"접속 에러: {e}")
        return

    news_items = []
    items = root.findall(".//item")
    
    # AI 관련 핵심 키워드
    ai_keywords = ["AI", "Artificial Intelligence", "Technology", "Quantum", "Cyber", "Semiconductor", "Chip"]
    count = 0

    for item in items:
        title_en = item.find("title").text
        link = item.find("link").text
        pub_date_raw = item.find("pubDate").text

        # AI 관련 키워드가 포함된 경우만 수집
        if any(kw.lower() in title_en.lower() for kw in ai_keywords):
            # 날짜 변환 (yyyy-mm-dd)
            try:
                date_obj = datetime.strptime(pub_date_raw[5:16], "%d %b %Y")
                pub_date = date_obj.strftime("%Y-%m-%d")
            except:
                pub_date = pub_date_raw

            # 한글 번역
            try:
                print(f"   - 번역 중: {title_en[:30]}...")
                title_ko = translator.translate(title_en, src='en', dest='ko').text
                time.sleep(1) # 차단 방지
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
            if count >= 10: break # 최신 AI 뉴스 10개까지만

    if news_items:
        df = pd.DataFrame(news_items)
        df.to_excel("whitehouse_news.xlsx", index=False)
        print(f"✅ 백악관 AI 뉴스 {len(news_items)}건 저장 완료!")
    else:
        print("🔎 최근 AI 관련 백악관 뉴스가 없습니다.")

if __name__ == "__main__":
    crawl_whitehouse_ai()
