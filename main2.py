import asyncio
import csv
import re
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def get_exact_date(crawler, url, config, site_name):
    """기사 상세 페이지에서 날짜를 파내기 위한 이중 잠금 로직"""
    try:
        # 페이지 로딩을 기다리며 접속
        result = await crawler.arun(url=url, config=config)
        if not (result.success and result.markdown): return "날짜확인필요"
        
        content = result.markdown
        # 1. AI타임스 전용: 본문 전체에서 2026.01.28 같은 패턴을 찾음
        if site_name == "AI타임스":
            # 시/분까지 붙어있는 패턴을 먼저 찾음 (가장 정확)
            match = re.search(r'(\d{4}\.\d{2}\.\d{2})\s+\d{2}:\d{2}', content)
            if match: return match.group(1).replace('.', '-')
            # 없으면 날짜만 있는 패턴
            match2 = re.search(r'(\d{4}\.\d{2}\.\d{2})', content)
            if match2: return match2.group(1).replace('.', '-')

        # 2. 벤처비트/테크크런치: 상단 2000자 이내에서 영문/숫자 날짜 찾기
        header = content[:2000]
        # 숫자형 (2026-01-28)
        date_match = re.search(r'(\d{4}[-./]\d{2}[-./]\d{2})', header)
        if date_match: return date_match.group(1).replace('.', '-').replace('/', '-')
        
        # 영문형 (January 28, 2026)
        eng_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', header)
        if eng_match:
            dt = datetime.strptime(eng_match.group(1), "%B %d, %Y")
            return dt.strftime("%Y-%m-%d")
            
    except: pass
    return "날짜확인필요"

async def main():
    target_sites = {
        "AI타임스": "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1",
        "벤처비트": "https://venturebeat.com/category/ai/",
        "테크크런치": "https://techcrunch.com/category/artificial-intelligence/"
    }

    # 2025, 2026년 기사만 인정
    allowed_years = ['2025', '2026']
    
    browser_config = BrowserConfig(browser_type="chromium", headless=True)
    # AI타임스 날짜 로딩을 위해 5초 대기 옵션
    run_config = CrawlerRunConfig(
        wait_for="body", 
        delay_before_return_html=5.0 
    )
    
    final_data = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for site_name, url in target_sites.items():
            print(f"📡 [{site_name}] 수집 중... (잠시만 기다려주세요)")
            list_result = await crawler.arun(url=url, config=run_config)

            if list_result.success and list_result.markdown:
                # 기사 링크 추출
                links = re.findall(r'\[([^\]]{28,})\]\(([^\)]+)\)', list_result.markdown)
                
                count = 0
                for title, link in links:
                    title_clean = re.sub(r'[\[\]\r\n\t]', '', title).strip()
                    # 이미지 및 불필요 링크 제거
                    if "![" in title or any(ext in link.lower() for ext in ['.jpg', '.png', 'wp-content']): continue
                    
                    full_link = urljoin(url, link)
                    if any(d['제목'] == title_clean for d in final_data): continue

                    # 기사 안으로 들어가서 날짜 가져오기
                    print(f"   🔎 상세 페이지 확인: {title_clean[:15]}...")
                    exact_date = await get_exact_date(crawler, full_link, run_config, site_name)
                    
                    # 연도 필터링
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
                    if count >= 6: break # 한 사이트당 6개씩

    # 💾 정렬: 1. 출처별(가나다) -> 2. 발행일순(최신순)
    final_data.sort(key=lambda x: (x['출처'], x['발행일']), reverse=False)
    
    file_name = 'ai_trend_report.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["출처", "수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_data)
    
    print(f"\n🎉 성공! '{file_name}' 파일을 확인해보세요.")

if __name__ == "__main__":
    asyncio.run(main())
