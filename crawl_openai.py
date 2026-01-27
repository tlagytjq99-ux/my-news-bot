import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
from googletrans import Translator
import time

def crawl_openai_rss():
    print("1. 수집 시작...")
    url = "https://openai.com/news/rss.xml"
    headers = {"User-Agent": "Mozilla/5.0"}
    translator = Translator()
    
    # 오늘 수집일 날짜 생성
    collect_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        root = ET.fromstring(response.content)
        print("2. RSS 데이터 가져오기 성공")
    except Exception as e:
        print(f"접속 에러: {e}")
        return

    news_items = []
    # [핵심] 최신 뉴스 10개만 선택 (818개 전체 번역 방지)
    items = root.findall(".//item")[:10]
    print(f"3. 최신 뉴스 {len(items)}개의 번역 및 수집 시작...")

    for i, item in enumerate(items):
        title_en = item.find("title").text
        link = item.find("link").text
        pub_date_raw = item.find("pubDate").text
        
        # 발행일 형식 변경 (yyyy-mm-dd)
        try:
            date_obj = datetime.strptime(pub_date_raw[5:16], "%d %b %Y")
            pub_date = date_obj.strftime("%Y-%m-%d")
        except:
            pub_date = pub_date_raw

        # 한글 번역
        try:
            print(f"   - {i+1}/{len(items)} 번역 중: {title_en[:30]}...")
            title_ko = translator.translate(title_en, src='en', dest='ko').text
            time.sleep(1) # 안정적인 번역을 위한 1초 휴식
        except Exception as e:
            print(f"   - 번역 실패 ({e})")
            title_ko = title_en

        news_items.append({
            "수집일": collect_date,
            "발행일": pub_date,
            "기관": "OpenAI",
            "원문 제목": title_en,
            "한글 번역 제목": title_ko,
            "링크": link
        })
    
    df = pd.DataFrame(news_items)
    # 컬럼 순서 고정
    df = df[["수집일", "발행일", "기관", "원문 제목", "한글 번역 제목", "링크"]]
    df.to_excel("openai_news.xlsx", index=False)
    print("4. 모든 과정 완료 및 엑셀 저장 성공!")

if __name__ == "__main__":
    crawl_openai_rss()
