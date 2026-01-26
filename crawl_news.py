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
    # 최신순 정렬 주소
    url = f"https://search.naver.com/search.naver?where=news&query={keyword}&sm=tab_opt&sort=1"
    driver.get(url)
    time.sleep(5) 

    news_data = []
    
    # [수정 포인트] 특정 클래스 대신 '뉴스 리스트' 구역 전체에서 링크를 찾습니다.
    # 보통 뉴스 제목은 nso_SRE 혹은 news_tit 클래스를 포함한 a 태그입니다.
    # 하지만 더 확실하게 하기 위해 '뉴스 영역' 전체를 타겟팅합니다.
    links = driver.find_elements(By.CSS_SELECTOR, "a")

    for link in links:
        title = link.text.strip()
        href = link.get_attribute('href')
        
        # 기사 제목의 특징: 글자 수가 어느 정도 있고, 링크가 길며, 특정 키워드를 피함
        if len(title) > 15 and href and "news.naver.com" in href:
            # 중복 제거
            if not any(d['기사제목'] == title for d in news_data):
                news_data.append({
                    "수집일": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "기사제목": title,
                    "링크": href
                })
        
        if len(news_data) >= 10:
            break

    # 만약 위 방법으로도 못 찾았다면 (비상용)
    if not news_data:
        items = driver.find_elements(By.CLASS_NAME, "news_tit")
        for item in items:
            news_data.append({
                "수집일": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "기사제목": item.text.strip(),
                "링크": item.get_attribute('href')
            })

    if news_data:
        df = pd.DataFrame(news_data)
        file_name = "news_list.xlsx"
        df.to_excel(file_name, index=False)
        print(f"✅ {len(news_data)}개 뉴스 수집 성공!")
    else:
        print("❌ 여전히 데이터를 찾지 못했습니다. 구조 확인이 필요합니다.")

except Exception as e:
    print(f"오류 발생: {e}")
finally:
    driver.quit()
