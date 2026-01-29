import feedparser
import csv
import os
from datetime import datetime
# 번역 라이브러리 추가
from googletrans import Translator

def main():
    rss_url = "https://www.cao.go.jp/houdou/houdou.rdf"
    file_name = 'japan_ai_report.csv'
    translator = Translator()
    
    print(f"📡 [일본 내각부] 데이터 수집 및 한국어 번역 시작...")

    try:
        feed = feedparser.parse(rss_url)
        new_data = []
        
        # 💡 테스트를 위해 중복 체크를 잠시 끄거나 파일을 새로 만듭니다.
        # 기존 데이터를 무시하고 새로 다 긁어보겠습니다.

        count = 0
        for entry in feed.entries:
            if count >= 10: break # 최신 10개만 수집
            
            original_title = entry.title
            link = entry.link
            
            # 💡 [핵심] 일본어 제목 -> 한국어로 번역
            try:
                translated = translator.translate(original_title, src='ja', dest='ko')
                title_ko = translated.text
            except:
                title_ko = original_title # 번역 실패 시 원문 유지

            print(f"   📝 번역완료: {title_ko[:40]}...")

            new_data.append({
                "기관": "일본 내각부(CAO)",
                "발행일": entry.get('published', datetime.now().strftime("%Y-%m-%d")),
                "제목": title_ko, # 한국어 제목 저장
                "원문제목": original_title,
                "링크": link,
                "수집일": datetime.now().strftime("%Y-%m-%d")
            })
            count += 1

        # 💾 결과 저장 (완전히 새로 쓰기 모드 'w'로 테스트)
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문제목", "링크", "수집일"])
            writer.writeheader()
            writer.writerows(new_data)
            
        print(f"✅ 성공! {len(new_data)}건의 뉴스를 한국어로 번역하여 저장했습니다.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    main()
