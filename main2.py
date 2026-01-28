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
        "테크크런치": "https://techcrunch.com/category/artificial-intelligence/",
        "백악관(보도자료)": "https://www.whitehouse.gov/briefing-room/statements-releases/" # 정부기관 테스트용 추가
    }

    browser_config = BrowserConfig(browser_type="chromium", headless=True)
    # 날짜 데이터 로딩을 위해 대기 시간 최적화
    run_config = CrawlerRunConfig(wait_for="body", wait_for_timeout=25000)
    
    final_data = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for site_name, url in target_sites.items():
            try:
                print(f"📡 [{site_name}] 발행일 정밀 분석 중...")
                result = await crawler.arun(url=url, config=run_config)

                if result.success and result.markdown:
                    # [제목](링크) 패턴 추출
                    links = re.findall(r'\[([^\]]{20,})\]\(([^\)]+)\)', result.markdown)
                    
                    added = 0
                    for title, link in links:
                        # 🚫 이미지 및 노이즈 차단 (강화됨)
                        if "![" in title or any(ext in link.lower() for ext in ['.jpg', '.png', '.jpeg', '.gif', 'wp-content']): continue
                        
                        title_clean = re.sub(r'[\[\]\r\n\t]', '', title).strip()
                        if len(title_clean) < 25: continue
                        
                        full_link = urljoin(url, link)
                        if any(d['제목'] == title_clean for d in final_data): continue

                        # 📅 [사이트별 맞춤형 발행일 추출]
                        pub_date = "확인불가"
                        
                        # 기사 제목 근처 텍스트에서 날짜 탐색 범위 확대
                        title_index = result.markdown.find(title)
                        search_area = result.markdown[max(0, title_index-150) : title_index+300]

                        # 1순위: YYYY-MM-DD 또는 YYYY.MM.DD (AI타임스 등)
                        date_pattern = re.search(r'(\d{4}[-./]\d{1,2}[-./]\d{1,2})', search_area)
                        
                        # 2순위: 영문 날짜 (January 20, 2026 등 - 벤처비트/백악관용)
                        eng_date_pattern = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', search_area)

                        if date_pattern:
                            pub_date = date_pattern.group(1).replace('.', '-').replace('/', '-')
                        elif eng_date_pattern:
                            try:
                                # 영문 날짜를 YYYY-MM-DD로 변환
                                d = datetime.strptime(eng_date_pattern.group(1), "%B %d, %Y")
                                pub_date = d.strftime("%Y-%m-%d")
                            except:
                                pub_date = eng_date_pattern.group(1) # 변환 실패 시 원문 유지
                        elif "/202" in full_link: # 3순위: URL 내 날짜 포함 시
                            url_match = re.search(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', full_link)
                            if url_match:
                                pub_date = f"{url_match.group(1)}-{url_match.group(2).zfill(2)}-{url_match.group(3).zfill(2)}"

                        # 날짜를 전혀 못 찾은 경우에만 오늘 날짜 기입
                        if pub_date == "확인불가":
                            pub_date = today_str

                        final_data.append({
                            "출처": site_name,
                            "수집일": today_str,
                            "발행일": pub_date,
                            "제목": title_clean,
                            "링크": full_link
                        })
                        added += 1
                        if added >= 10: break
                    
                    print(f"✅ {site_name}: {added}개 수집 완료")
            except Exception as e:
                print(f"❌ {site_name} 오류: {e}")

    # CSV 저장
    file_name = 'ai_trend_report.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["출처", "수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_data)
    
    print(f"🎉 모든 필터링 및 날짜 교정 완료!")

if __name__ == "__main__":
    asyncio.run(main())
