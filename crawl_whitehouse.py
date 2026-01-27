import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
from googletrans import Translator
import time

def crawl_whitehouse_ai():
    print("1. 백악관 뉴스 수집 시작...")
    url = "https://www.whitehouse.gov/briefing-room/statements-releases/feed/"
    
    # [수정] 실제 브라우저처럼 보이도록 헤더 보강
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8"
    }
    
    translator = Translator()
    collect_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        # 응답 상태 확인
        response.raise_for_status() 
        
        # XML 데이터가 비어있는지 확인
        if not response.content.strip():
            print("❌ 서버에서 빈 데이터를 보냈습니다.")
            return

        root = ET.fromstring(response.content)
        print("2. RSS 데이터 가져오기 성공")
        
    except ET.ParseError as e:
        print(f"❌ XML 파싱 에러 (형식 문제): {e}")
        # 에러 발생 시 로그 출력을 위해 앞부분 100자만 출력해봅니다.
        print(f"응답 내용 요약: {response.text[:100]}")
        return
    except Exception as e:
        print(f"❌ 접속 또는 기타 에러: {e}")
        return

    news_items = []
    items = root.findall(".//item")
    ai_keywords = ["AI", "Artificial Intelligence", "Technology", "Quantum", "Cyber", "Semiconductor", "Chip", "Security"]
    
    for item in items[:50]:
        title_tag = item.find("title")
        link_tag = item.find("link")
        pub_tag = item.find("pubDate")
        
        if title_tag is None: continue
        
        title_en = title_tag.text
        link = link_tag.text if link_tag is not None else ""
        pub_date_raw = pub_tag.text if pub_tag is not None else ""

        if any(kw.lower() in title_en.lower() for kw in ai_keywords):
            try:
                date_obj = datetime.strptime(pub_date_raw[5:16], "%d %b %Y")
                pub_date = date_obj.strftime("%Y-%m-%d")
            except:
                pub_date = pub_date_raw[:16] if pub_date_raw else ""

            try:
                print(f"   - 번역 중: {title_en[:30]}...")
                title_ko = translator.translate(title_en, src='en', dest='ko').text
                time.sleep(1.5) # 번역기 차단 방지용 여유 시간 증가
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

    # 에러 방지를 위한 엑셀 저장 (데이터가 없으면 빈 틀만 생성)
    df = pd.DataFrame(news_items) if news_items else pd.DataFrame(columns=["수집일", "발행일", "기관", "원문 제목", "한글 번역 제목", "링크"])
    df.to_excel("whitehouse_news.xlsx", index=False)
    print(f"3. 모든 과정 완료! 수집된 뉴스: {len(news_items)}건")

if __name__ == "__main__":
    crawl_whitehouse_ai()
