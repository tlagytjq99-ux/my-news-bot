import asyncio
import csv
import re
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def get_exact_date_and_content(crawler, url, config, site_name):
    """상세 페이지에서 날짜와 AI 관련성 여부를 동시에 확인합니다."""
    try:
        result = await crawler.arun(url=url, config=config)
        if not (result.success and result.markdown): 
            return "날짜확인필요", False
        
        content = result.markdown
        header = content[:3000].lower() # 상단 3000자 분석

        # 📅 [날짜 추출]
        final_date = "날짜확인필요"
        # 1. 백악관/영문 (January 28, 2026)
        eng_match = re.search(r'([a-z]+ \d{1,2}, \d{4})', header)
        if eng_match:
            try:
                dt = datetime.strptime(eng_match.group(1), "%B %d, %Y")
                final_date = dt.strftime("%Y-%m-%d")
            except: pass
        
        # 2. 한국형/숫자형 (2026.01.28)
        if final_date == "날짜확인필요":
            match = re.search(r'(\d{4}[./-]\d{2}[./-]\d{2})', header)
            if match: final_date = match.group(1).replace('.', '-').replace('/', '-')

        # 3. 테크크런치 등 URL 날짜 보정
        if final_date == "날짜확인필요":
            url_date = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
            if url_date: final_date = f"{url_date.group(1)}-{url_date.group(2)}-{url_date.group(3)}"

        # 🔍 [AI 관련성 검증] - 백악관 등 정부 문서용
        # 단순 'Tech'를 넘어 AI 정책 핵심 단어들이 포함되었는지 확인
        ai_focus_keywords = ['ai', 'artificial intelligence', 'machine learning', 'computing', 'semiconductor', 'llm', 'algorithm', 'cybersecurity']
        is_ai_related = any(kw in header for kw in ai_focus_keywords)

        return final_date, is_ai_related
            
    except: pass
    return "날짜확인필요", False

async def main():
    target_sites = {
        "AI타임스": "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1",
        "벤처비트": "https://venturebeat.com/category/ai/",
        "테크크런치": "https://techcrunch.com/category/artificial-intelligence/",
        "백악관(AI)": "https://www.whitehouse.gov/briefing-room/statements-releases/"
    }

    allowed_years = ['2025', '2026']
    browser_config = BrowserConfig(browser_type="chromium", headless=True)
    run_config = CrawlerRunConfig(wait_for="body", delay_before_return_html=7.0)
    
    final_data = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for site_name, url in target_sites.items():
            print(f"📡 [{site_name}] 데이터 스캔 및 필터링 중...")
            list_result = await crawler.arun(url=url, config=run_config)

            if list_result.success and list_result.markdown:
                links = re.findall(r'\[([^\]]{20,})\]\(([^\)]+)\)', list_result.markdown)
                
                count = 0
                for title, link in links:
                    title_clean = re.sub(r'[\[\]\r\n\t]', '', title).strip()
                    if "![" in title or any(ext in link.lower() for ext in ['.jpg', '.png']): continue
                    
                    full_link = urljoin(url, link)
                    if any(d['제목'] == title_clean for d in final_data): continue

                    # 📅 [핵심] 상세 페이지로 들어가서 날짜와 AI 관련성 '이중 체크'
                    print(f"   🔎 정밀 분석 중: {title_clean[:12]}...")
                    exact_date, is_ai = await get_exact_date_and_content(crawler, full_link, run_config, site_name)
                    
                    # 백악관의 경우 AI 관련 내용이 확인된 것만 수집
                    if site_name == "백악관(AI)" and not is_ai:
                        continue

                    # 날짜 미확인 시 오늘 날짜로 보정 후 연도 필터링
                    date_for_filter = exact_date if exact_date != "날짜확인필요" else today_str
                    if not any(year in date_for_filter for year in allowed_years):
                        continue

                    final_data.append({
                        "출처": site_name,
                        "수집일": today_str,
                        "발행일": date_for_filter,
                        "제목": title_clean,
                        "링크": full_link
                    })
                    count += 1
                    if count >= 8: break

    # ✅ 정렬: 출처별 -> 발행일순(최신순)
    final_data.sort(key=lambda x: (x['출처'], x['발행일']), reverse=False)
    
    file_name = 'ai_trend_report.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["출처", "수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_data)
    
    print(f"\n🎉 필터링 강화 완료! 백악관의 '진짜 AI' 소식만 담았습니다.")

if __name__ == "__main__":
    asyncio.run(main())
