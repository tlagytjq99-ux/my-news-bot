import asyncio
import csv
import re
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def get_exact_date(crawler, url, config, site_name):
    """사이트 특성에 맞춰 최적화된 방식으로 날짜를 추출합니다."""
    try:
        # ✅ 페이지 로딩 대기 시간을 더 확보하여 동적 데이터 수집
        result = await crawler.arun(url=url, config=config)
        if not (result.success and result.markdown): return "날짜확인필요"
        
        content = result.markdown

        # 1️⃣ AI타임스 전용 로직: '승인 202X.XX.XX' 문구를 최우선 탐색
        if site_name == "AI타임스":
            # 가장 구체적인 패턴 우선 (승인/등록 날짜)
            match = re.search(r'(?:승인|등록|수정)\s+(\d{4}\.\d{2}\.\d{2})', content)
            if match: return match.group(1).replace('.', '-')

        # 2️⃣ 일반적인 숫자 패턴 (YYYY-MM-DD)
        # 단, 벤처비트 등에서 추천 기사 날짜와 헷갈리지 않게 본문 상단 1000자 이내에서만 검색
        top_content = content[:1500] 
        date_match = re.search(r'(\d{4}[-./]\d{2}[-./]\d{2})', top_content)
        if date_match:
            found = date_match.group(1).replace('.', '-').replace('/', '-')
            if found.startswith(('2025', '2026')): return found

        # 3️⃣ 영문 패턴 (백악관 등)
        eng_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', top_content)
        if eng_match:
            dt = datetime.strptime(eng_match.group(1), "%B %d, %Y")
            return dt.strftime("%Y-%m-%d")
            
    except: pass
    return "날짜확인필요"

async def main():
    target_sites = {
        "AI타임스": "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1",
        "벤처비트": "https://venturebeat.com/category/ai/",
        "테크크런치": "https://techcrunch.com/category/artificial-intelligence/",
        "백악관(AI)": "https://www.whitehouse.gov/briefing-room/statements-releases/"
    }

    allowed_years = ['2025', '2026']
    ai_keywords = ['ai', 'intelligence', 'tech', 'digital', '인공지능', '데이터']

    browser_config = BrowserConfig(browser_type="chromium", headless=True)
    # ✅ 지연 시간을 줘서 자바스크립트가 날짜를 렌더링하게 함
    run_config = CrawlerRunConfig(
        wait_for="body", 
        wait_for_timeout=30000,
        delay_before_return_html=5.0 
    )
    
    final_data = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for site_name, url in target_sites.items():
            print(f"📡 [{site_name}] 분석 중...")
            list_result = await crawler.arun(url=url, config=run_config)

            if list_result.success and list_result.markdown:
                # 노이즈를 피하기 위해 제목이 긴 것만 추출
                links = re.findall(r'\[([^\]]{28,})\]\(([^\)]+)\)', list_result.markdown)
                
                count = 0
                for title, link in links:
                    title_clean = re.sub(r'[\[\]\r\n\t]', '', title).strip()
                    
                    # 필터링 (이미지, 키워드 등)
                    if "![" in title or any(ext in link.lower() for ext in ['.jpg', '.png', 'wp-content']): continue
                    if site_name == "백악관(AI)" and not any(kw in title_clean.lower() for kw in ai_keywords): continue
                    
                    full_link = urljoin(url, link)
                    if any(d['제목'] == title_clean for d in final_data): continue

                    # 📅 날짜 추출 (본문 깊숙이 진입)
                    exact_date = await get_exact_date(crawler, full_link, run_config, site_name)
                    
                    # 🚫 최신 기사만 엄격하게 필터링
                    if not any(year in exact_date for year in allowed_years):
                        if exact_date != "날짜확인필요": continue

                    final_data.append({
                        "출처": site_name,
                        "수집일": today_str,
                        "발행일": exact_date,
                        "제목": title_clean,
                        "링크": full_link
                    })
                    count += 1
                    if count >= 6: break

    # 발행일 기준 내림차순 정렬 (최신순)
    final_data.sort(key=lambda x: x['발행일'], reverse=True)
    
    file_name = 'ai_trend_report.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["출처", "수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_data)
    
    print(f"🎉 모든 교정이 완료된 리포트가 생성되었습니다!")

if __name__ == "__main__":
    asyncio.run(main())
