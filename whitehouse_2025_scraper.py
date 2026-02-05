import feedparser
import csv
import urllib.parse
import requests
from bs4 import BeautifulSoup
from googlenewsdecoder import gnewsdecoder
import time

def get_whitehouse_content(url):
    """백악관 원문 링크에 접속해 본문 텍스트를 가져옵니다."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # 본문을 가져오기 위해 직접 접속
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # 백악관 공식 문서의 본문 섹션 추출
            content = soup.find('section', class_='body-content')
            return content.get_text(strip=True).lower() if content else ""
    except:
        return ""
    return ""

def main():
    target_site = "whitehouse.gov/presidential-actions/"
    # 5G/6G 관련 주파수(Spectrum)와 NTIA(관리청) 등 핵심 키워드
    keywords = "(5G OR 6G OR Spectrum OR Wireless OR NTIA OR Connectivity)"
    query = f"site:{target_site} {keywords} after:2025-01-01 before:2026-01-01"
    
    rss_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    results = []

    print(f"📡 2025년 정책 본문 정밀 스캔 시작 (제목+본문 내용 검사)...")

    for entry in feed.entries:
        try:
            # 1. 링크 해독
            decoded = gnewsdecoder(entry.link)
            actual_url = decoded.get('decoded_url', entry.link)
            
            # 2. 본문 텍스트 가져오기
            full_text = get_whitehouse_content(actual_url)
            title = entry.title.split(' - ')[0].strip()

            # 3. 제목이나 본문에 우리 키워드가 있는지 확인
            check_words = ["5g", "6g", "spectrum", "wireless", "ntia", "connectivity", "telecom"]
            if any(word in title.lower() for word in check_words) or any(word in full_text for word in check_words):
                
                # 본문에서 앞부분 300자만 요약으로 추출
                summary = full_text[:300].replace(',', ' ') + "..." if full_text else "본문 내용 확인 필요"
                
                results.append({
                    "발행일": entry.published if 'published' in entry else "2025-Ongoing",
                    "제목": title,
                    "본문요약(핵심내용)": summary,
                    "원문링크": actual_url
                })
                print(f"✅ 수집 완료: {title[:30]}")
                time.sleep(1) # 차단 방지를 위한 간격
        except Exception as e:
            continue

    # 4. CSV 저장 (요약 컬럼 추가)
    file_name = 'whitehouse_5G6G_DeepScan_2025.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["발행일", "제목", "본문요약(핵심내용)", "원문링크"])
        writer.writeheader()
        writer.writerows(results)

    print(f"🏁 완료: 총 {len(results)}건의 정책 본문을 분석하여 저장했습니다.")

if __name__ == "__main__":
    main()
