import asyncio
import csv
import re
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def get_exact_date(crawler, url, config, site_name):
    """기사 상세 페이지에서 실제 발행일을 정밀 추출합니다."""
    try:
        result = await crawler.arun(url=url, config=config)
        if not (result.success and result.markdown): return "날짜확인필요"
        
        content = result.markdown
        # 🔍 상단 1000자까지만 검색 (노이즈 차단)
        header_content = content[:1000]

        if site_name == "AI타임스":
            # AI타임스 패턴: '2026.01.28 14:30' 또는 '승인 2026.01.28'
            match = re.search(r'(\d{4}\.\d{2}\.\d{2})\s+\d{2}:\d{2}', header_content)
            if match: return match.group(1).replace('.', '-')
            match2 = re.search(r'(?:승인|등록)\s+(\d{4}\.\d{2}\.\d{2})', header_content)
            if match2: return match2.group(1).replace('.', '-')

        # 벤처비트/테크크런치용
        date_match = re.search(r'(\d{4}[-./]\d{2}[-./]\d{2})', header_content)
        if date_match:
            return date_match.group(1).replace('.', '-').replace('/', '-')
            
        eng_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', header_content)
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

    allowed_years = ['2025', '2026']
    browser_config = BrowserConfig(browser_type="chromium", headless=True)
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
                links = re.findall(r'\[([^\]]{28,})\]\(([^\)]+)\)', list_result.markdown)
                
                count = 0
                for title, link in links:
                    title_clean = re.sub(r'[\[\]\r\n\t]', '', title).strip()
                    if "![" in title or any(ext in link.lower() for ext in ['.jpg', '.png']): continue
                    
                    full_link = urljoin(url, link)
                    if any(d['제목'] == title_clean for d in final_data): continue

                    print(f"   🔎 날짜 확인 중: {title_clean[:15]}...")
                    exact_date = await get_exact_date(crawler, full_link, run_config, site_name)
                    
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
                    if count >= 8: break

    # ✅ [정렬 로직 수정] 
    # 1순위: 출처(가나다순/ABC순) 
    # 2순위: 발행일(최신순)
    final_data.sort(key=lambda x: (x['출처'], x['발행일']), reverse=False)
    # 발행일만 최신순으로 보고 싶으시면 아래처럼 정렬 조건을 조합합니다.
    # final_data.sort(key=lambda x: (x['출처'], datetime.strptime(x['발행일'], '%Y-%m-%d') if '-' in x['발행일'] else datetime.min), reverse=True)
    
    file_name = 'ai_trend_report.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["출처", "수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_data)
    
    print(f"🎉 출처별 정렬 완료! 리포트가 생성되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())
