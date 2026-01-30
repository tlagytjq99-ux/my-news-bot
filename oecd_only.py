import feedparser
import csv
import urllib.parse
from datetime import datetime
from googletrans import Translator
# 💡 좀 더 안정적인 gnewsdecoder 사용
from googlenewsdecoder import gnewsdecoder

def main():
    # 🎯 검색 필터: OECD 사이트 내 AI 관련 핵심 문서
    query = 'site:oecd.org (intitle:"Artificial Intelligence" OR intitle:AI) -intitle:PISA'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    file_name = 'oecd_ai_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"📡 수집 시작 (URL: {rss_url})")
    raw_data = []

    try:
        feed = feedparser.parse(rss_url)
        print(f"🔍 총 {len(feed.entries)}건 발견. 필터링 시작...")
        
        for entry in feed.entries:
            title_en = entry.title.split(' - ')[0]
            google_link = entry.link
            
            # 💡 [핵심] 원본 링크 변환 시도 (실패해도 멈추지 않음)
            actual_link = google_link
            try:
                decoded = gnewsdecoder(google_link, interval=1)
                if decoded.get('status'):
                    actual_link = decoded.get('decoded_url')
            except Exception as e:
                print(f"🔗 링크 변환 건너뜀: {e}")

            # AI 키워드 검사
            keywords = ['AI', 'ARTIFICIAL', 'INTELLIGENCE', 'ALGORITHMS', 'GENERATIVE']
            if not any(kw in title_en.upper() for kw in keywords):
                continue

            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_dt = datetime(*entry.published_parsed[:6])
                raw_data.append({
                    "기관": "OECD",
                    "발행일": pub_dt.strftime('%Y-%m-%d'),
                    "dt_obj": pub_dt,
                    "제목_en": title_en,
                    "링크": actual_link
                })

        # 최신순 정렬 후 5개만
        raw_data.sort(key=lambda x: x['dt_obj'], reverse=True)
        final_5 = raw_data[:5]

        final_data = []
        for item in final_5:
            try:
                title_ko = translator.translate(item['제목_en'].strip(), dest='ko').text
            except:
                title_ko = item['제목_en']
            
            final_data.append({
                "기관": "OECD", "발행일": item['발행일'], "제목": title_ko,
                "원문": item['제목_en'], "링크": item['링크'], "수집일": collected_date
            })

    except Exception as e:
        print(f"❌ 전체 프로세스 오류: {e}")

    # 💾 파일 저장 (빈 파일 방지용 헤더 기록)
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        if final_data:
            writer.writerows(final_data)
            print(f"✅ 완료! {len(final_data)}건의 데이터를 파일에 썼습니다.")
        else:
            print("⚠️ 수집된 데이터가 없습니다. 검색 조건을 확인하세요.")

if __name__ == "__main__":
    main()
