import feedparser
import csv
import os
import time
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 기관별 RSS 주소
    sources = [
        {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
        {"name": "Gartner", "url": "https://www.gartner.com/en/newsroom/rss"}
    ]
    
    file_name = 'ai_market_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📡 [통합 엔진] 시장조사기관 수집 시작...")

    new_data = []
    # 💡 키워드 확장: 가트너 소식을 더 잘 잡기 위해 비즈니스/IT 키워드 추가
    ai_keywords = ['AI', 'TECH', 'DIGITAL', 'DATA', 'GEN', 'INTELLIGENCE', 'STRATEGY', 'IT', 'CYBER', 'SOFTWARE', 'CLOUD', 'BUSINESS']

    for source in sources:
        print(f"🔍 {source['name']} 분석 중...")
        try:
            feed = feedparser.parse(source['url'])
            
            # 피드 자체가 비어있는지 확인
            if not feed.entries:
                print(f"   ⚠️ {source['name']} 피드에 데이터가 아예 없습니다. (주소 확인 필요)")
                continue

            count = 0
            for entry in feed.entries:
                title_en = entry.title
                link = entry.link
                
                # 발행일 형식 변환
                raw_date = entry.get('published_parsed', None)
                published_date = time.strftime('%Y-%m-%d', raw_date) if raw_date else collected_date

                # 💡 키워드 매칭 (공백 포함 여부로 더 정교하게 체크)
                upper_title = title_en.upper()
                is_match = any(kw in upper_title for kw in ai_keywords)

                if is_match:
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
                    if count >= 15: break # 기관당 최대 15건
            
            print(f"   ✅ {source['name']}에서 {count}건 확보!")

        except Exception as e:
            print(f"   ❌ {source['name']} 수집 중 오류: {e}")

    # 💾 CSV 저장
    if new_data:
        # 최신순 정렬
        new_data.sort(key=lambda x: x['발행일'], reverse=True)
        
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ["기관", "발행일", "제목", "원문", "링크", "수집일"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(new_data)
        print(f"\n🎉 통합 수집 완료! 총 {len(new_data)}건 저장.")
    else:
        print("\n💡 키워드에 맞는 리포트가 하나도 없습니다.")

if __name__ == "__main__":
    main()
