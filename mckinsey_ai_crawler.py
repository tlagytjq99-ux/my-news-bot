import requests
from bs4 import BeautifulSoup
import feedparser
import csv
import os
import time
from datetime import datetime
from googletrans import Translator

def main():
    file_name = 'ai_market_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📡 [통합 엔진] 수집 시작 (McKinsey + PwC 정밀 타격)...")
    new_data = []

    # --- [McKinsey: RSS 방식] ---
    print(f"🔍 McKinsey 분석 중...")
    try:
        mck_feed = feedparser.parse("https://www.mckinsey.com/insights/rss")
        for entry in mck_feed.entries[:12]:
            try:
                title_ko = translator.translate(entry.title, dest='ko').text
                new_data.append({
                    "기관": "McKinsey",
                    "발행일": time.strftime('%Y-%m-%d', entry.published_parsed) if 'published_parsed' in entry else collected_date,
                    "제목": title_ko, "원문": entry.title, "링크": entry.link, "수집일": collected_date
                })
            except:
                continue
        print(f"   ✅ McKinsey 확보 완료")
    except Exception as e:
        print(f"   ⚠️ McKinsey 오류: {e}")

    # --- [PwC: 광범위 텍스트 수색 방식] ---
    print(f"🔍 PwC 기술 섹션 수색 중 (범위 확대)...")
    pwc_url = "https://www.pwc.com/gx/en/issues/technology.html"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        res = requests.get(pwc_url, headers=headers, timeout=30)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            pwc_count = 0
            # a, h3, h4, span 태그를 모두 뒤져서 데이터를 찾습니다.
            potential_items = soup.find_all(['a', 'h3', 'h4', 'span'])
            
            for item in potential_items:
                text = item.get_text().strip()
                # 필터: 제목 길이(25~150자) 및 핵심 키워드 포함 여부
                if 25 < len(text) < 150:
                    upper_text = text.upper()
                    if any(kw in upper_text for kw in ['AI', 'GEN', 'DIGITAL', 'INTELLIGENCE', 'TECH', 'CLOUD', 'DATA']):
                        
                        # 링크 추출 로직
                        link = ""
                        if item.name == 'a': 
                            link = item.get('href', '')
                        else:
                            parent_a = item.find_parent('a')
                            if parent_a: link = parent_a.get('href', '')
                        
                        if link and not link.startswith('#'):
                            full_url = f"https://www.pwc.com{link}" if link.startswith('/') else link
                            
                            # 중복 제거
                            if not any(d['원문'] == text for d in new_data):
                                try:
                                    title_ko = translator.translate(text, dest='ko').text
                                    new_data.append({
                                        "기관": "PwC", 
                                        "발행일": collected_date,
                                        "제목": title_ko, 
                                        "원문": text, 
                                        "링크": full_url, 
                                        "수집일": collected_date
                                    })
                                    pwc_count += 1
                                    print(f"   ✨ PwC 발견: {title_ko[:20]}...")
                                except:
                                    continue
                    if pwc_count >= 10: break
            print(f"   ✅ PwC에서 {pwc_count}건 정밀 확보!")
        else:
            print(f"   ❌ PwC 접속 실패 (상태 코드: {res.status_code})")
    except Exception as e:
        print(f"   ❌ PwC 에러: {e}")

    # --- [저장] ---
    if new_data:
        # 최신순 정렬
        new_data.sort(key=lambda x: x['발행일'], reverse=True)
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
            writer.writeheader()
            writer.writerows(new_data)
        print(f"\n🎉 성공! 총 {len(new_data)}건의 데이터를 확보했습니다.")
    else:
        print("\n💡 수집된 새로운 데이터가 없습니다.")

if __name__ == "__main__":
    main()
