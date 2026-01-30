import feedparser
import csv
import time
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 글로벌 정책 및 의제 설정 기구 타겟
    # OECD는 대표님이 주신 'AI 정책(pi20)' 테마의 최신 데이터를 가져오는 주소를 사용합니다.
    sources = [
        {
            "name": "OECD", 
            "url": "https://www.oecd.org/en/topics/subtopics/artificial-intelligence/jcr:content/feed"
        },
        {
            "name": "WEF", 
            "url": "https://www.weforum.org/agenda/feed"
        }
    ]
    
    file_name = 'oecd_wef_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    
    # 💡 정책 및 글로벌 경제 관련 핵심 키워드
    policy_keywords = ['AI', 'DIGITAL', 'ECONOMY', 'POLICY', 'GOVERNANCE', 'FRAMEWORK', 'OUTLOOK', 'REPORT', 'STRATEGY']

    print(f"📡 [OECD & WEF 정책 엔진] 수집 시작...")
    new_data = []

    for source in sources:
        print(f"🔍 {source['name']} 정책 리포트 분석 중...")
        try:
            feed = feedparser.parse(source['url'])
            if not feed.entries:
                print(f"   ⚠️ {source['name']} 피드에서 데이터를 찾을 수 없습니다.")
                continue

            count = 0
            for entry in feed.entries:
                title_en = entry.title
                
                # 제목에 핵심 키워드가 포함된 경우만 수집 (순도 유지)
                if any(kw in title_en.upper() for kw in policy_keywords):
                    
                    # 발행일 처리
                    raw_date = entry.get('published_parsed', None)
                    published_date = time.strftime('%Y-%m-%d', raw_date) if raw_date else collected_date

                    # 한국어 번역
                    try:
                        # OECD/WEF는 문장이 길어 번역 엔진 호출 시 예외 처리가 중요합니다.
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
                    if count >= 20: break # 기관당 최신 20건 수집
            
            print(f"   ✅ {source['name']}에서 {count}건의 핵심 의제 확보!")

        except Exception as e:
            print(f"   ❌ {source['name']} 수집 중 에러 발생: {e}")

    # 💾 결과 저장 (발행일 기준 내림차순 정렬)
    if new_data:
        new_data.sort(key=lambda x: x['발행일'], reverse=True)
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
            writer.writeheader()
            writer.writerows(new_data)
        print(f"\n🎉 작업 완료! '{file_name}'에 글로벌 정책 인사이트가 저장되었습니다.")
    else:
        print("\n💡 새로 업데이트된 정책 리포트가 없습니다.")

if __name__ == "__main__":
    main()
