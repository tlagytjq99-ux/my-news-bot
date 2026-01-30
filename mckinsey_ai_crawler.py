import feedparser
import csv
import time
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 가장 신뢰도 높은 2대 지식 창고만 타겟팅
    sources = [
        {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
        {"name": "MIT_Sloan", "url": "https://sloanreview.mit.edu/feed/"}
    ]
    
    file_name = 'ai_market_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    
    # 💡 AI 및 경영 혁신 관련 핵심 키워드
    ai_keywords = ['AI', 'GEN', 'DIGITAL', 'TECH', 'INTELLIGENCE', 'DATA', 'FUTURE', 'AUTOMATION']

    print(f"📡 [정예 엔진] McKinsey & MIT Sloan 수집 시작...")
    new_data = []

    for source in sources:
        print(f"🔍 {source['name']} 분석 중...")
        try:
            feed = feedparser.parse(source['url'])
            if not feed.entries:
                print(f"   ⚠️ {source['name']} 피드 응답 없음")
                continue

            count = 0
            for entry in feed.entries:
                title_en = entry.title
                # AI 관련 기사인지 제목에서 1차 검축
                if any(kw in title_en.upper() for kw in ai_keywords):
                    
                    # 날짜 처리
                    raw_date = entry.get('published_parsed', None)
                    published_date = time.strftime('%Y-%m-%d', raw_date) if raw_date else collected_date

                    # 한국어 번역
                    try:
                        title_ko = translator.translate(title_en, dest='ko').text
                    except:
                        title_ko = title_en

                    new_data.append({
                        "기관": source['name'],
                        "발행일": published_date,
                        "제목": title_ko,
                        "원문": title_en,
                        "링크": entry.link,
                        "수집일": collected_date
                    })
                    count += 1
                    if count >= 15: break # 기관당 최대 15건
            
            print(f"   ✅ {source['name']}에서 {count}건 확보 성공!")

        except Exception as e:
            print(f"   ❌ {source['name']} 에러 발생: {e}")

    # 💾 결과 저장 (최신순 정렬)
    if new_data:
        new_data.sort(key=lambda x: x['발행일'], reverse=True)
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
            writer.writeheader()
            writer.writerows(new_data)
        print(f"\n🎉 작업 완료! 엑셀 파일이 업데이트되었습니다.")
    else:
        print("\n💡 수집된 새로운 데이터가 없습니다.")

if __name__ == "__main__":
    main()
