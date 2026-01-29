import feedparser
import csv
import os
import time
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 수집 대상 기관 리스트 (확장이 가능하도록 설계)
    sources = [
        {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
        {"name": "Gartner", "url": "https://www.gartner.com/en/newsroom/rss"}
    ]
    
    file_name = 'ai_market_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📡 [통합 엔진] 시장조사기관 수집 시작 (McKinsey + Gartner)...")

    new_data = []
    ai_keywords = ['AI', 'TECH', 'DIGITAL', 'DATA', 'GEN', 'INTELLIGENCE', 'STRATEGY', 'IT', 'CYBER']

    for source in sources:
        print(f"🔍 {source['name']} 분석 중...")
        try:
            feed = feedparser.parse(source['url'])
            count = 0

            for entry in feed.entries:
                title_en = entry.title
                link = entry.link
                
                # 발행일 형식 변환 (yyyy-mm-dd)
                raw_date = entry.get('published_parsed', None)
                published_date = time.strftime('%Y-%m-%d', raw_date) if raw_date else collected_date

                # 제목에 키워드가 포함된 경우만 수집
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
                    if count >= 10: break # 기관당 최대 10건
            
            print(f"   ✅ {source['name']}에서 {count}건 확보!")

        except Exception as e:
            print(f"   ❌ {source['name']} 수집 중 오류: {e}")

    # 💾 CSV 저장
    if new_data:
        # 발행일 기준으로 내림차순 정렬 (최신순)
        new_data.sort(key=lambda x: x['발행일'], reverse=True)
        
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ["기관", "발행일", "제목", "원문", "링크", "수집일"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(new_data)
        print(f"\n🎉 통합 수집 완료! 총 {len(new_data)}건의 리포트가 저장되었습니다.")
    else:
        print("\n💡 수집된 새로운 데이터가 없습니다.")

if __name__ == "__main__":
    main()
