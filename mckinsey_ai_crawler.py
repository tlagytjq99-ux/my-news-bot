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
    
    print(f"📡 [통합 엔진] 전략 리포트 정밀 수집 시작...")
    new_data = []

    # --- [McKinsey 수집] ---
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
            except: continue
        print(f"   ✅ McKinsey 수집 완료")
    except: print(f"   ⚠️ McKinsey 오류")

    # --- [PwC 정밀 타격 수집] ---
    print(f"🔍 PwC 리포트 본진(Technology) 공략 중...")
    pwc_url = "https://www.pwc.com/gx/en/issues/technology.html"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        res = requests.get(pwc_url, headers=headers, timeout=30)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 💡 PwC의 '진짜 리포트'가 담긴 카드 영역만 조준합니다.
        # h3 태그 중 클래스명이 title을 포함하거나, 특정 패턴을 가진 것들 위주
        articles = soup.select('div.pwc-feature-tile__content, div.item-content') 
        
        pwc_count = 0
        for art in articles:
            # 1. 제목 추출 (h3 또는 h4 태그)
            title_tag = art.find(['h3', 'h4', 'span'], class_=lambda x: x and 'title' in x.lower())
            if not title_tag:
                title_tag = art.find(['h3', 'h4'])
            
            if title_tag:
                title_en = title_tag.get_text().strip()
                
                # 메뉴 이름(너무 짧은 것)은 버리고, 리포트다운 제목만 필터링
                if len(title_en) > 30: 
                    # 2. 링크 추출
                    link_tag = art.find('a', href=True)
                    if link_tag:
                        link = link_tag['href']
                        full_url = f"https://www.pwc.com{link}" if link.startswith('/') else link
                        
                        # 중복 제거
                        if not any(d['원문'] == title_en for d in new_data):
                            try:
                                title_ko = translator.translate(title_en, dest='ko').text
                                new_data.append({
                                    "기관": "PwC", "발행일": collected_date,
                                    "제목": title_ko, "원문": title_en, "링크": full_url, "수집일": collected_date
                                })
                                pwc_count += 1
                            except: continue
            if pwc_count >= 10: break
            
        print(f"   ✅ PwC 정밀 리포트 {pwc_count}건 확보!")
    except Exception as e:
        print(f"   ❌ PwC 에러: {e}")

    # --- [저장] ---
    if new_data:
        new_data.sort(key=lambda x: x['발행일'], reverse=True)
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
            writer.writeheader()
            writer.writerows(new_data)
        print(f"\n🎉 성공! 이제 찌꺼기 없는 진짜 데이터를 확인하세요.")

if __name__ == "__main__":
    main()
