import asyncio
import csv
import os
import re
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def main():
    # 🔗 [정보원 관리] 여기에 새로운 사이트를 계속 추가하세요!
    target_sites = {
        "AI타임스": "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1",
        "벤처비트": "https://venturebeat.com/category/ai/",
        "테크크런치": "https://techcrunch.com/category/artificial-intelligence/",
        "AI뉴스(영국)": "https://www.artificialintelligence-news.com/",
        "전자신문AI": "https://www.etnews.com/news/section.html?id1=20&id2=065",
        "ZDNet_AI": "https://zdnet.co.kr/newskey/?lstkey=인공지능"
    }

    browser_config = BrowserConfig(browser_type="chromium", headless=True)
    # 로딩 시간을 충분히 주어 누락 방지
    run_config = CrawlerRunConfig(wait_for="body", wait_for_timeout=20000)
    
    final_data = []
    today = datetime.now().strftime("%Y-%m-%d")

    # 🚫 강화된 필터링 키워드 (메뉴, 로고, 카테고리 등 제거)
    exclude_keywords = [
        "바로가기", "로그인", "회원가입", "copyright", "terms", "privacy", 
        "newsletter", "brand studio", "battlefield", "advertising", "contact",
        "policy", "media", "entertainment", "subscribe", "events"
    ]

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for site_name, url in target_sites.items():
            try:
                print(f"📡 [{site_name}] 데이터 수집 시도...")
                result = await crawler.arun(url=url, config=run_config)

                if result.success and result.markdown:
                    # 마크다운 내 링크 패턴 [제목](링크) 추출
                    # 제목이 너무 짧으면 메뉴일 확률이 높으므로 25자 이상으로 필터링
                    links = re.findall(r'\[([^\]]{25,})\]\(([^\)]+)\)', result.markdown)
                    
                    added = 0
                    for title, link in links:
                        title_clean = title.replace("\n", " ").strip()
                        
                        # 1. 제외 키워드 검사
                        if any(kw in title_clean.lower() for kw in exclude_keywords): continue
                        # 2. 이미지가 섞인 링크 제거 (![...])
                        if "![" in title_clean: continue
                        # 3. 특수문자로만 된 제목 제거
                        if not re.search('[a-zA-Z가-힣]', title_clean): continue

                        full_link = urljoin(url, link)
                        
                        final_data.append({
                            "출처": site_name,
                            "수집일": today,
                            "제목": title_clean,
                            "링크": full_link
                        })
                        added += 1
                        if added >= 8: break # 사이트당 최대 8개까지
                    
                    print(f"✅ {site_name}: {added}개 뉴스 확보")
            except Exception as e:
                print(f"❌ {site_name} 오류: {e}")

    # 저장 로직
    if final_data:
        with open('ai_trend_report.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["출처", "수집일", "제목", "링크"])
            writer.writeheader()
            writer.writerows(final_data)
        print(f"🎉 필터링 완료! 총 {len(final_data)}개의 뉴스가 저장되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())
