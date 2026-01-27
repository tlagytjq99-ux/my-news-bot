import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    # 수집할 정보원 4곳 (국내 2, 해외 2)
    urls = [
        "https://www.nia.or.kr/site/nia_kor/ex/bbs/List.do?cbIdx=82618", # NIA(국내정책)
        "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1", # AI타임스(국내산업)
        "https://venturebeat.com/category/ai/", # VentureBeat(해외비즈니스)
        "https://www.artificialintelligence-news.com/" # AI News(해외기술)
    ]
    
    # 파일 이름 설정
    names = ["NIA_Policy", "AITimes_Korea", "VentureBeat_Global", "AINews_Global"]

    async with AsyncWebCrawler() as crawler:
        # 4개 사이트를 동시에 수집
        results = await crawler.arun_many(urls=urls)
        
        for i, result in enumerate(results):
            if result.success:
                filename = f"{names[i]}.md"
                with open(filename, "w", encoding="utf-8") as f:
                    # AI가 읽기 좋은 형태로 저장
                    f.write(result.markdown)
                print(f"성공: {filename}")

if __name__ == "__main__":
    asyncio.run(main())
