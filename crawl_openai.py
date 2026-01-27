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
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        root = ET.fromstring(response.content)
        print("2. RSS 데이터 가져오기 성공")
    except Exception as e:
        print(f"접속 에러: {e}")
        return

    news_items = []
    items = root.findall(".//item")[:5] # 시뮬레이션을 위해 우선 5개만 테스트해봅시다.
    print(f"3. 총 {len(items)}개의 뉴스 번역 시작...")

    for i, item in enumerate(items):
        title_en = item.find("title").text
        link = item.find("link").text
        pub_date_raw = item.find("pubDate").text
        
        # 날짜 변환
        try:
            date_obj = datetime.strptime(pub_date_raw[5:16], "%d %b %Y")
            pub_date = date_obj.strftime("%Y-%m-%d")
        except:
            pub_date = pub_date_raw

        # 번역 (여기가 멈추는 구간일 확률이 높음)
        try:
            print(f"   - {i+1}번 뉴스 번역 중...")
            title_ko = translator.translate(title_en, src='en', dest='ko').text
            time.sleep(1) # 차단 방지를 위한 1초 휴식
        except Exception as e:
            print(f"   - 번역 실패 ({e})")
            title_ko = title_en # 실패 시 영어 제목 그대로 사용

        news_items.append({
            "발행일": pub_date,
            "기관": "OpenAI",
            "원문 제목": title_en,
            "한글 번역 제목": title_ko,
            "링크": link
        })
    
    df = pd.DataFrame(news_items)
    df.to_excel("openai_news.xlsx", index=False)
    print("4. 모든 과정 완료 및 엑셀 저장 성공!")

if __name__ == "__main__":
    crawl_openai_rss()
