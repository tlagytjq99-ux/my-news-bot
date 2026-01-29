import asyncio
import csv
import re
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def get_exact_date(crawler, url, config, site_name):
    """기사 상세 페이지에서 날짜를 정밀하게 추출"""
    try:
        result = await crawler.arun(url=url, config=config)
        if not (result.success and result.markdown): return "날짜확인필요"
        
        content = result.markdown
        header = content[:2500] # 상단 영역 집중 분석

        # 1. 한국 사이트 (AI타임스 등)
        if any(kw in site_name for kw in ["AI타임스", "국내"]):
            match = re.search(r'(\d{4}\.\d{2}\.\d{2})', header)
            if match: return match.group(1).replace('.', '-')

        # 2. 영문 사이트 (백악관, 벤처비트 등)
        eng_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', header)
        if eng_match:
            dt = datetime.strptime(eng_match.group(1), "%B %d, %Y")
            return dt.strftime("%Y-%m-%d")
            
        # 3. URL에서 날짜 파내기 (테크크런치 등)
        url_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
        if url_match: return f"{url_match.group(1)}-{url_match.group(2)}-{url_match.group(3)}"

    except: pass
    return "날짜확인필요"

async def main():
    # 수집 대상 사이트 (백악관 포함)
    target_sites = {
        "AI타임스": "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1",
        "벤처비트": "https://venturebeat.com/category/ai/",
        "테크크런치": "https://techcrunch.com/category/artificial-intelligence/",
        "백악관(AI)": "https://www.whitehouse.gov/briefing-room/" # 브리핑룸 전체에서 검색
    }

    # 🎯 [핵심] AI 관련 핵심 키워드 (이 중 하나라도 제목에 있어야 함)
    ai_keywords = [
        'AI', '인공지능', 'GPT', 'LLM', 'CHATGPT', 'OPENAI', 'ANTHROPIC', 
        'DEEPMIND', '머신러닝', 'MACHINE LEARNING', 'GENAI', 'NVIDIA', 'CHIP'
    ]
    
    allowed_years = ['2025', '2026']
    browser_config = BrowserConfig(browser_type="chromium", headless=True)
    run_config = CrawlerRunConfig(wait_for="body", delay_before_return_html=7.0)
    
    final_data = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for site_name, url in target_sites.items():
            print(f"📡 [{site_name}] AI 뉴스 선별 수집 중...")
            list_result = await crawler.arun(url=url, config=run_config)

            if list_result.success and list_result.markdown:
                # 마크다운 핀셋으로 제목/링크 추출
                links = re.findall(r'\[([^\]]{20,})\]\(([^\)]+)\)', list_result.markdown)
                
                count = 0
                for title, link in links:
                    title_clean = re.sub(r'[\[\]\r\n\t]', '', title).strip()
                    
                    # 1️⃣ [AI 필터] 제목에 AI 키워드가 없으면 가차없이 버림
                    if not any(kw in title_clean.upper() for kw in ai_keywords):
                        continue
                    
                    # 2️⃣ [노이즈 필터] 이미지, 페이스북 공유 링크 등 제거
                    if any(x in link.lower() for x in ['facebook', 'twitter', '.jpg', '.png', 'wp-content']):
                        continue

                    full_link = urljoin(url, link)
                    if any(d['제목'] == title_clean for d in final_data): continue

                    print(f"   🔎 AI 뉴스 확인됨: {title_clean[:20]}...")
                    exact_date = await get_exact_date(crawler, full_link, run_config, site_name)
                    
                    # 연도 확인 및 미확인 날짜 처리
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
                    if count >= 6: break # 품질을 위해 사이트당 6개 엄선

    # 정렬: 출처 -> 발행일순
    final_data.sort(key=lambda x: (x['출처'], x['발행일']), reverse=False)
    
    file_name = 'ai_only_trend_report.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["출처", "수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_data)
    
    print(f"\n🎉 완료! AI 기사만 엄선된 '{file_name}'를 확인하세요.")

if __name__ == "__main__":
    asyncio.run(main())
