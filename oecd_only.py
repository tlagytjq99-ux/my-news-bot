import feedparser
import csv
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 우회 전술: 구글 뉴스를 통해 OECD AI 정책 소식만 필터링해서 가져옴
    # 검색어: site:oecd.org "Artificial Intelligence"
    query = 'site:oecd.org "Artificial Intelligence"'
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    
    file_name = 'oecd_ai_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"📡 구글 뉴스를 통해 OECD 데이터 우회 수집 시작...")
    new_data = []

    try:
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            print("⚠️ 검색 결과가 없습니다.")
        else:
            print(f"🔍 총 {len(feed.entries)}건의 데이터 발견. 분석 중...")

            for entry in feed.entries[:20]: # 최신 20건
                title_en = entry.title
                # 구글 뉴스 제목은 '제목 - 매체명' 형식이므로 분리
                title_en = title_en.split(' - ')[0]
                link = entry.link
                
                # 날짜 처리
                published_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d')

                # 한국어 번역
                try:
                    title_ko = translator.translate(title_en, dest='ko').text
                except:
                    title_ko = title_en

                new_data.append({
                    "기관": "OECD",
                    "발행일": published_date,
                    "제목": title_ko,
                    "원문": title_en,
                    "링크": link,
                    "수집일": collected_date
                })

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    # 💾 결과 저장 (데이터가 없어도 빈 파일은 생성)
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        if new_data:
            writer.writerows(new_data)
            print(f"✅ {len(new_data)}건의 데이터를 구글 우회 방식으로 확보했습니다!")
        else:
            print("⚠️ 수집된 데이터가 없습니다.")

if __name__ == "__main__":
    main()
