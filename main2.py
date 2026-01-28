import asyncio
import csv
import os
import re
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def main():
    target_sites = {
        "AI타임스": "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1",
        "벤처비트": "https://venturebeat.com/category/ai/",
        "테크크런치": "https://techcrunch.com/category/artificial-intelligence/"
    }

    browser_config = BrowserConfig(browser_type="chromium", headless=True)
    run_config = CrawlerRunConfig(wait_for="body", wait_for_timeout=20000)
    
    final_data = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for site_name, url in target_sites.items():
            try:
                print(f"📡 [{site_name}] 정밀 수집 중...")
                result = await crawler.arun(url=url, config=run_config)

                if result.success and result.markdown:
                    # [제목](링크) 패턴 추출
                    links = re.findall(r'\[([^\]]{20,})\]\(([^\)]+)\)', result.markdown)
                    
                    added = 0
                    for title, link in links:
                        # 🚫 [이미지 및 노이즈 차단]
                        if "![" in title: continue
                        if any(img_ext in link.lower() for img_ext in ['.jpg', '.png', '.jpeg', '.gif', '_next/image']): continue
                        
                        title_clean = re.sub(r'[\[\]\r\n\t]', '', title).strip()
                        if len(title_clean) < 25: continue
                        
                        full_link = urljoin(url, link)
                        if any(d['제목'] == title_clean for d in final_data): continue

                        # 📅 [발행일 정밀 추출 로직]
                        pub_date = today_str # 기본값
                        
                        # 방법 1: URL에서 날짜 패턴 찾기 (테크크런치 등)
                        url_date = re.search(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', full_link)
                        if url_date:
                            pub_date = f"{url_date.group(1)}-{url_date.group(2).zfill(2)}-{url_date.group(3).zfill(2)}"
                        else:
                            # 방법 2: 마크다운 텍스트에서 제목 근처 날짜 탐색 (벤처비트 등)
                            # 기사 제목 앞뒤 100자 이내에서 날짜 형식 찾기
                            context = result.markdown[max(0, result.markdown.find(title)-100) : result.markdown.find(title)+200]
                            date_match = re.search(r'(\d{4}[-./]\d{1,2}[-./]\d{1,2})', context)
                            if date_match:
                                pub_date = date_match.group(1).replace('.', '-').replace('/', '-')

                        final_data.append({
                            "출처": site_name,
                            "수집일": today_str,
                            "발행일": pub_date,
                            "제목": title_clean,
                            "링크": full_link
                        })
                        added += 1
                        if added >= 10: break # 사이트별 10개까지 확대
                    
                    print(f"✅ {site_name}: {added}개 뉴스 확보")
            except Exception as e:
                print(f"❌ {site_name} 오류: {e}")

    # CSV 저장
    file_name = 'ai_trend_report.csv'
    fieldnames = ["출처", "수집일", "발행일", "제목", "링크"]
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_data)
    
    print(f"🎉 필터링 강화 리포트 생성 완료!")

if __name__ == "__main__":
    asyncio.run(main())
