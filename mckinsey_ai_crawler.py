import feedparser
import csv
import os
import time
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 타겟 기관 교체: 가트너 -> 딜로이트 (AI 리포트 풍부)
    sources = [
        {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
        {"name": "Deloitte", "url": "https://www2.deloitte.com/us/en/pages/about-deloitte/articles/rss-feed.rss"}
    ]
    
    file_name = 'ai_market_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📡 [통합 엔진] 시장조사기관 수집 시작 (McKinsey + Deloitte)...")

    new_data = []
    ai_keywords = ['AI', 'TECH', 'DIGITAL', 'DATA', 'GEN', 'INTELLIGENCE', 'STRATEGY', 'CLOUD', 'FUTURE']

    for source in sources:
        print(f"🔍 {source['name']} 분석 중...")
        try:
            feed = feedparser.parse(source['url'])
            
            if not feed.entries:
                print(f"   ⚠️ {source['name']} 피드가 비어있습니다.")
                continue

            count = 0
            for entry in feed.entries:
                title_en = entry.title
                link = entry.link
                
                # 날짜 처리
                raw_date = entry.get('published_parsed', None)
                published_date = time.strftime('%Y-%m-%d', raw_date) if raw_date else collected_date

                # AI 관련 키워드 필터링
                upper_title = title_en.upper()
                if any(kw in upper_title for kw in ai_keywords):
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
                    if count >= 15: break
            
            print(f"   ✅ {source['name']}에서 {count}건 확보 완료!")

        except Exception as e:
            print(f"   ❌ {source['name']} 수집 중 에러: {e}")

    # 💾 결과 저장
    if new_data:
        new_data.sort(key=lambda x: x['발행일'], reverse=True)
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ["기관", "발행일", "제목", "원문", "링크", "수집일"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(new_data)
        print(f"\n🎉 통합 수집 완료! 총 {len(new_data)}건의 인사이트를 담았습니다.")
    else:
        print("\n💡 새로 올라온 AI 리포트가 없습니다.")

if __name__ == "__main__":
    main()
