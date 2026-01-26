import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime
import time

# 1. 브라우저 설정 (차단 방지 최적화)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# 가짜 신분증(User-Agent) 강화
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    # 2. 접속 시도 (AI 키워드 최신순)
    keyword = "AI"
    url = f"https://search.naver.com/search.naver?where=news&query={keyword}&sm=tab_opt&sort=1"
    driver.get(url)
    
    # 페이지 로딩을 기다리며 넉넉히 대기
    time.sleep(7) 

    news_data = []
    
    # 3. 뉴스 아이템 탐색 (더 유연한 방식)
    # 네이버 뉴스의 각 칸을 의미하는 여러 가지 클래스명을 다 시도합니다.
    items = driver.find_elements(By.CSS_SELECTOR, "li.bx, .news_wrap, .news_area")

    for item in items:
        try:
            # 제목과 링크 찾기
            title_el = item.find_element(By.CSS_SELECTOR, "a.news_tit")
            title = title_el.text.strip()
            link = title_el.get_attribute('href')
            
            # 날짜(발행일) 찾기 - 여러 위치를 다 뒤집니다.
            try:
                # info_group 안의 info 클래스 중 날짜 형태인 것을 찾음
                info_els = item.find_elements(By.CSS_SELECTOR, ".info_group .info")
                # 보통 두 번째 info가 날짜인 경우가 많음
                date_text = info_els[-1].text.strip() if info_els else "날짜미상"
            except:
                date_text = "날짜미상"

            # 데이터 저장 (제목이 있고 광고가 아닌 경우)
            if title and "static/channelPromotion" not in link:
                if not any(d['기사제목'] == title for d in news_data):
                    news_data.append({
                        "수집일": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "발행일": date_text,
                        "기사제목": title,
                        "링크": link
                    })
        except:
            continue
            
        if len(news_data) >= 10:
            break

    # 4. 결과 저장 및 로그 출력
    if news_data:
        df = pd.DataFrame(news_data)
        df.to_excel("news_list.xlsx", index=False)
        print(f"✅ 성공! {len(news_data)}개의 뉴스를 엑셀로 저장했습니다.")
    else:
        # 실패 시 로봇이 본 화면 제목 출력 (디버깅용)
        print(f"❌ 실패: 페이지 내용을 읽지 못했습니다. (접속된 페이지 제목: {driver.title})")

except Exception as e:
    print(f"⚠️ 에러 발생: {e}")
finally:
    driver.quit()
