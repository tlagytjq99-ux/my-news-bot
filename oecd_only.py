import feedparser
import csv
import urllib.parse
import requests
import base64
import re
from datetime import datetime
from googletrans import Translator

def get_original_url(google_url):
    """구글 뉴스의 암호화된 URL을 분석하여 원본 URL을 강제로 추출"""
    try:
        # 1. 구글 뉴스 링크에서 암호화된 데이터 부분 추출
        # https://news.google.com/rss/articles/CBMi... 형태에서 CBMi... 부분
        path = google_url.split('/')[-1].split('?')[0]
        
        # 2. Base64 디코딩 시도 (구글이 사용하는 방식)
        # 패딩 문제 해결을 위해 '===' 추가
        decoded_bytes = base64.urlsafe_b64decode(path + '===')
        decoded_str = decoded_bytes.decode('latin-1')
        
        # 3. 디코딩된 문자열에서 URL 패턴(http...)을 정규식으로 찾아냄
        urls = re.findall(r'https?://[^\x00-\x1f\x7f-\xff]+', decoded_str)
        
        if urls:
            # 발견된 URL 중 가장 긴 것이 대개 원본 주소입니다.
            actual_url = max(urls, key=len)
            # 불필요한 노이즈 제거
            actual_url = actual_url.split('?')[0].split('\x01')[0].split('\x03')[0]
            return actual_url
            
        # 4. 위 방식 실패 시, 실제 접속 후 경로 추적 (Fallback)
        res = requests.get(google_url, timeout=5, allow_redirects=True)
        return res.url
    except:
        return google_url

def main():
    query = 'site:oecd.org (intitle:"Artificial Intelligence" OR intitle:AI) -intitle:PISA'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    file_name = 'oecd_ai_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"📡 OECD 데이터 수집 및 링크 해독 시작...")
    raw_data = []

    try:
        feed = feedparser.parse(rss_url)
        entries = sorted(feed.entries, key=lambda x: x.get('published_parsed'), reverse=True)
        
        count = 0
        for entry in entries:
            if count >= 5: break
            
            title_en = entry.title.split(' - ')[0]
            
            # 키워드 필터링
            keywords = ['AI', 'ARTIFICIAL', 'INTELLIGENCE', 'ALGORITHMS', 'GENERATIVE']
            if not any(kw in title_en.upper() for kw in keywords):
                continue

            print(f"🔗 {count+1}번째 원본 링크 해독 중...")
            # 💡 [핵심] 암호 해독 및 리다이렉트 추적
            actual_link = get_original_url(entry.link)
            
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

    # 💾 저장
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        if raw_data:
            writer.writerows(raw_data)
            print(f"✅ 완료! {len(raw_data)}건의 원본 링크를 확보했습니다.")

if __name__ == "__main__":
    main()
