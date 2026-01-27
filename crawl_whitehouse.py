import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
from googletrans import Translator
import time
import os

def crawl_whitehouse_ai():
    print("1. 백악관 뉴스 수집 시작...")
    url = "https://www.whitehouse.gov/briefing-room/statements-releases/feed/"
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
    ai_keywords = ["AI", "Artificial Intelligence", "Technology", "Quantum", "Cyber", "Semiconductor", "Chip", "Security"]
    
    for item in items[:50]:
        title_en = item.find("title").text
        link = item.find("link").text
        pub_date_raw = item.find("pubDate").text

        if any(kw.lower() in title_en.lower() for kw in ai_keywords):
            try:
                date_obj = datetime.strptime(pub_date_raw[5:16], "%d %b %Y")
                pub_date = date_obj.strftime("%Y-%m-%d")
            except:
                pub_date = pub_date_raw

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
            if len(news_items) >= 10: break

    # [수정] 데이터가 없더라도 빈 파일이라도 생성하여 깃허브 에러 방지
    if not news_items:
        print("🔎 최근 AI 관련 백악관 뉴스가 없습니다. 빈 파일을 생성합니다.")
        df = pd.DataFrame(columns=["수집일", "발행일", "기관", "원문 제목", "한글 번역 제목", "링크"])
    else:
        df = pd.DataFrame(news_items)
        print(f"✅ 백악관 AI 뉴스 {len(news_items)}건 수집 완료!")

    df.to_excel("whitehouse_news.xlsx", index=False)

if __name__ == "__main__":
    crawl_whitehouse_ai()
