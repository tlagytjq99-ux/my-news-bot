import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime
import time

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    keyword = "AI"
    # 최신순 정렬
    url = f"https://search.naver.com/search.naver?where=news&query={keyword}&sm=tab_opt&sort=1"
    driver.get(url)
    time.sleep(5) 

    news_data = []
    # 제외하고 싶은 문구들
    exclude_keywords = ['언론사 선정', '구독하세요', '심층기획', '네이버 메인에서']

    # 낚싯대: 뉴스 기사 제목의 공통 클래스인 'news_tit'을 먼저 찾고, 없으면 'a' 태그 전체 탐색
    items = driver.find_elements(By.CLASS_NAME, "news_tit")
    
    if not items:
        items = driver.find_elements(By.CSS_SELECTOR, "a")

    for item in items:
        title = item.text.strip()
        href = item.get_attribute('href')
        
        # 1. 제목이 너무 짧지 않고
        # 2. 링크가 있고
        # 3. 제외 키워드가 제목에 들어있지 않으며
        # 4. 홍보용 링크(channelPromotion)가 아닌 경우만 수집
        if len(title) > 15 and href and "channelPromotion" not in href:
            if not any(key in title for key in exclude_keywords):
                if not any(d['기사제목'] == title for d in news_data):
                    news_data.append({
                        "수집일": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "기사제목": title,
                        "링크": href
                    })
        
        if len(news_data) >= 10:
            break

    if news_data:
        df = pd.DataFrame(news_data)
        file_name = "news_list.xlsx"
        df.to_excel(file_name, index=False)
        print(f"✅ 진짜 뉴스 {len(news_data)}개 수집 성공!")
    else:
        print("❌ 유효한 뉴스 기사를 찾지 못했습니다.")

except Exception as e:
    print(f"오류 발생: {e}")
finally:
    driver.quit()
