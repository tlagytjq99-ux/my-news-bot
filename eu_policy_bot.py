from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time

def fetch_eu_final_boss():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # [핵심] 창 크기를 크게 해야 요소가 숨겨지지 않습니다.
    chrome_options.add_argument("--window-size=1920,1080")
    # [핵심] 실제 사람 브라우저처럼 보이게 헤더 강화
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # 2025년 결과 페이지로 직접 연결
    url = "https://op.europa.eu/en/search-results?p_p_id=eu_europa_publications_portlet_facet_search_result_FacetedSearchResultPortlet_INSTANCE_TTTP7nyqSt8X&p_p_lifecycle=0&facet.documentYear=2025&facet.collection=EUPub"

    print(f"🕵️ '최종 보스' 공략 시작: {url}", flush=True)
    collected_data = []

    try:
        driver.get(url)
        
        # 1. 인내심 대폭 연장 (30초)
        wait = WebDriverWait(driver, 30)
        
        # 2. 특정 클래스가 아니라 '결과 리스트 전체'가 뜰 때까지 기다림
        print("⏳ 데이터 렌더링 대기 중...", flush=True)
        time.sleep(10) # 자바스크립트 실행을 위한 절대적인 시간 부여
        
        # 3. 데이터 추출 (더 유연한 셀렉터 사용)
        # 아이템을 감싸는 컨테이너 자체를 찾습니다.
        items = driver.find_elements(By.CSS_SELECTOR, "div.search-result-item, div.results-row")
        
        if not items:
            # 만약 못 찾았다면 페이지 소스를 출력해 봅니다 (디버깅)
            print("⚠️ 아이템을 못 찾았습니다. 현재 페이지의 텍스트 일부: ", driver.page_source[:500], flush=True)

        for item in items:
            try:
                # 제목 추출
                title_el = item.find_element(By.TAG_NAME, "h4")
                title = title_el.text.strip()
                link = title_el.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                try:
                    date = item.find_element(By.CLASS_NAME, "metadata-value").text.strip()
                except:
                    date = "2025"

                if title:
                    collected_data.append({"date": date, "title": title, "link": link})
            except Exception as e:
                continue

    except Exception as e:
        print(f"❌ 런타임 오류: {str(e)[:100]}", flush=True)
    finally:
        driver.quit()

    # 결과 저장
    file_name = 'EU_Policy_2025_Full.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
        writer.writeheader()
        if collected_data:
            writer.writerows(collected_data)
            print(f"🎯 드디어 성공! {len(collected_data)}건의 데이터를 파일에 담았습니다.", flush=True)
        else:
            print("😭 여전히 데이터가 0건입니다. 하지만 파일은 생성했습니다.", flush=True)

if __name__ == "__main__":
    fetch_eu_final_boss()
