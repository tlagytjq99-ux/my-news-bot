import requests
from bs4 import BeautifulSoup
import csv
import time

def crawl_digital_agency_2025_all():
    base_url = "https://www.digital.go.jp/news?page="
    file_name = 'Japan_Digital_All_2025.csv'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    
    all_2025_data = []
    page = 0
    keep_scanning = True

    print("🚀 [2025 전수 조사] 디지털청 아카이브 정밀 스캔을 시작합니다...")

    while keep_scanning:
        url = f"{base_url}{page}"
        print(f"📄 현재 {page}페이지 스캔 중... ({url})")
        
        try:
            res = requests.get(url, headers=headers, timeout=20)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 기사 리스트 아이템 추출 (ecl-card 클래스 혹은 article 태그)
            articles = soup.find_all(['article', 'div'], class_=lambda x: x and 'card' in x) or soup.find_all('li')
            
            if not articles:
                print("🏁 더 이상 데이터가 없습니다.")
                break

            page_found_2025 = False
            for item in articles:
                link_tag = item.find('a')
                date_tag = item.find('time')
                
                if link_tag and date_tag:
                    title = link_tag.get_text(strip=True)
                    date_text = date_tag.get_text(strip=True)
                    href = link_tag['href']
                    
                    # 2025년 데이터인지 확인 (연도 혹은 연호 令和7年)
                    if "2025" in date_text or "令和7" in date_text:
                        all_2025_data.append({
                            "date": date_text,
                            "title": title,
                            "link": "https://www.digital.go.jp" + href if href.startswith('/') else href
                        })
                        page_found_2025 = True
                        page_has_2025_data = True
                    
                    # 2024년 데이터가 나오기 시작하면 중단
                    elif "2024" in date_text or "令和6" in date_text:
                        print("🛑 2024년 데이터 구간에 진입했습니다. 스캔을 종료합니다.")
                        keep_scanning = False
                        break
            
            # 현재 페이지에 2025년 데이터가 하나도 없고, 이미 2026년 구간을 지났다면 종료 안전장치
            if not page_found_2025 and page > 50: # 안전을 위해 50페이지까지는 탐색
                keep_scanning = False

            page += 1
            time.sleep(1) # 서버 부하 방지 매너 타임

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            break

    # 데이터 저장
    if all_2025_data:
        # 중복 제거
        unique_data = list({v['link']: v for v in all_2025_data}.values())
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(unique_data)
        print(f"✅ 수집 완료! 총 {len(unique_data)}건의 2025년 자료를 저장했습니다.")
    else:
        print("⚠️ 2025년 데이터를 찾지 못했습니다.")

if __name__ == "__main__":
    crawl_digital_agency_2025_all()
