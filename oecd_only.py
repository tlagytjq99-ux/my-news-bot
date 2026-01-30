import feedparser
import csv
import urllib.parse
import base64
import re
from datetime import datetime
from googletrans import Translator

def decode_google_news_url(url):
    """구글 뉴스 주소의 암호화된 부분을 해독하여 원본 URL 추출"""
    try:
        # 1. URL에서 암호화된 핵심 문자열만 추출
        base64_str = url.split("articles/")[1].split("?")[0]
        
        # 2. Base64 디코딩 (패딩 보정 작업 포함)
        padding = len(base64_str) % 4
        if padding != 0:
            base64_str += "=" * (4 - padding)
        
        decoded_bytes = base64.urlsafe_b64decode(base64_str)
        # 다양한 인코딩 대응
        decoded_text = decoded_bytes.decode('latin-1', errors='ignore')
        
        # 3. 디코딩된 텍스트 안에서 http로 시작하는 문자열을 정규식으로 찾기
        match = re.search(r'https?://[^\s\x00-\x1f\x7f-\xff]+', decoded_text)
        if match:
            clean_url = match.group(0)
            # 끝부분에 남을 수 있는 쓰레기 문자 제거
            clean_url = clean_url.split('?')[0].split('')[0].split('\x01')[0]
            return clean_url
    except Exception:
        pass
    return url # 해독 실패 시 원래 링크 반환

def main():
    query = 'site:oecd.org (intitle:"Artificial Intelligence" OR intitle:AI) -intitle:PISA'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    file_name = 'oecd_ai_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"📡 OECD 데이터 수집 및 암호 링크 해독 시작...")
    raw_data = []

    try:
        feed = feedparser.parse(rss_url)
        entries = sorted(feed.entries, key=lambda x: x.get('published_parsed'), reverse=True)
        
        count = 0
        for entry in entries:
            if count >= 5: break
            
            title_en = entry.title.split(' - ')[0]
            
            # AI 키워드 검증
            keywords = ['AI', 'ARTIFICIAL', 'INTELLIGENCE', 'ALGORITHMS', 'GENERATIVE']
            if not any(kw in title_en.upper() for kw in keywords):
                continue

            print(f"🔑 {count+1}번째 암호 해독 중: {title_en[:30]}...")
            
            # 💡 구글 서버에 묻지 않고 내부 수식으로 링크 해독
            actual_link = decode_google_news_url(entry.link)
            
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
            print(f"✅ 완료! {len(raw_data)}건의 리포트를 해독하여 저장했습니다.")
