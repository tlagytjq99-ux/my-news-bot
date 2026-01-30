import feedparser
import csv
import urllib.parse
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 검색 필터 강화: 제목에 반드시 AI 관련 단어가 포함된 OECD 결과만 검색
    # intitle:"Artificial Intelligence" OR intitle:AI
    query = 'site:oecd.org (intitle:"Artificial Intelligence" OR intitle:AI) -intitle:PISA'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    file_name = 'oecd_ai_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"📡 OECD 최신 AI 리포트(Top 5) 정밀 수집 시작...")
    raw_data = []

    try:
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries:
            title_en = entry.title.split(' - ')[0]
            link = entry.link
            
            # 💡 [2차 필터] 제목에 AI 관련 핵심 키워드가 없는 경우 제외
            keywords = ['AI', 'ARTIFICIAL INTELLIGENCE', 'ALGORITHMS', 'GENERATIVE']
            if not any(kw in title_en.upper() for kw in keywords):
                continue

            # 날짜 파싱 및 객체 변환
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_dt = datetime(*entry.published_parsed[:6])
                pub_date_str = pub_dt.strftime('%Y-%m-%d')
            else:
                continue

            raw_data.append({
                "기관": "OECD",
                "발행일": pub_date_str,
                "dt_obj": pub_dt,
                "제목_en": title_en,
                "링크": link
            })

        # 1️⃣ 최신순 정렬
        raw_data.sort(key=lambda x: x['dt_obj'], reverse=True)

        # 2️⃣ 최상위 5개만 선택
        final_5 = raw_data[:5]

        # 3️⃣ 번역 및 데이터 구성
        final_data = []
        for item in final_5:
            try:
                # 번역 품질을 위해 앞뒤 공백 제거
                title_ko = translator.translate(item['제목_en'].strip(), dest='ko').text
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

    # 💾 결과 저장
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        if final_data:
            writer.writerows(final_data)
            print(f"✅ 성공! 최신 AI 핵심 리포트 {len(final_data)}건 저장 완료.")
        else:
            print("⚠️ 조건에 맞는 최신 AI 리포트가 발견되지 않았습니다.")

if __name__ == "__main__":
    main()
