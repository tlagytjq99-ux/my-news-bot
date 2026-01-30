import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
from googletrans import Translator
import time

def main():
    # 🎯 맥킨지(RSS) + PwC 기술 섹션(직접 크롤링)
    target_url = "https://www.pwc.com/gx/en/issues/technology.html"
    file_name = 'ai_market_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📡 [PwC 기술섹션] 직접 공략 수집 시작...")

    new_data = []

    # 1️⃣ [McKinsey 수집] - 기존에 잘 되던 방식 유지
    try:
        import feedparser
        mck_feed = feedparser.parse("https://www.mckinsey.com/insights/rss")
        for entry in mck_feed.entries[:10]:
            new_data.append({
                "기관": "McKinsey",
                "발행일": time.strftime('%Y-%m-%d', entry.published_parsed) if 'published_parsed' in entry else collected_date,
                "제목": translator.translate(entry.title, dest='ko').text,
                "원문": entry.title,
                "링크": entry.link,
                "수집일": collected_date
            })
        print(f"   ✅ McKinsey 수집 완료")
    except:
        print(f"   ⚠️ McKinsey 수집 중 일부 오류")

    # 2️⃣ [PwC 직접 공략] - 대표님이 주신 페이지를 뚫습니다.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,ko;q=0.8"
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # PwC 페이지의 뉴스 카드 제목과 링크를 찾습니다.
            # PwC는 보통 h3 태그나 특정 클래스의 a 태그를 사용합니다.
            articles = soup.find_all(['h3', 'h4', 'a'], limit=50)
            
            pwc_count = 0
            for art in articles:
                title_en = art.get_text().strip()
                # AI, Tech 관련 글만 필터링
                if any(kw in title_en.upper() for kw in ['AI', 'TECH', 'DIGITAL', 'GEN', 'INTELLIGENCE']):
                    link = ""
                    if art.name == 'a':
                        link = art.get('href', '')
                    else:
                        parent = art.find_parent('a')
                        if parent: link = parent.get('href', '')

                    if link and len(title_en) > 20:
                        full_url = f"https://www.pwc.com{link}" if link.startswith('/') else link
                        
                        # 중복 제거 및 수집
                        if not any(d['원문'] == title_en for d in new_data):
                            try:
                                title_ko = translator.translate(title_en, dest='ko').text
                            except:
                                title_ko = title_en

                            new_data.append({
                                "기관": "PwC",
                                "발행일": collected_date, # 페이지 특성상 발행일 추출이 어려워 수집일로 대체
                                "제목": title_ko,
                                "원문": title_en,
                                "링크": full_url,
                                "수집일": collected_date
                            })
                            pwc_count += 1
                if pwc_count >= 10: break
            print(f"   ✅ PwC ({target_url})에서 {pwc_count}건 확보!")
        else:
            print(f"   ❌ PwC 페이지 접속 실패 (상태 코드: {response.status_code})")
    except Exception as e:
        print(f"   ❌ PwC 직접 크롤링 중 에러: {e}")

    # 💾 CSV 저장
    if new_data:
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
            writer.writeheader()
            writer.writerows(new_data)
        print(f"\n🎉 통합 수집 완료! 총 {len(new_data)}건 저장.")
    else:
        print("\n💡 수집된 데이터가 없습니다.")

if __name__ == "__main__":
    main()
