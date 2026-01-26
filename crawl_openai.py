import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime

async def get_openai_news():
    print("🌐 OpenAI 뉴스 수집을 시작합니다...")
    news_list = []
    
    async with async_playwright() as p:
        # 1. 브라우저 실행 (서버 환경을 위해 headless=True)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            # 2. OpenAI 뉴스 페이지 접속
            await page.goto("https://openai.com/news/", wait_until="networkidle")
            
            # 3. 뉴스 아이템 추출 (현재 OpenAI 사이트 구조 반영)
            # 리스트 아이템(li) 중 뉴스 기사들을 찾습니다.
            items = await page.query_selector_all('li.relative')
            
            for item in items[:5]:  # 최신 5개만
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
            print(f"❌ 오류 발생: {e}")
        finally:
            await browser.close()
            
    return news_list

if __name__ == "__main__":
    # 비동기 함수 실행
    results = asyncio.run(get_openai_news())
    
    if results:
        # 데이터프레임 생성 및 저장
        df = pd.DataFrame(results)
        df.insert(0, "수집일", datetime.now().strftime("%Y-%m-%d"))
        
        # 별도의 파일명으로 저장 (openai_news.xlsx)
        df.to_excel("openai_news.xlsx", index=False)
        print(f"✅ OpenAI 수집 완료! (openai_news.xlsx 저장됨)")
        print(df[['기사제목', '발행일']])
    else:
        print("❌ 수집된 데이터가 없습니다.")
