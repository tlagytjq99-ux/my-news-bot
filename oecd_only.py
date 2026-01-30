import feedparser
import csv
import urllib.parse
from datetime import datetime
from googletrans import Translator
from googlenewsdecoder import gnewsdecoder # 💡 암호 해독 전문 도구

def main():
    # 🎯 검색어: OECD 사이트 내의 AI 관련 문서
    query = 'site:oecd.org (intitle:"Artificial Intelligence" OR intitle:AI) -intitle:PISA'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    file_name = 'oecd_ai_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"📡 OECD 데이터 수집 및 링크 암호 해독 시작...")
    raw_data = []

    try:
        feed = feedparser.parse(rss_url)
        print(f"🔍 {len(feed.entries)}개의 뉴스 발견. 원본 링크 추출 중...")

        for entry in feed.entries:
            title_en = entry.title.split(' - ')[0]
            
            # AI 키워드 필터링
            keywords = ['AI', 'ARTIFICIAL', 'INTELLIGENCE', 'ALGORITHMS', 'GENERATIVE']
            if not any(kw in title_en.upper() for kw in keywords):
                continue

            # 💡 [핵심] 구글 뉴스 암호 해독 (서버 응답 대기 없음)
            try:
                decoded = gnewsdecoder(entry.link)
                actual_link = decoded.get('decoded_url', entry.link)
            except:
                actual_link = entry.link

            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_dt = datetime(*entry.published_parsed[:6])
                raw_data.append({
                    "기관": "OECD",
                    "발행일": pub_dt.strftime('%Y-%m-%d'),
                    "dt_obj": pub_dt,
                    "제목_en": title_en,
                    "링크": actual_link
                })

        # 최신순 정렬 후 5개 선택
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
        print(f"❌ 오류 발생: {e}")

    # 💾 결과 저장
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        if final_data:
            writer.writerows(final_data)
            print(f"✅ 성공! 원본 링크로 변환된 {len(final_data)}건 저장 완료.")
        else:
            print("⚠️ 조건에 맞는 데이터가 없습니다.")

if __name__ == "__main__":
    main()
