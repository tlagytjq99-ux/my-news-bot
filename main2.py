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
    run_config = CrawlerRunConfig(
        wait_for="body", 
        wait_for_timeout=25000,
        # HTML 구조를 더 잘 파악하기 위해 콘텐츠 필터링 완화
        process_iframes=True
    )
    
    final_data = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for site_name, url in target_sites.items():
            try:
                print(f"📡 [{site_name}] 데이터 및 날짜 정밀 분석 중...")
                # result.html을 함께 가져오도록 설정
                result = await crawler.arun(url=url, config=run_config)

                if result.success:
                    # 마크다운과 HTML을 모두 활용하여 데이터 추출
                    content = result.markdown
                    links = re.findall(r'\[([^\]]{20,})\]\(([^\)]+)\)', content)
                    
                    added = 0
                    for title, link in links:
                        if "![" in title or any(ext in link.lower() for ext in ['.jpg', '.png', '.jpeg', '.gif']): continue
                        
                        title_clean = re.sub(r'[\[\]\r\n\t]', '', title).strip()
                        if len(title_clean) < 25: continue
                        
                        full_link = urljoin(url, link)
                        if any(d['제목'] == title_clean for d in final_data): continue

                        # 📅 [발행일 정밀 추출]
                        pub_date = "확인필요"
                        
                        # 1순위: URL에서 날짜 추출 (가장 정확함)
                        url_date = re.search(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', full_link)
                        if url_date:
                            pub_date = f"{url_date.group(1)}-{url_date.group(2).zfill(2)}-{url_date.group(3).zfill(2)}"
                        
                        # 2순위: 제목 근처 텍스트 탐색 (범위를 대폭 늘림: 앞뒤 500자)
                        if pub_date == "확인필요":
                            title_pos = content.find(title)
                            context = content[max(0, title_pos-300) : title_pos+500]
                            
                            # 숫자형 날짜 (2026.01.27 / 2026-01-27)
                            date_match = re.search(r'(\d{4}[-./]\d{1,2}[-./]\d{1,2})', context)
                            if date_match:
                                pub_date = date_match.group(1).replace('.', '-').replace('/', '-')
                            else:
                                # 영문형 날짜 (Jan 27, 2026 / January 27, 2026)
                                eng_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', context)
                                if eng_match:
                                    try:
                                        dt = datetime.strptime(eng_match.group(1), "%B %d, %Y")
                                        pub_date = dt.strftime("%Y-%m-%d")
                                    except:
                                        try:
                                            dt = datetime.strptime(eng_match.group(1), "%b %d, %Y")
                                            pub_date = dt.strftime("%Y-%m-%d")
                                        except:
                                            pub_date = eng_match.group(1)

                        # 마지막 수단: 못 찾으면 오늘 날짜가 아닌 "확인필요"로 표시 (구분하기 위함)
                        final_data.append({
                            "출처": site_name,
                            "수집일": today_str,
                            "발행일": pub_date,
                            "제목": title_clean,
                            "링크": full_link
                        })
                        added += 1
                        if added >= 8: break
                    
                    print(f"✅ {site_name}: {added}개 확보 (날짜 매칭 완료)")
            except Exception as e:
                print(f"❌ {site_name} 오류: {e}")

    # CSV 저장
    file_name = 'ai_trend_report.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["출처", "수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_data)
    
    print(f"🎉 리포트 생성 완료!")

if __name__ == "__main__":
    asyncio.run(main())
