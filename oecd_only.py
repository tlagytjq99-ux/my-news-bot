import feedparser
import csv
import urllib.parse
import requests
from datetime import datetime
from googletrans import Translator

def resolve_google_url(google_url):
    """구글의 리다이렉트 벽을 뚫고 실제 원본 URL을 찾아내는 함수"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        # 💡 핵심: 세션을 사용하고 allow_redirects=True로 끝까지 추적합니다.
        session = requests.Session()
        response = session.get(google_url, headers=headers, timeout=10, allow_redirects=True)
        
        # 마지막으로 도착한 URL이 원본 주소입니다.
        final_url = response.url
        
        # 만약 여전히 google.com이 포함되어 있다면 리다이렉트 체인을 다시 확인
        if "google.com" in final_url and response.history:
            final_url = response.history[-1].headers.get('Location', final_url)
            
        return final_url
    except Exception as e:
        print(f"🔗 링크 변환 중 오류(건너뜀): {e}")
        return google_url

def main():
    query = 'site:oecd.org (intitle:"Artificial Intelligence" OR intitle:AI) -intitle:PISA'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    file_name = 'oecd_ai_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"📡 OECD 최신 데이터 수집 및 원본 링크 강제 추출 시작...")
    raw_data = []

    try:
        feed = feedparser.parse(rss_url)
        # 최신 발행 순 정렬
        entries = sorted(feed.entries, key=lambda x: x.get('published_parsed'), reverse=True)
        
        count = 0
        for entry in entries:
            if count >= 5: break
            
            title_en = entry.title.split(' - ')[0]
            
            # AI 관련 키워드 재검증
            keywords = ['AI', 'ARTIFICIAL', 'INTELLIGENCE', 'ALGORITHMS', 'GENERATIVE']
            if not any(kw in title_en.upper() for kw in keywords):
                continue

            print(f"🔄 {count+1}번째 링크 분석 중: {title_en[:30]}...")
            
            # 💡 [핵심] 리다이렉트 추적 실행
            actual_link = resolve_google_url(entry.link)
            
            pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d') if hasattr(entry, 'published_parsed') else collected_date

            try:
                title_ko = translator.translate(title_en.strip(), dest='ko').text
            except:
                title_ko = title_en

            raw_data.append({
                "기관": "OECD", "발행일": pub_date, "제목": title_ko,
                "원문": title_en, "링크": actual_link, "수집일": collected_date
            })
            count += 1

    except Exception as e:
        print(f"❌ 오류: {e}")

    # 💾 결과 저장
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        if raw_data:
            writer.writerows(raw_data)
            print(f"✅ 성공! 원본 링크를 포함한 {len(raw_data)}건의 보고서를 확보했습니다.")
        else:
            print("⚠️ 조건에 맞는 리포트가 없습니다.")

if __name__ == "__main__":
    main()
