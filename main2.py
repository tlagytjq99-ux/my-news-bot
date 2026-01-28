import asyncio
import csv
import os
import re
from datetime import datetime
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def main():
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    urls = [
        "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1",
        "https://venturebeat.com/category/ai/",
        "https://www.artificialintelligence-news.com/"
    ]

    final_data = []
    today = datetime.now().strftime("%Y-%m-%d")

    # 🚫 제외할 단어 목록 (이미지에 나온 노이즈들)
    exclude_keywords = [
        "바로가기", "logo", "로그인", "회원가입", "menu", "skip", 
        "copyright", "terms", "privacy", "owner", "click here",
        "english news", "future energy"
    ]

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for url in urls:
            try:
                print(f"📡 {url} 정밀 필터링 중...")
                result = await crawler.arun(url=url, bypass_cache=True)

                if result.success and result.markdown:
                    # [제목](링크) 패턴 추출
                    links = re.findall(r'\[([^\]]{15,})\]\(([^\)]+)\)', result.markdown)
                    
                    added = 0
                    for title, link in links:
                        title_clean = title.strip()
                        
                        # 필터링 조건 1: 너무 짧은 제목 제외
                        if len(title_clean) < 15: continue
                        # 필터링 조건 2: 제외 단어가 포함된 경우 패스
                        if any(kw in title_clean.lower() for kw in exclude_keywords): continue
                        # 필터링 조건 3: 이미지가 포함된 마크다운 제외
                        if "![" in title_clean: continue
                        
                        full_link = link if link.startswith("http") else url + link
                        
                        final_data.append({
                            "수집일": today,
                            "발행일": today,
                            "제목": title_clean,
                            "링크": full_link
                        })
                        added += 1
                        if added >= 5: break
                    print(f"✅ {url}: {added}개 뉴스 확보")
            except Exception as e:
                print(f"❌ {url} 에러: {e}")

    # 데이터가 없을 경우 대비
    if not final_data:
        final_data.append({"수집일": today, "발행일": "-", "제목": "검색 결과 없음 (필터링 기준 미달)", "링크": "-"})

    with open('ai_trend_report.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_data)
    
    print(f"💾 필터링 완료! 파일이 저장되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())
