import asyncio
import csv
import re
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def get_exact_date(crawler, url, config):
    """기사 상세 페이지에서 실제 발행일을 정밀 추출합니다."""
    try:
        # AI타임스 등 까다로운 사이트를 위해 HTML 구조를 직접 분석
        result = await crawler.arun(url=url, config=config)
        if result.success:
            content = result.markdown
            
            # 1. AI타임스 특화 패턴: '승인 202X.XX.XX' 또는 '202X.XX.XX XX:XX'
            ai_pattern = re.search(r'(\d{4}\.\d{2}\.\d{2})\s+\d{2}:\d{2}', content)
            if ai_pattern:
                return ai_pattern.group(1).replace('.', '-')

            # 2. 일반 숫자 패턴 (YYYY-MM-DD)
            date_match = re.search(r'(\d{4}[-./]\d{2}[-./]\d{2})', content)
            if date_match:
                return date_match.group(1).replace('.', '-').replace('/', '-')
            
            # 3. 영문 날짜 변환 (백악관 등)
            eng_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', content)
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

    # 🎯 정부 기관에서 'AI' 관련 내용만 뽑기 위한 키워드
    ai_keywords = ['ai', 'intelligence', 'tech', 'digital', 'data', 'algorithm', 'cyber', '인공지능', '데이터', '디지털']

    browser_config = BrowserConfig(browser_type="chromium", headless=True)
    run_config = CrawlerRunConfig(wait_for="body", wait_for_timeout=20000)
    
    final_data = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for site_name, url in target_sites.items():
            print(f"📡 [{site_name}] 데이터 정밀 스캔 중...")
            list_result = await crawler.arun(url=url, config=run_config)

            if list_result.success and list_result.markdown:
                links = re.findall(r'\[([^\]]{25,})\]\(([^\)]+)\)', list_result.markdown)
                
                count = 0
                for title, link in links:
                    title_clean = re.sub(r'[\[\]\r\n\t]', '', title).strip()
                    
                    # 🔍 정부 기관(백악관)의 경우 AI 키워드가 없으면 건너뜀
                    if site_name == "백악관(AI)":
                        if not any(kw in title_clean.lower() for kw in ai_keywords):
                            continue

                    # 노이즈 필터링
                    if "![" in title or any(ext in link.lower() for ext in ['.jpg', '.png', '.jpeg']): continue
                    
                    full_link = urljoin(url, link)
                    if any(d['제목'] == title_clean for d in final_data): continue

                    # 📅 상세 페이지 깊이 분석 (날짜 찾기)
                    print(f"   🔎 날짜 추출 중: {title_clean[:15]}...")
                    exact_date = await get_exact_date(crawler, full_link, run_config)
                    
                    # URL에서 날짜 재검증 (테크크런치 방식)
                    if exact_date == "날짜확인필요":
                        url_date = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', full_link)
                        if url_date:
                            exact_date = f"{url_date.group(1)}-{url_date.group(2)}-{url_date.group(3)}"

                    final_data.append({
                        "출처": site_name,
                        "수집일": today_str,
                        "발행일": exact_date,
                        "제목": title_clean,
                        "링크": full_link
                    })
                    count += 1
                    if count >= 8: break

    # CSV 저장
    file_name = 'ai_trend_report.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["출처", "수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_data)
    print(f"🎉 교정 완료! 이제 AI타임스 날짜와 백악관 필터가 적용되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())
