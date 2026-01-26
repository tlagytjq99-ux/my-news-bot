import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime
import time

# 1. 브라우저 설정 (더 강력한 차단 우회 설정)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    # 2. 네이버 뉴스 검색 (AI 키워드, 최신순)
    keyword = "AI"
    url = f"https://search.naver.com/search.naver?where=news&query={keyword}&sort=1"
    driver.get(url)
    time.sleep(5) # 페이지가 다 뜰 때까지 충분히 기다림

    # 3. 데이터 추출 (여러 가지 경로로 시도)
    news_data = []
    
    # 방법 1: 클래스 이름으로 찾기
    items = driver.find_elements(By.CSS_SELECTOR, ".news_tit")
    
    # 만약 방법 1로 못 찾으면 방법 2 시도 (더 넓은 범위)
    if not items:
        items = driver.find_elements(By.CSS_SELECTOR, "a.news_tit")

    for item in items:
        title = item.text.strip()
        href = item.get_attribute('href')
        
        if title and href:
            news_data.append({
                "수집일": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "기사제목": title,
                "링크": href
            })
        
        if len(news_data) >= 10:
            break

    # 4. 엑셀 저장
    if news_data:
        df = pd.DataFrame(news_data)
        # 파일명을 고정해서 업데이트가 잘 보이게 합니다.
        file_name = "news_list.xlsx"
        df.to_excel(file_name, index=False)
        print(f"✅ {len(news_data)}개 뉴스 수집 성공!")
    else:
        # 실패 시 화면에 어떤 내용이 떠 있는지 출력 (디버깅용)
        print("❌ 수집된 데이터가 없습니다. 현재 페이지 제목:", driver.title)

except Exception as e:
    print(f"오류 발생: {e}")
finally:
    driver.quit()
