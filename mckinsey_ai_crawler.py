import feedparser
import csv
import os
import time
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 맥킨지 + PwC 공식 보도자료 채널 (PR Newswire)
    sources = [
        {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
        # 💡 PwC가 공식 보도자료를 뿌리는 글로벌 뉴스 피드입니다. (차단 불가)
        {"name": "PwC_Official", "url": "https://www.prnewswire.com/rss/news-releases-list.rss?search=PwC"}
    ]
    
    file_name = 'ai_market_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📡 [최후의 수단] PwC 뉴스 피드 수집 시작...")

    new_data = []
    ai_keywords = ['AI', 'TECH', 'DIGITAL', 'INTELLIGENCE', 'DATA', 'GEN', 'CLOUD', 'ESG']

    for source in sources:
        print(f"🔍 {source['name']} 분석 중...")
        try:
            # PR Newswire는 봇 차단이 거의 없어 잘 뚫립니다.
            feed = feedparser.parse(source['url'])
            
            if not feed.entries:
                print(f"   ⚠️ {source['name']} 응답 없음. (주소를 점검 중...)")
                continue

            count = 0
            for entry in feed.entries:
                title_en = entry.title
                link = entry.link
                
                raw_date = entry.get('published_parsed', None)
                published_date = time.strftime('%Y-%m-%d', raw_date) if raw_date else collected_date

                # 제목에 키워드 확인 (PwC는 AI뿐만 아니라 디지털 전환 전체를 봅니다)
                upper_title = title_en.upper()
                if any(kw in upper_title for kw in ai_keywords):
                    try:
                        res = translator.translate(title_en, src='en', dest='ko')
                        title_ko = res.text
                    except:
                        title_ko = title_en

                    print(f"   ✅ [성공] {source['name']}: {title_ko[:25]}...")

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
            
            print(f"   ✅ {source['name']}에서 {count}건 확보!")

        except Exception as e:
            print(f"   ❌ {source['name']} 에러: {e}")

    # 💾 저장 로직
    if new_data:
        new_data.sort(key=lambda x: x['발행일'], reverse=True)
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ["기관", "발행일", "제목", "원문", "링크", "수집일"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(new_data)
        print(f"\n🎉 드디어 마침표! 총 {len(new_data)}건의 데이터를 확보했습니다.")
    else:
        print("\n💡 새로 발견된 전략 리포트가 없습니다.")

if __name__ == "__main__":
    main()
