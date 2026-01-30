import feedparser
import csv
import urllib.parse
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 검색어 최적화 (AI와 정책/전략/전망 위주)
    query = 'site:oecd.org "Artificial Intelligence" (Policy OR Strategy OR Outlook)'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    file_name = 'oecd_ai_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"📡 OECD 최신 Insight 5개 추출 시작...")
    raw_data = []

    try:
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries:
            title_en = entry.title.split(' - ')[0]
            link = entry.link
            
            # 날짜 파싱 및 객체 변환 (정렬을 위해 필요)
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_dt = datetime(*entry.published_parsed[:6])
                pub_date_str = pub_dt.strftime('%Y-%m-%d')
            else:
                continue # 날짜 없는 데이터는 버림

            raw_data.append({
                "기관": "OECD",
                "발행일": pub_date_str,
                "dt_obj": pub_dt, # 정렬용 임시 객체
                "제목_en": title_en,
                "링크": link
            })

        # 1️⃣ 최신순 정렬 (가장 최근에 올라온 것부터)
        raw_data.sort(key=lambda x: x['dt_obj'], reverse=True)

        # 2️⃣ 상위 5개만 선택
        final_5 = raw_data[:5]

        # 3️⃣ 번역 및 최종 데이터 구성
        final_data = []
        for item in final_5:
            try:
                title_ko = translator.translate(item['제목_en'], dest='ko').text
            except:
                title_ko = item['제목_en']
            
            final_data.append({
                "기관": "OECD",
                "발행일": item['발행일'],
                "제목": title_ko,
                "원문": item['제목_en'],
                "링크": item['링크'],
                "수집일": collected_date
            })

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    # 💾 저장 (데이터가 5개 미만이어도 정상 저장)
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        if final_data:
            writer.writerows(final_data)
            print(f"✅ 성공! 최신 리포트 5건을 선별하여 저장했습니다.")
        else:
            print("⚠️ 수집된 최신 데이터가 없습니다.")

if __name__ == "__main__":
    main()
