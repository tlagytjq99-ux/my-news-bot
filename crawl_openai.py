import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
from googletrans import Translator

def crawl_openai_rss():
    url = "https://openai.com/news/rss.xml"
    headers = {"User-Agent": "Mozilla/5.0"}
    translator = Translator()
    
    try:
        response = requests.get(url, headers=headers)
        root = ET.fromstring(response.content)
    except Exception as e:
        print(f"접속 에러: {e}")
        return

    news_items = []
    
    for item in root.findall(".//item"):
        title_en = item.find("title").text
        link = item.find("link").text
        pub_date_raw = item.find("pubDate").text
        
        # 1. 날짜 형식 변경 (예: Wed, 22 Jan 2026 -> 2026-01-22)
        try:
            # RSS 날짜 표준 형식 파싱 (RFC 822)
            date_obj = datetime.strptime(pub_date_raw[5:16], "%d %b %Y")
            pub_date = date_obj.strftime("%Y-%m-%d")
        except:
            pub_date = pub_date_raw

        # 2. 한글 번역
        try:
            title_ko = translator.translate(title_en, src='en', dest='ko').text
        except:
            title_ko = "번역 오류"

        news_items.append({
            "발행일": pub_date,
            "기관": "OpenAI",
            "원문 제목": title_en,
            "한글 번역 제목": title_ko,
            "링크": link
        })
    
    # 데이터프레임 생성 및 엑셀 저장
    df = pd.DataFrame(news_items)
    df.to_excel("openai_news.xlsx", index=False)
    print(f"성공: {len(df)}건의 뉴스 수집 및 번역 완료")

if __name__ == "__main__":
    crawl_openai_rss()
