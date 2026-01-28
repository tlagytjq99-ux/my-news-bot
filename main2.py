import asyncio
import csv
import re
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def get_exact_date(crawler, url, config, site_name):
    """사이트별 맞춤형 날짜 추출 (AI타임스 정밀 타격)"""
    try:
        # ✅ 더 긴 대기시간 부여 (데이터 렌더링 보장)
        result = await crawler.arun(url=url, config=config)
        if not (result.success and result.markdown): return "날짜확인필요"
        
        content = result.markdown
        # 🔍 상단 영역만 집중 분석 (하단 카피라이트/오늘날짜 노이즈 제거)
        header_text = content[:2000]

        if site_name == "AI타임스":
            # 1순위: '승인 2026.01.28 14:30' 패턴 (가장 정확)
            match = re.search(r'(?:승인|등록|수정)\s+(\d{4}\.\d{2}\.\d{2})', header_text)
            if match: return match.group(1).replace('.', '-')
            # 2순위: '2026.01.28 14:30' 패턴
            match2 = re.search(r'(\d{4}\.\d{2}\.\d{2})\s+\d{2}:\d{2}', header_text)
            if match2: return match2.group(1).replace('.', '-')

        # 영문 사이트 (백악관, 테크크런치 등)
        eng_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', header_text)
        if eng_match:
            try:
                dt = datetime.strptime(eng_match.group(1), "%B %d, %Y")
                return dt.strftime("%Y-%m-%d")
            except: pass

        # URL에서 날짜 추출 (테크크런치/벤처비트 보조)
        url_date = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
        if url_date:
            return f"{url_date.group(1)}-{url_date.group(2)}-{url_date.group(3)}"
            
    except: pass
    return "날짜확인필요"

async def main():
    target_sites = {
        "AI타임스": "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1",
        "벤처비트": "https://venturebeat.com/category/ai/",
        "테크크런치": "https://techcrunch.com/category/artificial-intelligence/",
        "백악관(AI)": "https://www.whitehouse.gov/?s=AI" # 대표님 요청하신 검색 필터 주소
    }

    allowed_years = ['2025', '2026']
    browser_config = BrowserConfig(browser_type="chromium", headless=True)
    # ✅ AI타임스의 느린 렌더링을 위해 delay_before_return_html을 8초로 상향
    run_config = CrawlerRunConfig(
        wait_for="body", 
        delay_before_return_html=8.0 
    )
    
    final_data = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for site_name, url in target_sites.items():
            print(f"📡 [{site_name}] 분석 중...")
            list_result = await crawler.arun(url=url, config=run_config)

            if list_result.success and list_result.markdown:
                # 기사 링크 추출
                links = re.findall(r'\[([^\]]{15,})\]\(([^\)]+)\)', list_result.markdown)
                
                count = 0
                for title, link in links:
                    title_clean = re.sub(r'[\[\]\r\n\t]', '', title).strip()
                    
                    # 노이즈 필터링
                    if any(x in link.lower() for x in ['search', 'category', 'facebook', 'twitter', '.jpg']): continue
                    if site_name == "백악관(AI)" and "AI" not in title_clean.upper(): continue 

                    full_link = urljoin(url, link)
                    if any(d['제목'] == title_clean for d in final_data): continue

                    print(f"   🔎 날짜 정밀 추출: {title_clean[:12]}...")
                    exact_date = await get_exact_date(crawler, full_link, run_config, site_name)
                    
                    # 📅 날짜 검증 및 연도 필터
                    # '날짜확인필요'가 떴을 때 오늘 날짜로 덮어쓰지 않고 실제 과거 날짜를 찾도록 유도
                    if exact_date == "날짜확인필요":
                        # 최후의 수단: URL에서라도 날짜를 찾음
                        url_date = re.search(r'(\d{4})[-/](\d{2})[-/](\d{2})', full_link)
                        if url_date: exact_date = f"{url_date.group(1)}-{url_date.group(2)}-{url_date.group(3)}"
                    
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

    # ✅ 정렬: 출처별 -> 발행일순(최신순)
    final_data.sort(key=lambda x: (x['출처'], x['발행일']), reverse=False)
    
    file_name = 'ai_trend_report.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["출처", "수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_data)
    
    print(f"\n🎉 교정 완료! 엑셀 파일을 확인해보세요.")

if __name__ == "__main__":
    asyncio.run(main())
