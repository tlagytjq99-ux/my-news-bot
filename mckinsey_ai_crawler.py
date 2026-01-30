import feedparser
import csv
import time
import requests
import base64
from datetime import datetime
from googletrans import Translator

def get_original_url(google_url):
    """구글 뉴스 링크를 원래의 원본 URL로 변환하는 함수"""
    try:
        # 구글 뉴스 링크의 중간 암호화 부분을 추출하여 복호화 시도
        if "articles/" in google_url:
            base64_url = google_url.split("articles/")[1].split("?")[0]
            # 구글의 변형된 base64 패딩 처리
            base64_url += "=" * ((4 - len(base64_url) % 4) % 4)
            decoded_bytes = base64.urlsafe_b64decode(base64_url)
            # 복호화된 바이트 데이터에서 실제 URL 패턴 추출
            decoded_str = decoded_bytes.decode('latin-1')
            if "http" in decoded_str:
                # 불필요한 바이너리 데이터를 제거하고 URL만 추출
                start_idx = decoded_str.find("http")
                # URL 끝부분의 찌꺼기 제거 (일반적인 URL 문자 범위로 한정)
                import re
                clean_url = re.split(r'[^\w\d\.\/\:\%\?\&\=\-\+\_\~\#]', decoded_str[start_idx:])[0]
                return clean_url
    except:
        pass
    return google_url # 실패 시 구글 링크 유지

def main():
    # 🎯 딜로이트 쿼리를 더 정교하게 수정 (insights 섹션 집중)
    sources = [
        {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
        {"name": "MIT_Sloan", "url": "https://sloanreview.mit.edu/feed/"},
        {"name": "Deloitte", "url": "https://news.google.com/rss/search?q=site:deloitte.com+AI+insights&hl=en-US&gl=US&ceid=US:en"},
        {"name": "BCG", "url": "https://news.google.com/rss/search?q=site:bcg.com+AI&hl=en-US&gl=US&ceid=US:en"}
    ]
    
    file_name = 'ai_market_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📡 [링크 복원 엔진] 수집 및 URL 디코딩 시작...")
    new_data = []

    for source in sources:
        print(f"🔍 {source['name']} 분석 중...")
        try:
            feed = feedparser.parse(source['url'])
            count = 0
            for entry in feed.entries:
                title_en = entry.title.split(' - ')[0]
                google_link = entry.link
                
                # 💡 구글 링크를 원래 주소로 변환
                if "google.com" in google_link:
                    final_link = get_original_url(google_link)
                else:
                    final_link = google_link

                raw_date = entry.get('published_parsed', None)
                published_date = time.strftime('%Y-%m-%d', raw_date) if raw_date else collected_date

                # 제목 번역 및 수집
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
            print(f"   ✅ {source['name']} {count}건 확보 완료!")
        except Exception as e:
            print(f"   ❌ {source['name']} 에러: {e}")

    # 💾 저장
    if new_data:
        new_data.sort(key=lambda x: x['발행일'], reverse=True)
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
            writer.writeheader()
            writer.writerows(new_data)
        print(f"\n🎉 성공! 이제 깨끗한 원본 링크로 데이터를 확인하세요.")

if __name__ == "__main__":
    main()
