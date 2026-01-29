import feedparser
import csv
import os
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 맥킨지 인사이트 RSS (웹사이트보다 훨씬 접근이 쉬움)
    rss_url = "https://www.mckinsey.com/insights/rss"
    file_name = 'mckinsey_ai_report.csv'
    translator = Translator()
    
    print(f"📡 [McKinsey] RSS 피드 우회 수집 시작...")

    try:
        # RSS 데이터 파싱
        feed = feedparser.parse(rss_url)
        new_data = []
        
        # 'AI', 'Artificial Intelligence', 'Gen AI' 등의 키워드가 포함된 기사만 필터링
        ai_keywords = ['AI', 'TECH', 'DIGITAL', 'DATA', 'GEN']

        for entry in feed.entries:
            title_en = entry.title
            link = entry.link
            
            # 제목에 AI 관련 단어가 있는지 확인
            if any(kw in title_en.upper() for kw in ai_keywords):
                try:
                    # 번역 시도
                    res = translator.translate(title_en, src='en', dest='ko')
                    title_ko = res.text
                except:
                    title_ko = title_en

                print(f"   ✅ 발견 & 번역: {title_ko[:30]}...")
                
                new_data.append({
                    "기관": "McKinsey",
                    "발행일": entry.get('published', datetime.now().strftime("%Y-%m-%d")),
                    "제목": title_ko,
                    "원문": title_en,
                    "링크": link
                })
                if len(new_data) >= 10: break

        if new_data:
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크"])
                writer.writeheader()
                writer.writerows(new_data)
            print(f"🎉 성공! {len(new_data)}건의 리포트를 RSS로 수집했습니다.")
        else:
            print("💡 최신 AI 관련 리포트가 피드에 없습니다.")

    except Exception as e:
        print(f"❌ RSS 수집 실패: {e}")

if __name__ == "__main__":
    main()
