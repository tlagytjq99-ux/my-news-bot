import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
from googletrans import Translator
import time
import os  # 파일 존재 여부 확인을 위해 필요

def crawl_openai_rss():
    file_name = "openai_news.xlsx"
    print("1. 수집 및 누적 프로세스 시작...")
    
    url = "https://openai.com/news/rss.xml"
    headers = {"User-Agent": "Mozilla/5.0"}
    translator = Translator()
    collect_date = datetime.now().strftime("%Y-%m-%d")
    
    # 📂 [중요] 기존 데이터 불러오기
    existing_df = pd.DataFrame()
    existing_links = []
    if os.path.exists(file_name):
        try:
            existing_df = pd.read_excel(file_name)
            existing_links = existing_df['링크'].tolist()  # 이미 수집된 링크 리스트
            print(f"   - 기존 데이터 {len(existing_df)}건을 로드했습니다.")
        except Exception as e:
            print(f"   - 기존 파일을 읽는 중 오류 발생(무시하고 새로 생성): {e}")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        root = ET.fromstring(response.content)
        print("2. RSS 데이터 가져오기 성공")
    except Exception as e:
        print(f"접속 에러: {e}")
        return

    news_items = []
    items = root.findall(".//item")[:15] # 최신 15개 확인
    
    new_count = 0
    for i, item in enumerate(items):
        link = item.find("link").text
        
        # 🛡️ [중복 체크] 이미 엑셀에 있는 링크라면 건너뜁니다.
        if link in existing_links:
            continue
            
        title_en = item.find("title").text
        pub_date_raw = item.find("pubDate").text
        
        # 발행일 형식 변경 (yyyy-mm-dd)
        try:
            # RSS 날짜 예시: "Wed, 28 Jan 2026 10:00:00 GMT" -> "2026-01-28"
            date_part = pub_date_raw[5:16]
            date_obj = datetime.strptime(date_part, "%d %b %Y")
            pub_date = date_obj.strftime("%Y-%m-%d")
        except:
            pub_date = pub_date_raw

        # 한글 번역
        try:
            print(f"   - [신규 기사] 번역 중: {title_en[:30]}...")
            title_ko = translator.translate(title_en, src='en', dest='ko').text
            time.sleep(1.2) # 번역 API 차단 방지
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
        new_count += 1
    
    if new_count > 0:
        new_df = pd.DataFrame(news_items)
        # 기존 데이터와 새 데이터를 합칩니다.
        final_df = pd.concat([new_df, existing_df], ignore_index=True)
        
        # 발행일 기준 최신순 정렬
        final_df = final_df.sort_values(by="발행일", ascending=False)
        
        # 저장
        final_df.to_excel(file_name, index=False)
        print(f"4. 완료! 신규 {new_count}건이 추가되어 총 {len(final_df)}건이 저장되었습니다.")
    else:
        print("4. 업데이트할 새로운 기사가 없습니다.")

if __name__ == "__main__":
    crawl_openai_rss()
