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
    # 뉴스 아이템들이 담긴 구역들을 찾습니다.
    items = driver.find_elements(By.CSS_SELECTOR, ".news_wrap.api_ani_send")

    for item in items:
        try:
            # 제목과 링크 추출
            title_element = item.find_element(By.CSS_SELECTOR, ".news_tit")
            title = title_element.text.strip()
            href = title_element.get_attribute('href')
            
            # 발행일 추출 (보통 info_group 클래스 내의 info 클래스에 적혀 있음)
            # '30분 전', '2026.01.26.' 등의 텍스트를 가져옵니다.
            date_element = item.find_element(By.CSS_SELECTOR, ".info_group .info")
            publish_date = date_element.text.strip()

            # 광고성 문구 필터링
            if "channelPromotion" in href or len(title) < 10:
                continue

            if not any(d['기사제목'] == title for d in news_data):
                news_data.append({
                    "수집일": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "발행일": publish_date,
                    "기사제목": title,
                    "링크": href
                })
        except:
            continue
        
        if len(news_data) >= 10:
            break

    if news_data:
        df = pd.DataFrame(news_data)
        file_name = "news_list.xlsx"
        df.to_excel(file_name, index=False)
        print(f"✅ 발행일 포함 {len(news_data)}개 뉴스 수집 성공!")
    else:
        print("❌ 데이터를 찾지 못했습니다.")

except Exception as e:
    print(f"오류 발생: {e}")
finally:
    driver.quit()
