import feedparser
import csv
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 OECD AI 정책 관련 공식 RSS 피드 (가장 안정적)
    oecd_rss_url = "https://www.oecd.org/en/topics/subtopics/artificial-intelligence/jcr:content/feed"
    
    file_name = 'oecd_ai_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    new_data = []
    print(f"📡 [OECD RSS] 데이터 수집 시작...")

    try:
        feed = feedparser.parse(oecd_rss_url)
        for entry in feed.entries[:15]:
            title_en = entry.title
            link = entry.link
            
            try:
                title_ko = translator.translate(title_en, dest='ko').text
            except:
                title_ko = title_en

            new_data.append({
                "기관": "OECD", "발행일": collected_date,
                "제목": title_ko, "원문": title_en, "링크": link, "수집일": collected_date
            })
    except Exception as e:
        print(f"❌ 에러: {e}")

    # 파일 저장 (데이터가 없어도 헤더는 생성)
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        if new_data:
            writer.writerows(new_data)
            print(f"✅ {len(new_data)}건 수집 완료!")

if __name__ == "__main__":
    main()
