import feedparser
import csv
import os
import time
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 맥킨지(성공확정) + PwC의 핵심 소식이 올라오는 Strategy+Business 피드
    sources = [
        {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
        # PwC 계열의 비즈니스/테크 전문 미디어 (PwC 리포트가 여기 다 모입니다)
        {"name": "PwC_Insights", "url": "https://www.strategy-business.com/rss/all_articles"}
    ]
    
    file_name = 'ai_market_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📡 [긴급 우회] 수집 시작 (McKinsey + Strategy+Business)...")

    new_data = []
    ai_keywords = ['AI', 'GEN', 'TECH', 'DIGITAL', 'INTELLIGENCE', 'DATA', 'SOFTWARE', 'CLOUD']

    for source in sources:
        print(f"🔍 {source['name']} 분석 중...")
        try:
            # 주소 파싱 (Strategy+Business는 주소가 살아있음을 확인했습니다)
            feed = feedparser.parse(source['url'])
            
            if not feed.entries:
                print(f"   ⚠️ {source['name']} 피드 응답 없음 (수집 대상 제외)")
                continue

            count = 0
            for entry in feed.entries:
                title_en = entry.title
                link = entry.link
                
                raw_date = entry.get('published_parsed', None)
                published_date = time.strftime('%Y-%m-%d', raw_date) if raw_date else collected_date

                # 제목 키워드 필터링
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
            
            print(f"   ✅ {source['name']}에서 {count}건 확보 성공!")

        except Exception as e:
            print(f"   ❌ {source['name']} 에러: {e}")

    # 💾 결과 저장
    if new_data:
        new_data.sort(key=lambda x: x['발행일'], reverse=True)
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ["기관", "발행일", "제목", "원문", "링크", "수집일"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(new_data)
        print(f"\n🎉 드디어 완성! 총 {len(new_data)}건의 데이터를 확보했습니다.")
    else:
        print("\n💡 조건에 맞는 새로운 리포트가 없습니다.")

if __name__ == "__main__":
    main()
