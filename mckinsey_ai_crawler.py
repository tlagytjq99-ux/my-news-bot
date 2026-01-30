import feedparser
import csv
import time
import base64
import re
from datetime import datetime
from googletrans import Translator

def get_original_url(google_url):
    """구글 뉴스 링크를 원래의 원본 URL로 변환"""
    try:
        if "articles/" in google_url:
            base64_url = google_url.split("articles/")[1].split("?")[0]
            base64_url += "=" * ((4 - len(base64_url) % 4) % 4)
            decoded_bytes = base64.urlsafe_b64decode(base64_url)
            decoded_str = decoded_bytes.decode('latin-1')
            if "http" in decoded_str:
                start_idx = decoded_str.find("http")
                clean_url = re.split(r'[^\w\d\.\/\:\%\?\&\=\-\+\_\~\#]', decoded_str[start_idx:])[0]
                return clean_url
    except: pass
    return google_url

def main():
    # 🎯 더 정교해진 쿼리 (AI/Tech 리포트에 집중)
    sources = [
        {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
        {"name": "MIT_Sloan", "url": "https://sloanreview.mit.edu/feed/"},
        {"name": "Deloitte", "url": "https://news.google.com/rss/search?q=site:deloitte.com/insights+AI+OR+Generative+OR+Technology&hl=en-US&gl=US&ceid=US:en"},
        {"name": "BCG", "url": "https://news.google.com/rss/search?q=site:bcg.com+AI+OR+Generative+OR+Tech+Insight&hl=en-US&gl=US&ceid=US:en"}
    ]
    
    file_name = 'ai_market_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    
    # 💡 긍정 키워드 (이 중 하나는 반드시 포함되어야 함)
    positive_kws = ['AI', 'GEN', 'DIGITAL', 'TECH', 'INTELLIGENCE', 'DATA', 'CLOUD', 'AUTOMATION', 'ALGORITHM', 'TRENDS', 'OUTLOOK']
    # 💡 부정 키워드 (이 중 하나라도 포함되면 탈락)
    negative_kws = ['JOB', 'CAREER', 'HIRE', 'RECRUIT', 'WORKSHOP', 'WELCOME', 'APPLY', 'GRADUATE', 'STUDENT', 'HOME', 'CONTACT']

    print(f"📡 [정밀 필터링 엔진] 수집 및 필터링 시작...")
    new_data = []

    for source in sources:
        print(f"🔍 {source['name']} 분석 중...")
        try:
            feed = feedparser.parse(source['url'])
            count = 0
            for entry in feed.entries:
                title_en = entry.title.split(' - ')[0]
                upper_title = title_en.upper()

                # 1단계: 부정 키워드 필터링 (채용/공고 등 제거)
                if any(nk in upper_title for nk in negative_kws):
                    continue
                
                # 2단계: 긍정 키워드 필수 포함 필터링 (AI/테크 관련성 보장)
                if not any(pk in upper_title for pk in positive_kws):
                    continue

                # 3단계: 날짜 유효성 검사 (너무 오래된 데이터 제외)
                raw_date = entry.get('published_parsed', None)
                if raw_date:
                    year = raw_date.tm_year
                    if year < 2024: continue # 2024년 이전 자료는 패스
                    published_date = time.strftime('%Y-%m-%d', raw_date)
                else:
                    published_date = collected_date

                # 링크 변환
                final_link = get_original_url(entry.link) if "google.com" in entry.link else entry.link

                try:
                    title_ko = translator.translate(title_en, dest='ko').text
                except:
                    title_ko = title_en

                new_data.append({
                    "기관": source['name'],
                    "발행일": published_date,
                    "제목": title_ko,
                    "원문": title_en,
                    "링크": final_link,
                    "수집일": collected_date
                })
                count += 1
                if count >= 10: break
            print(f"   ✅ {source['name']} 정예 리포트 {count}건 확보!")
        except Exception as e:
            print(f"   ❌ {source['name']} 에러: {e}")

    # 💾 저장
    if new_data:
        new_data.sort(key=lambda x: x['발행일'], reverse=True)
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
            writer.writeheader()
            writer.writerows(new_data)
        print(f"\n🎉 필터링 완료! {len(new_data)}건의 고퀄리티 데이터가 준비되었습니다.")

if __name__ == "__main__":
    main()
