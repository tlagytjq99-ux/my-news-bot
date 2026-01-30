import feedparser
import csv
import urllib.parse
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 검색어 설정 (site:oecd.org "Artificial Intelligence")
    query = 'site:oecd.org "Artificial Intelligence"'
    
    # 💡 [핵심 수정] URL에 포함될 수 없는 공백 등을 특수 코드로 변환 (URL Encoding)
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    file_name = 'oecd_ai_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"📡 구글 뉴스(OECD) 데이터 수집 시도 중... (URL: {rss_url})")
    new_data = []

    try:
        # RSS 피드 파싱
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            print("⚠️ 검색 결과가 없습니다. 검색어를 확인하세요.")
        else:
            print(f"🔍 {len(feed.entries)}건의 데이터를 발견했습니다.")

            for entry in feed.entries[:20]:
                title_en = entry.title.split(' - ')[0] # 매체명 제거
                link = entry.link
                
                # 날짜 처리 (항상 최신순으로 가져옴)
                pub_date = collected_date
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d')

                # 한국어 번역
                try:
                    title_ko = translator.translate(title_en, dest='ko').text
                except:
                    title_ko = title_en

                new_data.append({
                    "기관": "OECD",
                    "발행일": pub_date,
                    "제목": title_ko,
                    "원문": title_en,
                    "링크": link,
                    "수집일": collected_date
                })

    except Exception as e:
        print(f"❌ 예기치 못한 오류 발생: {e}")

    # 💾 결과 저장
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        if new_data:
            writer.writerows(new_data)
            print(f"✅ 성공! {len(new_data)}건의 보고서 리스트가 '{file_name}'에 저장되었습니다.")
        else:
            print("⚠️ 저장할 데이터가 없습니다.")

if __name__ == "__main__":
    main()
