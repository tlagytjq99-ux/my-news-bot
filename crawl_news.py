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
    url = f"https://search.naver.com/search.naver?where=news&query={keyword}&sm=tab_opt&sort=1"
    driver.get(url)
    time.sleep(5) 

    news_data = []
    # 뉴스 기사 덩어리들을 찾습니다.
    items = driver.find_elements(By.CSS_SELECTOR, ".news_wrap")

    for item in items:
        try:
            # 1. 제목과 링크
            title_element = item.find_element(By.CSS_SELECTOR, ".news_tit")
            title = title_element.text.strip()
            href = title_element.get_attribute('href')
            
            # 2. 발행일 (여러 패턴 대응)
            # 네이버 뉴스 구조에 따라 .info 혹은 .sub_txt 등 다양한 이름을 사용합니다.
            try:
                # 첫 번째 시도: 일반적인 위치
                publish_date = item.find_element(By.CSS_SELECTOR, ".info_group .info").text
            except:
                try:
                    # 두 번째 시도: 다른 위치
                    publish_date = item.find_element(By.CSS_SELECTOR, ".sub_txt").text
                except:
                    publish_date = "날짜 정보 없음"

            # 광고 및 중복 필터링
            if "channelPromotion" in href or len(title) < 5:
                continue

            if not any(d['기사제목'] == title for d in news_data):
                news_data.append({
                    "수집일": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "발행일": publish_date.replace("선정", "").strip(), # '언론사 선정' 문구 제거
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
        print(f"✅ 총 {len(news_data)}개의 기사를 성공적으로 저장했습니다.")
    else:
        print("❌ 뉴스 구역(.news_wrap)을 찾는 데 실패했습니다. 페이지 구조를 다시 확인하세요.")

except Exception as e:
    print(f"오류 발생: {e}")
finally:
    driver.quit()
