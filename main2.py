import asyncio
import csv
import re
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def get_exact_date(crawler, url, config):
    """기사 상세 페이지에 접속하여 실제 발행일을 추출합니다."""
    try:
        result = await crawler.arun(url=url, config=config)
        if result.success and result.markdown:
            # 1. 숫자형 날짜 (YYYY-MM-DD, YYYY.MM.DD)
            date_match = re.search(r'(\d{4}[-./]\d{1,2}[-./]\d{1,2})', result.markdown)
            if date_match:
                return date_match.group(1).replace('.', '-').replace('/', '-')
            
            # 2. 영문형 날짜 (January 20, 2026 등)
            eng_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', result.markdown)
            if eng_match:
                try:
                    dt = datetime.strptime(eng_match.group(1), "%B %d, %Y")
                    return dt.strftime("%Y-%m-%d")
                except: pass
    except: pass
    return "날짜확인불가"

async def main():
    target_sites = {
        "AI타임스": "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1",
        "벤처비트": "https://venturebeat.com/category/ai/",
        "테크크런치": "https://techcrunch.com/category/artificial-intelligence/"
    }

    browser_config = BrowserConfig(browser_type="chromium", headless=True)
    run_config = CrawlerRunConfig(wait_for="body", wait_for_timeout=15000)
    
    final_data = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for site_name, url in target_sites.items():
            print(f"📡 [{site_name}] 뉴스 목록 수집 중...")
            list_result = await crawler.arun(url=url, config=run_config)

            if list_result.success and list_result.markdown:
                links = re.findall(r'\[([^\]]{25,})\]\(([^\)]+)\)', list_result.markdown)
                
                count = 0
                for title, link in links:
                    if "![" in title or any(ext in link.lower() for ext in ['.jpg', '.png', '.jpeg']): continue
                    
                    full_link = urljoin(url, link)
                    title_clean = re.sub(r'[\[\]\r\n\t]', '', title).strip()
                    
                    # 📅 상세 페이지 접속하여 날짜 가져오기 (핵심 로직)
                    print(f"   🔍 기사 분석 중: {title_clean[:20]}...")
                    exact_date = await get_exact_date(crawler, full_link, run_config)
                    
                    # 상세 페이지에서 못 찾으면 URL에서라도 시도
                    if exact_date == "날짜확인불가":
                        url_date = re.search(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', full_link)
                        if url_date:
                            exact_date = f"{url_date.group(1)}-{url_date.group(2).zfill(2)}-{url_date.group(3).zfill(2)}"

                    final_data.append({
                        "출처": site_name,
                        "수집일": today_str,
                        "발행일": exact_date,
                        "제목": title_clean,
                        "링크": full_link
                    })
                    count += 1
                    if count >= 5: break # 상세 페이지 접속을 위해 개수를 5개로 제한

    # CSV 저장
    file_name = 'ai_trend_report.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["출처", "수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_data)
    print(f"🎉 상세 분석 리포트 생성 완료!")

if __name__ == "__main__":
    asyncio.run(main())
