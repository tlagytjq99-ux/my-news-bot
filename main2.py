import asyncio
import csv
import os
import re
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def main():
    # 1. 🔗 [정보원 정밀 타격] RSS가 아닌 실제 뉴스 목록 웹 페이지 주소
    target_sites = {
        "AI타임스": "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1",
        "벤처비트": "https://venturebeat.com/category/ai/",
        "테크크런치": "https://techcrunch.com/category/artificial-intelligence/",
        "AI뉴스(영국)": "https://www.artificialintelligence-news.com/",
        "더버지(AI)": "https://www.theverge.com/ai-artificial-intelligence",
        "전자신문AI": "https://www.etnews.com/news/section.html?id1=20&id2=065"
    }

    browser_config = BrowserConfig(
        browser_type="chromium", 
        headless=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    # Playwright가 페이지 자바스크립트를 실행할 시간을 충분히 줍니다.
    run_config = CrawlerRunConfig(
        wait_for="body", 
        wait_for_timeout=20000,
        delay_before_return_html=2.0 
    )
    
    final_data = []
    today = datetime.now().strftime("%Y-%m-%d")

    # 🚫 노이즈 차단 키워드 리스트
    exclude_keywords = [
        "바로가기", "로그인", "회원가입", "copyright", "terms", "privacy", 
        "newsletter", "advertising", "contact", "policy", "subscribe",
        "media", "entertainment", "startup battlefield", "skip to content"
    ]

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for site_name, url in target_sites.items():
            try:
                print(f"📡 [{site_name}] 뉴스 목록 분석 중...")
                result = await crawler.arun(url=url, config=run_config)

                if result.success and result.markdown:
                    # [제목](링크) 패턴 추출 (제목이 최소 20자 이상인 것만)
                    links = re.findall(r'\[([^\]]{20,})\]\(([^\)]+)\)', result.markdown)
                    
                    added = 0
                    for title, link in links:
                        # 1. 이미지 태그(![...]) 원천 차단
                        if "![" in title: continue
                        
                        # 2. 제목 정제 (불필요한 대괄호, 줄바꿈 제거)
                        title_clean = re.sub(r'[\[\]\r\n\t]', '', title).strip()
                        
                        # 3. 필터링 조건 (제외 키워드 및 길이)
                        if any(kw in title_clean.lower() for kw in exclude_keywords): continue
                        if len(title_clean) < 25: continue # 너무 짧은 메뉴형 제목 배제
                        
                        # 4. 링크 보정
                        full_link = urljoin(url, link)
                        
                        # 5. 중복 기사 방지 (제목 기준)
                        if any(d['제목'] == title_clean for d in final_data): continue

                        final_data.append({
                            "출처": site_name,
                            "수집일": today,
                            "제목": title_clean,
                            "링크": full_link
                        })
                        added += 1
                        if added >= 8: break # 사이트당 최대 8개 기사 수집
                    
                    print(f"✅ {site_name}: {added}개 뉴스 확보")
            except Exception as e:
                print(f"❌ {site_name} 수집 실패: {e}")

    # 2. 💾 CSV 결과 저장
    file_name = 'ai_trend_report.csv'
    if final_data:
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["출처", "수집일", "제목", "링크"])
            writer.writeheader()
            writer.writerows(final_data)
        print(f"🎉 리포트 생성 완료! (총 {len(final_data)}건)")
    else:
        # 데이터가 없을 때도 빈 파일은 생성하여 에러 방지
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            f.write("출처,수집일,제목,링크\n-,2026-01-28,수집된 데이터가 없습니다,-")
        print("⚠️ 수집된 데이터가 없어 빈 파일을 생성했습니다.")

if __name__ == "__main__":
    asyncio.run(main())
