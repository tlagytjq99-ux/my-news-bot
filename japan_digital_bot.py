import requests
from bs4 import BeautifulSoup
import csv
import time

def crawl_digital_2025_bulk_scan():
    start_page = 21
    end_page = 188
    file_name = 'Japan_Digital_2025_Full_Archive.csv'
    base_url = "https://www.digital.go.jp/news?page="
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8'
    }
    
    all_data = []
    seen_links = set()

    print(f"🚀 [벌크 스캔] Page {start_page} ~ {end_page} 구간의 모든 기사 블록을 분석합니다.")

    for page in range(start_page, end_page + 1):
        url = f"{base_url}{page}"
        print(f"📡 {page}/{end_page} 페이지 정밀 분해 중... (현재 {len(all_data)}건)", end='\r')
        
        try:
            res = requests.get(url, headers=headers, timeout=20)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 디지털청 뉴스 리스트의 각 항목을 감싸는 모든 가능성 있는 태그들
            # 카드 형태(ecl-card), 리스트 형태(li), 일반 블록(div)을 모두 잡습니다.
            items = soup.select('.ecl-card, .ecl-list-item, article, li')
            
            for item in items:
                link_tag = item.find('a', href=True)
                if not link_tag:
                    continue
                
                href = link_tag['href']
                # 보도자료, 뉴스, 정책 등 핵심 콘텐츠 주소 확인
                if not any(path in href for path in ['/news/', '/press/', '/policies/', '/announcement/']):
                    continue
                
                full_url = "https://www.digital.go.jp" + href if href.startswith('/') else href
                
                if full_url not in seen_links:
                    # 블록 전체의 텍스트를 가져와서 제목으로 사용 (날짜 포함됨)
                    # separator를 주어 텍스트가 뭉치지 않게 합니다.
                    title_content = item.get_text(separator=" ", strip=True)
                    
                    # 메뉴 항목이나 너무 짧은 텍스트 필터링
                    if len(title_content) < 15:
                        continue
                        
                    seen_links.add(full_url)
                    all_data.append({
                        "title": title_content,
                        "link": full_url
                    })

            if page % 30 == 0:
                time.sleep(1)

        except Exception as e:
            continue

    # 데이터 저장
    if all_data:
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["title", "link"])
            writer.writeheader()
            writer.writerows(all_data)
        print(f"\n\n✅ 수집 완료! 총 {len(all_data)}건의 데이터를 확보했습니다.")
    else:
        print("\n⚠️ 데이터를 찾지 못했습니다.")

if __name__ == "__main__":
    crawl_digital_2025_bulk_scan()
