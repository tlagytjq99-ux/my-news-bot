import feedparser
import csv
import urllib.parse
import requests
from datetime import datetime
from googletrans import Translator

def get_real_url(google_url):
    """구글 뉴스 리다이렉트 링크를 원본 URL로 변환"""
    try:
        # 💡 원본 링크로 연결되는지 확인 (최대 5초 대기)
        response = requests.get(google_url, timeout=5)
        # 💡 최종 도착지(원본 주소) 반환
        return response.url
    except:
        # 실패 시 구글 링크라도 유지
        return google_url

def main():
    query = 'site:oecd.org (intitle:"Artificial Intelligence" OR intitle:AI) -intitle:PISA'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    file_name = 'oecd_ai_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"📡 OECD 최신 AI 리포트 수집 및 원본 링크 변환 시작...")
    raw_data = []

    try:
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries:
            title_en = entry.title.split(' - ')[0]
            
            # 💡 [필터링] AI 관련 핵심 키워드 검사
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
                    "google_link": entry.link # 임시 저장
                })

        # 1️⃣ 최신순 정렬
        raw_data.sort(key=lambda x: x['dt_obj'], reverse=True)

        # 2️⃣ 최상위 5개만 선택 및 원본 링크 변환
        final_data = []
        for item in raw_data[:5]:
            print(f"🔗 원본 링크 추출 중: {item['제목_en'][:30]}...")
            
            # 💡 구글 링크를 원본 링크로 변환
            actual_link = get_real_url(item['google_link'])
            
            try:
                title_ko = translator.translate(item['제목_en'].strip(), dest='ko').text
            except:
                title_ko = item['제목_en']
            
            final_data.append({
                "기관": "OECD",
                "발행일": item['발행일'],
                "제목": title_ko,
                "원문": item['제목_en'],
                "링크": actual_link,
                "수집일": collected_date
            })

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    # 💾 결과 저장
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        if final_data:
            writer.writerows(final_data)
            print(f"✅ 성공! 원본 링크가 포함된 {len(final_data)}건 저장 완료.")
        else:
            print("⚠️ 조건에 맞는 최신 AI 리포트가 발견되지 않았습니다.")

if __name__ == "__main__":
    main()
