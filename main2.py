import asyncio
import csv
import re
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def get_exact_date(crawler, url, config):
    """기사 상세 페이지에서 실제 발행일을 정밀 추출합니다."""
    try:
        result = await crawler.arun(url=url, config=config)
        if result.success and result.markdown:
            # 1. AI타임스 전용: '기사승인' 또는 '등록' 문구 옆 날짜 찾기
            ai_times_match = re.search(r'(?:기사승인|등록|수정)\s*[:\s]*(\d{4}[-./]\d{1,2}[-./]\d{1,2})', result.markdown)
            if ai_times_match:
                return ai_times_match.group(1).replace('.', '-').replace('/', '-')

            # 2. 일반 숫자형 날짜 (YYYY-MM-DD)
            date_match = re.search(r'(\d{4}[-./]\d{1,2}[-./]\d{1,2})', result.markdown)
            if date_match:
                return date_match.group(1).replace('.', '-').replace('/', '-')
            
            # 3. 영문형 날짜 (백악관/해외 정부기관용: January 20, 2026)
            eng_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', result.markdown)
            if eng_match:
                try:
                    dt = datetime.strptime(eng_match.group(1), "%B %d, %Y")
                    return dt.strftime("%Y-%m-%d")
                except: pass
    except: pass
    return "확인불가"

async def main():
    # ✅ 여기에 정부기관 URL을 마음껏 추가해 보세요!
    target_sites = {
        "AI타임스": "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1",
        "벤처비트": "https://venturebeat.com/category/ai/",
        "테크크런치": "https://techcrunch.com/category/artificial-intelligence/",
        "백악관(AI)": "https://www.whitehouse.gov/briefing-room/statements-releases/"
    }

    browser_config = BrowserConfig(browser_type="chromium", headless=True)
    run_config = CrawlerRunConfig(wait_for="body", wait_for_timeout=15000)
    
    final_data = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for site_name, url in target_sites.items():
            print(f"📡 [{site_name}] 분석 시작...")
            list_result = await crawler.arun(url=url, config=run_config)

            if list_result.success and list_result.markdown:
                # 제목이 포함된 링크 추출
                links = re.findall(r'\[([^\]]{25,})\]\(([^\)]+)\)', list_result.markdown)
                
                count = 0
                for title, link in links:
                    if "![" in title or any(ext in link.lower() for ext in ['.jpg', '.png', '.jpeg']): continue
                    
                    full_link = urljoin(url, link)
                    title_clean = re.sub(r'[\[\]\r\n\t]', '', title).strip()
                    
                    # 중복 체크
                    if any(d['제목'] == title_clean for d in final_data): continue

                    # 📅 상세 페이지 깊이 분석
                    print(f"   🔎 날짜 매칭 중: {title_clean[:15]}...")
                    exact_date = await get_exact_date(crawler, full_link, run_config)
                    
                    # 끝까지 못 찾으면 URL에서 추출 시도
                    if exact_date == "확인불가":
                        url_date = re.search(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', full_link)
                        if url_date:
                            exact_date = f"{url_date.group(1)}-{url_date.group(2).zfill(2)}-{url_date.group(3).zfill(2)}"
                        else:
                            exact_date = today_str # 최후의 수단

                    final_data.append({
                        "출처": site_name,
                        "수집일": today_str,
                        "발행일": exact_date,
                        "제목": title_clean,
                        "링크": full_link
                    })
                    count += 1
                    if count >= 7: break # 사이트당 7개씩

    # CSV 저장
    file_name = 'ai_trend_report.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["출처", "수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_data)
    print(f"🎉 모든 날짜 교정 완료! 파일이 생성되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())
