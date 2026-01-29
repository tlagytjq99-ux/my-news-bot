import feedparser
import csv
import os
from datetime import datetime
from googletrans import Translator
import time

def main():
    rss_url = "https://www.mckinsey.com/insights/rss"
    file_name = 'mckinsey_ai_report.csv'
    translator = Translator()
    
    print(f"📡 [McKinsey] 데이터 정밀 가공 및 수집 시작...")

    try:
        feed = feedparser.parse(rss_url)
        new_data = []
        
        # 필터링 키워드
        ai_keywords = ['AI', 'TECH', 'DIGITAL', 'DATA', 'GEN', 'INTELLIGENCE', 'STRATEGY']

        for entry in feed.entries:
            title_en = entry.title
            link = entry.link
            
            # 1. 발행일 형식 변환 (yyyy-mm-dd)
            # RSS의 다양한 날짜 형식을 안전하게 변환합니다.
            raw_date = entry.get('published_parsed', None)
            if raw_date:
                published_date = time.strftime('%Y-%m-%d', raw_date)
            else:
                published_date = datetime.now().strftime("%Y-%m-%d")

            # 2. 수집일 생성 (오늘 날짜)
            collected_date = datetime.now().strftime("%Y-%m-%d")

            # 제목에 키워드가 포함된 경우만 수집
            if any(kw in title_en.upper() for kw in ai_keywords):
                try:
                    res = translator.translate(title_en, src='en', dest='ko')
                    title_ko = res.text
                except:
                    title_ko = title_en

                print(f"   ✅ [수집] {published_date} | {title_ko[:30]}...")
                
                new_data.append({
                    "기관": "McKinsey",
                    "발행일": published_date, # 변환된 날짜
                    "제목": title_ko,
                    "원문": title_en,
                    "링크": link,
                    "수집일": collected_date # 추가된 필드
                })
                if len(new_data) >= 15: break # 최대 15건

        # 💾 CSV 저장 (헤더 순서 조정)
        if new_data:
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                fieldnames = ["기관", "발행일", "제목", "원문", "링크", "수집일"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(new_data)
            print(f"🎉 성공! 모든 데이터가 'yyyy-mm-dd' 형식으로 정렬되어 저장되었습니다.")
        else:
            print("💡 조건에 맞는 최신 리포트가 없습니다.")

    except Exception as e:
        print(f"❌ 작업 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
