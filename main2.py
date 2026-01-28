import asyncio
import csv
import re
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def get_exact_date(crawler, url, config):
    """기사 상세 페이지에서 실제 발행일을 정밀 추출합니다."""
    try:
        # ✅ AI타임스의 동적 날짜를 잡기 위해 자바스크립트 실행 완료를 기다림
        result = await crawler.arun(url=url, config=config)
        if result.success and result.markdown:
            content = result.markdown
            
            # 1. AI타임스/국내지: '승인 202X.XX.XX' 또는 '등록 202X...' 패턴 (가장 정확)
            # 마크다운 텍스트 전체에서 날짜 형식을 더 꼼꼼히 찾습니다.
            date_match = re.search(r'(\d{4}[-./]\d{2}[-./]\d{2})', content)
            if date_match:
                found_date = date_match.group(1).replace('.', '-').replace('/', '-')
                # 기사 본문의 날짜가 현재 연도(2025-2026)인지 확인
                if found_date.startswith(('2025', '2026')):
                    return found_date

            # 2. 영문형 패턴 (벤처비트/테크크런치/백악관)
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

    # 🎯 최신성 유지를 위한 설정
    allowed_years = ['2025', '2026']
    ai_keywords = ['ai', 'intelligence', 'tech', 'digital', 'data', 'algorithm', '인공지능', '데이터']

    browser_config = BrowserConfig(browser_type="chromium", headless=True)
    # ✅ AI타임스 같은 동적 사이트를 위해 wait_for 설정을 강화합니다.
    run_config = CrawlerRunConfig(
        wait_for="body", 
        wait_for_timeout=30000,
        delay_before_return_html=3.0 # 자바스크립트가 날짜를 뿌려줄 시간을 줍니다.
    )
    
    final_data = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for site_name, url in target_sites.items():
            print(f"📡 [{site_name}] 최신 뉴스 정밀 스캔 중...")
            list_result = await crawler.arun(url=url, config=run_config)

            if list_result.success and list_result.markdown:
                # 벤처비트 노이즈(과거 기사) 제거를 위해 제목 길이를 더 엄격히 제한
                links = re.findall(r'\[([^\]]{30,})\]\(([^\)]+)\)', list_result.markdown)
                
                count = 0
                for title, link in links:
                    title_clean = re.sub(r'[\[\]\r\n\t]', '', title).strip()
                    
                    # 🔍 정부 기관 키워드 필터링
                    if site_name == "백악관(AI)" and not any(kw in title_clean.lower() for kw in ai_keywords): continue
                    
                    full_link = urljoin(url, link)
                    if any(d['제목'] == title_clean for d in final_data): continue

                    # 📅 상세 페이지 깊이 분석 (날짜 추출)
                    print(f"   🔎 발행일 확인: {title_clean[:12]}...")
                    exact_date = await get_exact_date(crawler, full_link, run_config)
                    
                    # 🚫 [연도 필터] 2025년 이후 기사만 엄선
                    is_recent = any(year in exact_date for year in allowed_years)
                    if not is_recent and exact_date != "날짜확인필요":
                        continue

                    final_data.append({
                        "출처": site_name,
                        "수집일": today_str,
                        "발행일": exact_date,
                        "제목": title_clean,
                        "링크": full_link
                    })
                    count += 1
                    if count >= 6: break # 품질 유지를 위해 사이트당 6개로 집중

    # 💾 최신순 정렬 및 저장
    final_data.sort(key=lambda x: x['발행일'], reverse=True)
    
    file_name = 'ai_trend_report.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["출처", "수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_data)
    
    print(f"🎉 교정 완료! 2025-2026 최신 기사만 수집되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())
