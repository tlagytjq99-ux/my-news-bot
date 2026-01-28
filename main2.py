import asyncio
import csv
import re
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def get_exact_date(crawler, url, config, site_name):
    """실패 없는 날짜 추출을 위해 사이트별 전용 로직만 가동합니다."""
    try:
        result = await crawler.arun(url=url, config=config)
        if not (result.success and result.markdown): return "날짜확인필요"
        
        content = result.markdown[:2500] # 상단 영역 집중

        # AI타임스: '2026.01.28' 형태를 찾아서 '-'로 변환
        if site_name == "AI타임스":
            match = re.search(r'(\d{4}\.\d{2}\.\d{2})', content)
            if match: return match.group(1).replace('.', '-')

        # 테크크런치/벤처비트: URL에서 날짜 추출 (본문보다 100% 정확함)
        url_date = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
        if url_date:
            return f"{url_date.group(1)}-{url_date.group(2)}-{url_date.group(3)}"

        # 공통 영문 날짜 (January 28, 2026)
        eng_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', content)
        if eng_match:
            dt = datetime.strptime(eng_match.group(1), "%B %d, %Y")
            return dt.strftime("%Y-%m-%d")
            
    except: pass
    return "날짜확인필요"

async def main():
    # 🔗 백악관은 일단 제외하고 핵심 뉴스 3사만 집중 타격
    target_sites = {
        "AI타임스": "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1",
        "벤처비트": "https://venturebeat.com/category/ai/",
        "테크크런치": "https://techcrunch.com/category/artificial-intelligence/"
    }

    allowed_years = ['2025', '2026']
    browser_config = BrowserConfig(browser_type="chromium", headless=True)
    # AI타임스 로딩을 위해 8초 대기 설정
    run_config = CrawlerRunConfig(wait_for="body", delay_before_return_html=8.0)
    
    final_data = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for site_name, url in target_sites.items():
            print(f"📡 [{site_name}] 데이터 복구 시작...")
            list_result = await crawler.arun(url=url, config=run_config)

            if list_result.success and list_result.markdown:
                # 기사 링크만 추출 (불필요한 이미지 링크 차단)
                links = re.findall(r'\[([^\]]{20,})\]\(([^\)]+)\)', list_result.markdown)
                
                count = 0
                for title, link in links:
                    title_clean = re.sub(r'[\[\]\r\n\t]', '', title).strip()
                    full_link = urljoin(url, link)

                    # 🚫 노이즈 차단 로직 강화
                    if any(x in full_link.lower() for x in ['view_type=sm', 'googlelogo', 'author', 'sponsored']): continue
                    if "![" in title_clean: continue

                    if any(d['제목'] == title_clean for d in final_data): continue

                    print(f"   🔎 날짜 확인: {title_clean[:15]}...")
                    exact_date = await get_exact_date(crawler, full_link, run_config, site_name)
                    
                    # 📅 날짜 보정: 확인 안 되면 수집일로 표시하되 2026년 유지
                    final_date = exact_date if exact_date != "날짜확인필요" else today_str
                    
                    if not any(year in final_date for year in allowed_years): continue

                    final_data.append({
                        "출처": site_name,
                        "수집일": today_str,
                        "발행일": final_date,
                        "제목": title_clean,
                        "링크": full_link
                    })
                    count += 1
                    if count >= 7: break

    # ✅ 정렬: 출처별 -> 날짜순
    final_data.sort(key=lambda x: (x['출처'], x['발행일']), reverse=False)
    
    file_name = 'ai_trend_report.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["출처", "수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_data)
    
    print(f"\n🎉 복구 완료! 깨끗해진 '{file_name}'를 확인하세요.")

if __name__ == "__main__":
    asyncio.run(main())
