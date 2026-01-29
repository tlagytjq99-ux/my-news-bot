import asyncio
import csv
import re
import os
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

# --- [1. 상세 페이지 날짜 추출 함수] ---
async def get_whitehouse_date(crawler, url, config):
    """백악관 상세 페이지에서 영문 날짜를 찾아 YYYY-MM-DD로 변환"""
    try:
        result = await crawler.arun(url=url, config=config)
        if not (result.success and result.markdown):
            return "날짜확인필요"
        
        # 예: "January 29, 2026" 패턴 찾기
        content = result.markdown[:2500]
        date_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', content)
        
        if date_match:
            dt = datetime.strptime(date_match.group(1), "%B %d, %Y")
            return dt.strftime("%Y-%m-%d")
    except:
        pass
    return datetime.now().strftime("%Y-%m-%d")

# --- [2. 메인 수집 로직] ---
async def main():
    # 🎯 타켓: 백악관 브리핑룸 내 'AI' 검색 결과
    target_url = "https://www.whitehouse.gov/?s=AI&post_type=briefing-room"
    
    print(f"🚀 [시작] 백악관 AI 정책 수집 (Target: {target_url})")

    # 브라우저 및 실행 설정 (정부기관 대응용 정밀 세팅)
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    run_config = CrawlerRunConfig(
        wait_for="body", 
        delay_before_return_html=10.0, # 넉넉한 대기 시간
        cache_mode="bypass"
    )

    # 필터링 키워드
    ai_keywords = ['AI', 'ARTIFICIAL INTELLIGENCE', 'LLM', 'GPT', 'ALGORITHM', 'TECHNOLOGY']
    final_data = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        print("📡 백악관 서버에 접속 중...")
        result = await crawler.arun(url=target_url, config=run_config)
        
        if result.success and result.markdown:
            # 제목과 링크 추출 (마크다운 기반)
            links = re.findall(r'\[([^\]]{15,})\]\(([^\)]+)\)', result.markdown)
            print(f"🔎 후보 {len(links)}건 발견. 필터링 시작...")
            
            count = 0
            for title, link in links:
                title_clean = title.strip()
                
                # 1. AI 키워드 필터링
                if not any(kw in title_clean.upper() for kw in ai_keywords):
                    continue

                full_link = urljoin(target_url, link)
                
                # 2. 중복 방지
                if any(d['제목'] == title_clean for d in final_data):
                    continue

                print(f"   📂 분석 중: {title_clean[:30]}...")
                exact_date = await get_whitehouse_date(crawler, full_link, run_config)

                final_data.append({
                    "기관": "백악관(White House)",
                    "발행일": exact_date,
                    "제목": title_clean,
                    "링크": full_link,
                    "수집일": datetime.now().strftime("%Y-%m-%d")
                })
                
                count += 1
                if count >= 10: break # 한 번에 최대 10개만
                await asyncio.sleep(2) # 서버 부하 방지 휴식

    # --- [3. 결과 저장] ---
    if final_data:
        file_name = 'whitehouse_ai_report.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "링크", "수집일"])
            writer.writeheader()
            writer.writerows(final_data)
        print(f"✅ 성공! {file_name} 파일이 생성되었습니다.")
    else:
        print("❌ 수집된 새로운 AI 정보가 없습니다.")

if __name__ == "__main__":
    asyncio.run(main())
