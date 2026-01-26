import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime
import time

# 1. 브라우저 설정 (GitHub Actions 환경 대응)
chrome_options = Options()
chrome_options.add_argument("--headless") # 화면 없이 실행 (필수)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    keyword = "AI"
    url = f"https://search.naver.com/search.naver?where=news&query={keyword}&sort=1"
    driver.get(url)
    time.sleep(3) # 로딩 대기

    # 2. 뉴스 데이터 정확하게 타겟팅
    # 네이버 뉴스 제목은 보통 'news_tit'이라는 클래스 이름을 가집니다.
    news_elements = driver.find_elements(By.CLASS_NAME, "news_tit")
    
    news_data = []
    exclude_keywords = ['언론사 선정', '네이버 메인에서', '구독하세요', '심층기획']

    for item in news_elements:
        title = item.text.strip()
        href = item.get_attribute('href')
        
        # 필터링 로직
        if any(key in title for key in exclude_keywords):
            continue
            
        if title and href:
            news_data.append({
                "수집일": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "기사제목": title,
                "링크": href
            })
        
        if len(news_data) >= 10:
            break

    # 3. 엑셀 저장 (파일명은 고정하는 것이 GitHub Actions 관리상 편합니다)
    if news_data:
        df = pd.DataFrame(news_data)
        file_name = "news_list.xlsx" # 파일명을 고정해야 GitHub에 업데이트하기 쉽습니다.
        df.to_excel(file_name, index=False)
        print(f"✅ {len(news_data)}개 뉴스 저장 완료!")
    else:
        print("❌ 수집된 데이터가 없습니다.")

except Exception as e:
    print(f"오류 발생: {e}")
finally:
    driver.quit()
