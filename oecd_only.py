import feedparser
import csv
import urllib.parse
from datetime import datetime
from googletrans import Translator
# 💡 원본 링크 추출을 위한 새로운 도구
from googlenewsdecoder import decoderv2

def main():
    query = 'site:oecd.org (intitle:"Artificial Intelligence" OR intitle:AI) -intitle:PISA'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    file_name = 'oecd_ai_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"📡 OECD 최신 리포트 수집 및 원본 링크 변환 시작...")
    raw_data = []

    try:
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries:
            title_en = entry.title.split(' - ')[0]
            google_link = entry.link
            
            # 💡 [핵심] 구글 리다이렉트 링크를 원본 링크로 변환
            try:
                decoded = decoderv2(google_link)
                actual_link = decoded.get('decoded_url', google_link)
            except:
                actual_link = google_link # 변환 실패 시 구글 링크 유지

            # 키워드 필터링
            keywords = ['AI', 'ARTIFICIAL INTELLIGENCE', 'ALGORITHMS', 'GENERATIVE']
            if not any(kw in title_en.upper() for kw in keywords):
                continue

            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_dt = datetime(*entry.published_parsed[:6])
                pub_date_str = pub_dt.strftime('%Y-%m-%d')
                raw_data.append({
                    "기관": "OECD",
                    "발행일": pub_date_str,
                    "dt_obj": pub_dt,
                    "제목_en": title_en,
                    "링크": actual_link
                })

        # 최신순 정렬 후 상위 5개 선택
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

    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        if final_data:
            writer.writerows(final_data)
            print(f"✅ 성공! 원본 링크로 변환된 최신 리포트 {len(final_data)}건 저장.")
