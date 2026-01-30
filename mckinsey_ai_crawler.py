import feedparser
import csv
import os
import time
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 타겟: 맥킨지(컨설팅 정수) + MIT Sloan(테크 경영의 정수)
    sources = [
        {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
        {"name": "MIT_Sloan", "url": "https://sloanreview.mit.edu/feed/"}
    ]
    
    file_name = 'ai_market_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📡 [글로벌 인사이트 엔진] 수집 시작 (McKinsey + MIT Sloan)...")

    new_data = []
    # AI 및 미래 기술 관련 핵심 키워드
    ai_keywords = ['AI', 'GEN', 'DIGITAL', 'TECH', 'INTELLIGENCE', 'DATA', 'ALGORITHM', 'FUTURE', 'AUTOMATION']

    for source in sources:
        print(f"🔍 {source['name']} 분석 중...")
        try:
            # MIT Sloan은 표준 RSS 형식을 아주 잘 지킵니다.
            feed = feedparser.parse(source['url'])
            
            if not feed.entries:
                print(f"   ⚠️ {source['name']} 피드가 현재 응답하지 않습니다.")
                continue

            count = 0
            for entry in feed.entries:
                title_en = entry.title
                link = entry.link
                
                # 날짜 처리 (발행일 추출)
                raw_date = entry.get('published_parsed', None)
                published_date = time.strftime('%Y-%m-%d', raw_date) if raw_date else collected_date

                # 제목 키워드 필터링 (불필요한 기사 제외)
                upper_title = title_en.upper()
                if any(kw in upper_title for kw in ai_keywords):
                    try:
                        # 한국어로 매끄럽게 번역
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
                    # 기관당 최대 15건 수집
                    if count >= 15: break
            
            print(f"   ✅ {source['name']}에서 {count}건 확보 성공!")

        except Exception as e:
            print(f"   ❌ {source['name']} 에러 발생: {e}")

    # 💾 결과 저장 (최신 발행일 순으로 정렬)
    if new_data:
        new_data.sort(key=lambda x: x['발행일'], reverse=True)
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ["기관", "발행일", "제목", "원문", "링크", "수집일"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(new_data)
        print(f"\n🎉 작업 완료! 총 {len(new_data)}건의 전략 리포트를 확보했습니다.")
    else:
        print("\n💡 새로 업데이트된 조건에 맞는 리포트가 없습니다.")

if __name__ == "__main__":
    main()
