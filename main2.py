import asyncio
import csv
import os
import re
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def main():
    # 1. 🔗 [정보원 관리] 3대 핵심 정보원
    target_sites = {
        "AI타임스": "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1",
        "벤처비트": "https://venturebeat.com/category/ai/",
        "테크크런치": "https://techcrunch.com/category/artificial-intelligence/"
    }

    browser_config = BrowserConfig(
        browser_type="chromium", 
        headless=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    run_config = CrawlerRunConfig(
        wait_for="body", 
        wait_for_timeout=20000,
        delay_before_return_html=2.0 
    )
    
    final_data = []
    today_str = datetime.now().strftime("%Y-%m-%d") # 오늘 날짜 (수집일)

    # 🚫 제외 키워드
    exclude_keywords = ["로그인", "회원가입", "copyright", "terms", "privacy", "subscribe", "advertising", "contact"]

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for site_name, url in target_sites.items():
            try:
                print(f"📡 [{site_name}] 분석 중...")
                result = await crawler.arun(url=url, config=run_config)

                if result.success and result.markdown:
                    # 기사 제목 패턴 추출
                    links = re.findall(r'\[([^\]]{25,})\]\(([^\)]+)\)', result.markdown)
                    
                    added = 0
                    for title, link in links:
                        if "![" in title: continue
                        
                        title_clean = re.sub(r'[\[\]\r\n\t]', '', title).strip()
                        if any(kw in title_clean.lower() for kw in exclude_keywords): continue
                        if len(title_clean) < 25: continue
                        
                        full_link = urljoin(url, link)
                        if any(d['제목'] == title_clean for d in final_data): continue

                        # 📅 [발행일 추출] 기사 근처의 날짜 정보 매칭
                        date_match = re.search(r'(\d{4}[-./]\d{1,2}[-./]\d{1,2})', result.markdown)
                        pub_date = date_match.group(1) if date_match else today_str

                        final_data.append({
                            "출처": site_name,
                            "수집일": today_str,  # ✅ 수집일 추가
                            "발행일": pub_date,   # ✅ 발행일 유지
                            "제목": title_clean,
                            "링크": full_link
                        })
                        added += 1
                        if added >= 8: break
                    
                    print(f"✅ {site_name}: {added}개 뉴스 확보")
            except Exception as e:
                print(f"❌ {site_name} 실패: {e}")

    # 2. 💾 CSV 저장 (모든 컬럼 포함)
    file_name = 'ai_trend_report.csv'
    # 대표님이 보기 편하시도록 컬럼 순서를 [출처, 수집일, 발행일, 제목, 링크]로 배치했습니다.
    fieldnames = ["출처", "수집일", "발행일", "제목", "링크"]
    
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        if final_data:
            writer.writerows(final_data)
        else:
            writer.writerow({
                "출처": "-", 
                "수집일": today_str, 
                "발행일": "-", 
                "제목": "수집된 데이터가 없습니다.", 
                "링크": "-"
            })
    
    print(f"🎉 리포트 생성 완료! (총 {len(final_data)}건)")

if __name__ == "__main__":
    asyncio.run(main())
