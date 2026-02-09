from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time

def fetch_eu_with_selenium():
    # 1. 크롬 옵션 설정 (창 없는 모드)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    url = "https://op.europa.eu/en/search-results?p_p_id=eu_europa_publications_portlet_facet_search_result_FacetedSearchResultPortlet_INSTANCE_TTTP7nyqSt8X&p_p_lifecycle=0&facet.documentYear=2025&facet.collection=EUPub"

    print(f"🌐 가상 브라우저 실행 중: {url}", flush=True)
    
    collected_data = []

    try:
        driver.get(url)
        
        # 2. 데이터가 나타날 때까지 최대 20초 대기 (핵심!)
        # 검색 결과 아이템이 나타날 때까지 기다립니다.
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "search-result-item")))
        
        # 사람처럼 보이게 3초 더 대기
        time.sleep(3)

        # 3. 데이터 추출
        items = driver.find_elements(By.CLASS_NAME, "search-result-item")
        print(f"🔎 화면 렌더링 완료! {len(items)}개의 아이템 발견.", flush=True)

        for item in items:
            try:
                title_el = item.find_element(By.TAG_NAME, "h4").find_element(By.TAG_NAME, "a")
                title = title_el.text
                link = title_el.get_attribute("href")
                
                # 메타데이터 추출 (날짜 등)
                try:
                    date = item.find_element(By.CLASS_NAME, "metadata-value").text
                except:
                    date = "2025"

                collected_data.append({"date": date, "title": title, "link": link})
            except:
                continue

    except Exception as e:
        print(f"❌ 셀레늄 실행 중 오류: {e}", flush=True)
    finally:
        driver.quit()

    # 4. 저장
    file_name = 'EU_Policy_2025_Full.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
        writer.writeheader()
        if collected_data:
            writer.writerows(collected_data)
            print(f"✅ 최종 {len(collected_data)}건 저장 완료!", flush=True)
        else:
            writer.writerow({"date": "N/A", "title": "Failed to render data", "link": "N/A"})

if __name__ == "__main__":
    fetch_eu_with_selenium()
