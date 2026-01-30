import feedparser
import csv
import os
import time
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 직접 접속 대신 '뉴스 중계망'을 통한 안정적 수집
    sources = [
        {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
        {"name": "MIT_Sloan", "url": "https://sloanreview.mit.edu/feed/"},
        # 💡 Deloitte: 구글 뉴스가 수집한 딜로이트 인사이트 (차단 불가능)
        {"name": "Deloitte", "url": "https://news.google.com/rss/search?q=site:deloitte.com/insights+AI&hl=en-US&gl=US&ceid=US:en"},
        # 💡 BCG: 구글 뉴스가 수집한 BCG 최신 리포트
        {"name": "BCG", "url": "https://news.google.com/rss/search?q=site:bcg.com+AI&hl=en-US&gl=US&ceid=US:en"}
    ]
    
    file_name = 'ai_market_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📡 [보안 우회형 통합 엔진] 수집 시작...")

    new_data = []
    ai_keywords = ['AI', 'GEN', 'DIGITAL', 'TECH', 'INTELLIGENCE', 'DATA', 'FUTURE']

    for source in sources:
        print(f"🔍 {source['name']} 분석 중...")
        try:
            # 구글 뉴스 서버를 거치기 때문에 404 에러가 나지 않습니다.
            feed = feedparser.parse(source['url'])
            
            if not feed.entries:
                print(f"   ⚠️ {source['name']} 피드가 현재 비어 있습니다.")
                continue

            count = 0
            for entry in feed.entries:
                title_en = entry.title.split(' - ')[0] # 구글 뉴스 특유의 출처 표기 제거
                link = entry.link
                
                raw_date = entry.get('published_parsed', None)
                published_date = time.strftime('%Y-%m-%d', raw_date) if raw_date else collected_date

                if any(kw in title_en.upper() for kw in ai_keywords):
                    try:
                        res = translator.translate(title_en, src='en', dest='ko')
                        title_ko = res.text
                    except:
                        title_ko = title_en

                    new_data.append({
                        "기관": source['name'],
                        "발행일": published_date,
                        "제목": title_ko,
                        "원문": title_en,
                        "링크": link,
                        "수집일": collected_date
                    })
                    count += 1
                    if count >= 10: break
            
            print(f"   ✅ {source['name']}에서 {count}건 확보 완료!")

        except Exception as e:
            print(f"   ❌ {source['name']} 에러: {e}")

    # 💾 저장
    if new_data:
        new_data.sort(key=lambda x: x['발행일'], reverse=True)
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
            writer.writeheader()
            writer.writerows(new_data)
        print(f"\n🎉 드디어 성공! 총 {len(new_data)}건의 데이터를 확보했습니다.")
    else:
        print("\n💡 새로 업데이트된 리포트가 없습니다.")

if __name__ == "__main__":
    main()
