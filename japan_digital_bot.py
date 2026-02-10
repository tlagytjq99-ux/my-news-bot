import requests
from bs4 import BeautifulSoup
import csv
import time

def crawl_digital_2025_fixed_range():
    # 대표님이 확인해주신 2025년 구간
    start_page = 21
    end_page = 188
    
    file_name = 'Japan_Digital_2025_Full_Archive.csv'
    base_url = "https://www.digital.go.jp/news?page="
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    
    all_data = []

    print(f"🚀 [정밀 타격] Page {start_page}부터 {end_page}까지 2025년 데이터를 수집합니다...")

    for page in range(start_page, end_page + 1):
        url = f"{base_url}{page}"
        print(f"📡 스캔 중: {page}/{end_page} 페이지...", end='\r')
        
        try:
            res = requests.get(url, headers=headers, timeout=20)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 디지털청의 뉴스 리스트 아이템 (ecl-card 클래스 기반)
            articles = soup.select('div.ecl-card') or soup.select('article')
            
            # 만약 선택자가 안 잡힐 경우를 대비한 <a> 태그 직접 추적
            if not articles:
                # 링크와 날짜를 포함하는 가장 가까운 부모 요소를 찾음
                articles = soup.find_all('li') 

            for item in articles:
                link_tag = item.find('a')
                date_tag = item.find('time')
                
                if link_tag and date_tag:
                    title = link_tag.get_text(strip=True)
                    date = date_tag.get('datetime') or date_tag.get_text(strip=True)
                    href = link_tag['href']
                    
                    # 2025년 데이터인지 한 번 더 검증 (안전장치)
                    if "2025" in date or "2025" in title:
                        all_data.append({
                            "date": date[:10],
                            "title": title,
                            "link": "https://www.digital.go.jp" + href if href.startswith('/') else href
                        })

            # 서버 부하를 고려해 0.3초씩 휴식
            if page % 10 == 0:
                time.sleep(1)
                print(f"\n✨ {page}페이지까지 누적 {len(all_data)}건 확보...")

        except Exception as e:
            print(f"\n❌ {page}페이지 오류 발생: {e}")
            continue

    # 데이터 저장 (중복 제거 포함)
    if all_data:
        unique_data = list({v['link']: v for v in all_data}.values())
        # 날짜순 정렬
        unique_data.sort(key=lambda x: x['date'], reverse=True)
        
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(unique_data)
        print(f"\n\n✅ 수집 완료! 총 {len(unique_data)}건의 2025년 정책 자료를 저장했습니다.")
        print(f"📂 파일명: {file_name}")
    else:
        print("\n⚠️ 데이터를 찾지 못했습니다. 선택자(Selector)를 다시 점검해야 합니다.")

if __name__ == "__main__":
    crawl_digital_2025_fixed_range()
