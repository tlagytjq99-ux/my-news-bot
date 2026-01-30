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
    
    print(f"📡 [통합 엔진] 전략 리포트 수집 시작 (McKinsey + PwC)...")
    new_data = []

    # --- [섹션 1: McKinsey 수집 (RSS 방식)] ---
    print(f"🔍 McKinsey 분석 중...")
    try:
        mck_feed = feedparser.parse("https://www.mckinsey.com/insights/rss")
        mck_count = 0
        for entry in mck_feed.entries:
            title_en = entry.title
            # AI 및 비즈니스 핵심 키워드 필터
            if any(kw in title_en.upper() for kw in ['AI', 'TECH', 'DIGITAL', 'DATA', 'GEN', 'STRATEGY']):
                try:
                    title_ko = translator.translate(title_en, src='en', dest='ko').text
                except:
                    title_ko = title_en
                
                new_data.append({
                    "기관": "McKinsey",
                    "발행일": time.strftime('%Y-%m-%d', entry.published_parsed) if 'published_parsed' in entry else collected_date,
                    "제목": title_ko,
                    "원문": title_en,
                    "링크": entry.link,
                    "수집일": collected_date
                })
                mck_count += 1
            if mck_count >= 10: break
        print(f"   ✅ McKinsey에서 {mck_count}건 확보!")
    except Exception as e:
        print(f"   ⚠️ McKinsey 수집 중 오류: {e}")

    # --- [섹션 2: PwC 수집 (직접 크롤링 방식)] ---
    print(f"🔍 PwC 기술 섹션 공략 중...")
    pwc_url = "https://www.pwc.com/gx/en/issues/technology.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(pwc_url, headers=headers, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # PwC의 실제 리포트 제목들은 보통 h3 또는 특정 클래스의 a 태그에 담깁니다.
            articles = soup.find_all(['h3', 'h4'])
            pwc_count = 0
            
            for art in articles:
                title_en = art.get_text().strip()
                
                # 💡 핵심 필터: 
                # 1. 제목이 25자 이상이어야 함 (메뉴 이름은 보통 짧음)
                # 2. 테크 관련 핵심 키워드가 포함되어야 함
                tech_keywords = ['AI', 'GEN', 'DIGITAL', 'INTELLIGENCE', 'TECH', 'DATA', 'FUTURE', 'TRANSFORMATION']
                
                if len(title_en) > 25 and any(kw in title_en.upper() for kw in tech_keywords):
                    link_tag = art.find_parent('a') or art.find('a') or art.select_one('a')
                    if not link_tag: # 주변에서 링크 찾기 시도
                        link_tag = art.find_next('a') or art.find_previous('a')
                        
                    if link_tag:
                        href = link_tag.get('href', '')
                        full_url = f"https://www.pwc.com{href}" if href.startswith('/') else href
                        
                        # 중복 수집 방지
                        if not any(d['원문'] == title_en for d in new_data):
                            try:
                                title_ko = translator.translate(title_en, src='en', dest='ko').text
                            except:
                                title_ko = title_en

                            new_data.append({
                                "기관": "PwC",
                                "발행일": collected_date, # 웹페이지 직접 수집은 정확한 날짜 추출이 어려워 수집일로 표시
                                "제목": title_ko,
                                "원문": title_en,
                                "링크": full_url,
                                "수집일": collected_date
                            })
                            pwc_count += 1
                if pwc_count >= 10: break
            print(f"   ✅ PwC에서 {pwc_count}건 정밀 확보!")
        else:
            print(f"   ❌ PwC 접속 실패 (코드: {response.status_code})")
    except Exception as e:
        print(f"   ❌ PwC 크롤링 중 오류: {e}")

    # --- [섹션 3: 데이터 저장] ---
    if new_data:
        # 발행일 기준 내림차순 정렬
        new_data.sort(key=lambda x: x['발행일'], reverse=True)
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ["기관", "발행일", "제목", "원문", "링크", "수집일"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(new_data)
        print(f"\n🎉 모든 작업 완료! {file_name} 파일을 확인하세요.")
    else:
        print("\n💡 수집된 새로운 데이터가 없습니다.")

if __name__ == "__main__":
    main()
