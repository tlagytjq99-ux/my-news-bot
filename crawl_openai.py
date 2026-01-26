import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime

async def get_openai_news():
    print("🌐 OpenAI 뉴스 수집 시작...")
    news_list = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 실제 브라우저처럼 보이게 하기 위한 설정 추가
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            # 타임아웃을 60초로 늘리고 로딩 완료를 기다림
            await page.goto("https://openai.com/news/", wait_until="networkidle", timeout=60000)
            # 페이지가 뜬 후 추가로 3초 더 대기 (안전장치)
            await asyncio.sleep(3)
            
            items = await page.query_selector_all('li.relative')
            print(f"🔎 발견된 아이템 개수: {len(items)}개")
            
            for item in items[:5]:
                title_el = await item.query_selector('h3')
                date_el = await item.query_selector('time')
                link_el = await item.query_selector('a')
                
                if title_el and date_el:
                    title = await title_el.inner_text()
                    date = await date_el.inner_text()
                    href = await link_el.get_attribute('href')
                    link = f"https://openai.com{href}" if href.startswith('/') else href
                    
                    news_list.append({
                        "카테고리": "글로벌(OpenAI)",
                        "기사제목": title.strip(),
                        "발행일": date.strip(),
                        "링크": link
                    })
        except Exception as e:
            print(f"❌ 수집 중 오류 발생: {e}")
        finally:
            await browser.close()
    return news_list

if __name__ == "__main__":
    results = asyncio.run(get_openai_news())
    
    # 데이터가 없어도 에러 방지를 위해 빈 데이터프레임이라도 생성
    if not results:
        print("⚠️ 수집된 데이터가 없어 빈 파일을 생성합니다.")
        df = pd.DataFrame(columns=["수집일", "카테고리", "기사제목", "발행일", "링크"])
    else:
        df = pd.DataFrame(results)
        df.insert(0, "수집일", datetime.now().strftime("%Y-%m-%d"))
        print(f"✅ {len(results)}건 수집 완료!")

    # 무조건 파일 생성 (Git 에러 방지)
    df.to_excel("openai_news.xlsx", index=False)
