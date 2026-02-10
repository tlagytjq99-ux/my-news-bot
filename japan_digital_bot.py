import requests
from bs4 import BeautifulSoup
import csv
import time

def crawl_digital_2025_ultimate_archive():
    start_page = 21
    end_page = 188
    file_name = 'Japan_Digital_2025_Full_Archive.csv'
    base_url = "https://www.digital.go.jp/news?page="
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    
    all_data = []

    print(f"🚀 [전수 조사] Page {start_page} ~ {end_page}의 모든 2025년 데이터를 추출합니다...")

    for page in range(start_page, end_page + 1):
        url = f"{base_url}{page}"
        print(f"📡 {page}/{end_page} 페이지 정밀 스캔 중... (현재 {len(all_data)}건 확보)", end='\r')
        
        try:
            res = requests.get(url, headers=headers, timeout=20)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 특정 클래스에 얽매이지 않고, 날짜(time 태그)가 포함된 모든 구역을 타겟팅합니다.
            # 1. 모든 time 태그를 찾아서 그 부모 요소들로부터 정보를 추출
            time_tags = soup.find_all('time')
            
            for time_tag in time_tags:
                date_text = time_tag.get_text(strip=True)
                
                # 2025년 데이터인지 검증
                if "2025" in date_text:
                    # 해당 날짜 근처에 있는 가장 가까운 링크(a 태그)를 찾습니다.
                    # 부모 요소를 타고 올라가며 링크를 탐색합니다.
                    parent = time_tag.parent
                    link_tag = None
                    
                    # 최대 5단계 부모까지 올라가며 링크 탐색
                    for _ in range(5):
                        if parent:
                            link_tag = parent.find('a', href=True)
                            if link_tag: break
                            parent = parent.parent
                    
                    if link_tag:
                        title = link_tag.get_text(strip=True)
                        href = link_tag['href']
                        
                        # 메뉴 링크나 너무 짧은 제목 제외
                        if len(title) < 10 or href.startswith('#'): continue
                        
                        full_url = "https://www.digital.go.jp" + href if href.startswith('/') else href
                        all_data.append({
                            "date": date_text[:10],
                            "title": title,
                            "link": full_url
                        })

            if page % 20 == 0:
                time.sleep(1) # 과부하 방지

        except Exception as e:
            print(f"\n❌ {page}페이지 스캔 중 오류: {e}")
            continue

    # 데이터 정제 및 저장
    if all_data:
        # 링크 중복 제거
        unique_data = list({v['link']: v for v in all_data}.values())
        # 날짜순 정렬
        unique_data.sort(key=lambda x: x['date'], reverse=True)
        
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(unique_data)
        print(f"\n\n✅ 수집 완료! {len(unique_data)}건의 데이터를 확보했습니다.")
    else:
        print("\n⚠️ 데이터를 수집하지 못했습니다.")

if __name__ == "__main__":
    crawl_digital_2025_ultimate_archive()
