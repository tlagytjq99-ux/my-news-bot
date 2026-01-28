import asyncio
import csv
from datetime import datetime
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def main():
    # 수집할 AI 뉴스 사이트 (구조가 그나마 표준적인 곳들)
    urls = [
        "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1",
        "https://venturebeat.com/category/ai/",
        "https://www.artificialintelligence-news.com/"
    ]

    final_results = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    # 브라우저 설정: 진짜 사람처럼 위장
    browser_config = BrowserConfig(
        headless=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for url in urls:
            print(f"📡 {url} 접속 시도 중...")
            
            # 복잡한 규칙 대신 '전체 마크다운'을 긁어와서 분석하는 방식
            result = await crawler.arun(url=url, bypass_cache=True)

            if result.success and result.markdown:
                # 마크다운 텍스트에서 [제목](링크) 형태를 찾아내는 간단한 규칙
                import re
                # 일반적인 뉴스 링크 패턴 추출
                links = re.findall(r'\[([^\]]{15,})\]\(([^\)]+)\)', result.markdown)
                
                count = 0
                for title, link in links:
                    # 광고성 링크나 짧은 메뉴는 제외
                    if any(x in link for x in ['login', 'twitter', 'facebook', 'category', 'author']):
                        continue
                    
                    full_link = link if link.startswith('http') else f"{url.split('/')[0]}//{url.split('/')[2]}{link}"
                    
                    final_results.append({
                        "수집일": today_str,
                        "발행일": today_str, # 무료 버전에서는 오늘 날짜로 통일
                        "제목": title.strip(),
                        "링크": full_link
                    })
                    count += 1
                    if count >= 5: break
                
                print(f"✅ {url}: {count}개 수집 완료")

    # 결과 저장
    with open('ai_trend_report.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        if final_results:
            writer.writerows(final_results)
        else:
            writer.writerow({"수집일": today_str, "발행일": "-", "제목": "여전히 수집 실패. 사이트 보안이 강력합니다.", "링크": "-"})

if __name__ == "__main__":
    asyncio.run(main())
