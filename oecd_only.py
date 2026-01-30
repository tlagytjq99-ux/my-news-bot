import feedparser
import csv
import urllib.parse
from datetime import datetime
from googletrans import Translator
from googlenewsdecoder import decoderv2  # 💡 최신 디코딩 라이브러리

def main():
    query = 'site:oecd.org (intitle:"Artificial Intelligence" OR intitle:AI) -intitle:PISA'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    file_name = 'oecd_ai_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"📡 OECD 최신 데이터 수집 및 원본 링크 강제 해독 시작...")
    final_data = []

    try:
        feed = feedparser.parse(rss_url)
        # 최신순 정렬
        entries = sorted(feed.entries, key=lambda x: x.get('published_parsed'), reverse=True)
        
        count = 0
        for entry in entries:
            if count >= 5: break
            
            title_en = entry.title.split(' - ')[0]
            
            # AI 키워드 검증
            keywords = ['AI', 'ARTIFICIAL', 'INTELLIGENCE', 'ALGORITHMS', 'GENERATIVE']
            if not any(kw in title_en.upper() for kw in keywords):
                continue

            print(f"🔑 {count+1}번째 암호 해독 중...")
            
            # 💡 [핵심] 전용 디코더를 사용하여 원본 URL 추출
            try:
                decoded = decoderv2(entry.link, interval=1)
                actual_link = decoded.get('decoded_url', entry.link)
            except:
                actual_link = entry.link # 실패 시 구글 링크 유지

            pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d') if hasattr(entry, 'published_parsed') else collected_date

            try:
                title_ko = translator.translate(title_en.strip(), dest='ko').text
            except:
                title_ko = title_en

            final_data.append({
                "기관": "OECD", "발행일": pub_date, "제목": title_ko,
                "원문": title_en, "링크": actual_link, "수집일": collected_date
            })
            count += 1

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    # 💾 결과 저장
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        if final_data:
            writer.writerows(final_data)
            print(f"✅ 완료! 원본 링크가 포함된 {len(final_data)}건의 데이터를 파일에 썼습니다.")
        else:
            print("⚠️ 조건에 맞는 데이터가 발견되지 않았습니다.")

if __name__ == "__main__":
    main()
