import asyncio
import csv
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def main():
    # 🔗 관리할 정보원 리스트 (여기에 계속 추가하시면 됩니다)
    target_sites = {
        "AI타임스": "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1",
        "벤처비트": "https://venturebeat.com/category/ai/",
        "테크크런치": "https://techcrunch.com/category/artificial-intelligence/",
        "AI뉴스(영국)": "https://www.artificialintelligence-news.com/",
        "보안뉴스": "https://www.boannews.com/media/list.asp?mkind=1"
    }

    browser_config = BrowserConfig(browser_type="chromium", headless=True)
    run_config = CrawlerRunConfig(wait_for="h2, h3, a", wait_for_timeout=15000)
    
    final_data = []
    today = datetime.now().strftime("%Y-%m-%d")
    exclude_keywords = ["바로가기", "로그인", "회원가입", "copyright", "terms"]

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # 정보원이 많아지면 하나씩(For문) 수집하는 것이 안전합니다.
        for site_name, url in target_sites.items():
            try:
                print(f"📡 [{site_name}] 수집 중...")
                result = await crawler.arun(url=url, config=run_config)

                if result.success and result.markdown:
                    import re
                    # 뉴스 제목은 보통 20자 이상인 경우가 많습니다.
                    links = re.findall(r'\[([^\]]{20,})\]\(([^\)]+)\)', result.markdown)
                    
                    added = 0
                    for title, link in links:
                        title_clean = title.strip()
                        if any(kw in title_clean.lower() for kw in exclude_keywords): continue
                        
                        full_link = urljoin(url, link)
                        final_data.append({
                            "출처": site_name,
                            "수집일": today,
                            "제목": title_clean,
                            "링크": full_link
                        })
                        added += 1
                        if added >= 5: break # 사이트당 5개씩만
                    print(f"✅ {site_name}: {added}개 수집 완료")
            except Exception as e:
                print(f"❌ {site_name} 에러 발생: {e}")

    # 데이터 저장
    if final_data:
        with open('ai_trend_report.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["출처", "수집일", "제목", "링크"])
            writer.writeheader()
            writer.writerows(final_data)
        print(f"🎉 총 {len(final_data)}개의 뉴스가 저장되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())
