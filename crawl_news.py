import os
import pandas as pd
from datetime import datetime
import requests
from playwright.sync_api import sync_playwright

client_id = os.environ.get('NAVER_CLIENT_ID')
client_secret = os.environ.get('NAVER_CLIENT_SECRET')

# (네이버 수집 함수는 이전과 동일하므로 생략하거나 그대로 두셔도 됩니다)
def get_naver_news():
    news_list = []
    url = "https://openapi.naver.com/v1/search/news.json?query=AI&display=100&sort=sim"
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            items = res.json().get('items', [])
            for item in items[:8]: # 예시로 8개
                news_list.append({"카테고리": "네이버", "기사제목": item['title'].replace("<b>","").replace("</b>",""), "발행일": item['pubDate'][:16], "링크": item['link']})
    except: pass
    return news_list

def get_msit_with_playwright():
    msit_list = []
    url = "https://www.msit.go.kr/bbs/list.do?sCode=user&mId=307&mPid=208&pageIndex=1&bbsSeqNo=94&nttSeqNo=&searchOpt=ALL&searchTxt=ai"
    
    with sync_playwright() as p:
        # 브라우저 실행
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        try:
            # 페이지 접속 및 대기
            page.goto(url, wait_until="networkidle")
            page.wait_for_selector(".lst_b", timeout=10000) # 리스트가 나타날 때까지 대기
            
            # 제목과 링크 추출
            items = page.query_selector_all(".lst_b li")
            for item in items[:5]:
                title_el = item.query_selector("p.tit")
                link_el = item.query_selector("a")
                
                if title_el and link_el:
                    title = title_el.inner_text().strip()
                    href = link_el.get_attribute("href")
                    full_link = "https://www.msit.go.kr" + href
                    
                    msit_list.append({
                        "카테고리": "정부(과기부)",
                        "기사제목": title,
                        "발행일": "최근",
                        "링크": full_link
                    })
        except Exception as e:
            print(f"Playwright 수집 오류: {e}")
        finally:
            browser.close()
    return msit_list

if __name__ == "__main__":
    naver = get_naver_news()
    msit = get_msit_with_playwright()
    df = pd.DataFrame(naver + msit)
    df.to_excel("news_list.xlsx", index=False)
    print(f"✅ 완료! 과기부: {len(msit)}건")
