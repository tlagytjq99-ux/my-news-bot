import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
from googletrans import Translator
import time

def crawl_whitehouse_ai():
    print("1. 백악관 뉴스룸 공략 시작...")
    # 알려주신 news 페이지의 데이터를 담고 있는 공식 RSS 피드입니다.
    url = "https://www.whitehouse.gov/feed/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    translator = Translator()
    collect_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # 1. 페이지 접속
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status() 
        
        # 2. 데이터 파싱
        root = ET.fromstring(response.content)
        print("2. 백악관 데이터 수신 성공!")
        
    except Exception as e:
        print(f"❌ 접속 실패: {e}")
        # 에러 시 빈 파일 생성 (워크플로우 중단 방지)
        pd.DataFrame(columns=["수집일", "발행일", "기관", "원문 제목", "한글 번역 제목", "링크"]).to_excel("whitehouse_news.xlsx", index=False)
        return

    news_items = []
    # RSS 피드 내의 각 뉴스 항목(item) 추출
    items = root.findall(".//item")
    
    # AI 및 핵심 기술 키워드
    ai_keywords = ["AI", "Artificial Intelligence", "Technology", "Cyber", "Quantum", "Semiconductor", "Digital", "Security"]
    
    print(f"3. 총 {len(items)}개 뉴스 중 AI 관련 뉴스 필터링 시작...")

    for item in items:
        title_en = item.find("title").text
        link = item.find("link").text
        pub_date_raw = item.find("pubDate").text # 예: Tue, 27 Jan 2026...

        # 제목에 키워드가 포함되어 있는지 검사
        if any(kw.lower() in title_en.lower() for kw in ai_keywords):
            # 날짜 변환 (yyyy-mm-dd)
            try:
                date_obj = datetime.strptime(pub_date_raw[5:16], "%d %b %Y")
                pub_date = date_obj.strftime("%Y-%m-%d")
            except:
                pub_date = pub_date_raw[:16]

            # 번역 처리
            try:
                print(f"   [발견] {title_en[:50]}...")
                title_ko = translator.translate(title_en, src='en', dest='ko').text
                time.sleep(1.5) # 번역기 차단 방지용
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
            
            # 너무 많으면 시간이 걸리니 최신 10개만
            if len(news_items) >= 10: break

    # 데이터 저장
    if news_items:
        df = pd.DataFrame(news_items)
        print(f"✅ 총 {len(news_items)}건의 백악관 AI 뉴스 수집 완료!")
    else:
        print("🔎 최근 AI 관련 뉴스가 없습니다. 빈 엑셀을 생성합니다.")
        df = pd.DataFrame(columns=["수집일", "발행일", "기관", "원문 제목", "한글 번역 제목", "링크"])
    
    df.to_excel("whitehouse_news.xlsx", index=False)

if __name__ == "__main__":
    crawl_whitehouse_ai()
