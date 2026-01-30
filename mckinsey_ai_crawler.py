import feedparser
import csv
import os
import time
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 타겟 기관: McKinsey + IDC (IT 시장 분석 최강자)
    sources = [
        {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
        {"name": "IDC", "url": "https://www.idc.com/rss/pr"}
    ]
    
    file_name = 'ai_market_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📡 [IDC 통합 엔진] 수집 시작...")

    new_data = []
    # IDC는 하드웨어, 소프트웨어, AI 소식이 많으므로 키워드를 정교화합니다.
    ai_keywords = ['AI', 'TECH', 'DIGITAL', 'INTELLIGENCE', 'DATA', 'SMARTPHONE', 'CLOUD', 'SPENDING', 'MARKET']

    for source in sources:
        print(f"🔍 {source['name']} 분석 중...")
        try:
            # IDC와 맥킨지 모두 RSS 표준을 잘 따릅니다.
            feed = feedparser.parse(source['url'])
            
            if not feed.entries:
                print(f"   ⚠️ {source['name']} 피드 응답이 없습니다.")
                continue

            count = 0
            for entry in feed.entries:
                title_en = entry.title
                link = entry.link
                
                # 날짜 처리
                raw_date = entry.get('published_parsed', None)
                published_date = time.strftime('%Y-%m-%d', raw_date) if raw_date else collected_date

                # AI/Tech 관련 키워드 필터링
                upper_title = title_en.upper()
                if any(kw in upper_title for kw in ai_keywords):
                    try:
                        # 한국어 번역
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
            print(f"   ❌ {source['name']} 에러: {e}")

    # 💾 결과 저장 (최신순 정렬)
    if new_data:
        new_data.sort(key=lambda x: x['발행일'], reverse=True)
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ["기관", "발행일", "제목", "원문", "링크", "수집일"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(new_data)
        print(f"\n🎉 성공! 총 {len(new_data)}건의 최신 IT 리포트를 저장했습니다.")
    else:
        print("\n💡 수집된 새로운 데이터가 없습니다.")

if __name__ == "__main__":
    main()
