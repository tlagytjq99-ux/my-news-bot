import requests
from bs4 import BeautifulSoup
import csv
import time

def crawl_digital_2025_fixed_range_all():
    # 대표님이 확정해주신 2025년 구간
    start_page = 21
    end_page = 188
    
    file_name = 'Japan_Digital_2025_Full_Archive.csv'
    base_url = "https://www.digital.go.jp/news?page="
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    
    all_data = []
    seen_links = set() # 중복 방지

    print(f"🚀 [전량 수집] Page {start_page} ~ {end_page} 구간의 모든 기사를 수집합니다.")

    for page in range(start_page, end_page + 1):
        url = f"{base_url}{page}"
        print(f"📡 {page}/{end_page} 페이지 수집 중... (현재 누적 {len(all_data)}건)", end='\r')
        
        try:
            res = requests.get(url, headers=headers, timeout=20)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 1. 뉴스 카드 섹션 탐색 (가장 정확한 데이터 영역)
            # 카드 구조가 아니더라도 모든 뉴스 링크(/news/...)를 추적합니다.
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                
                # 유효한 뉴스/공지 링크 패턴만 필터링
                if '/news/' in href or '/press/' in href or '/policies/' in href:
                    full_url = "https://www.digital.go.jp" + href if href.startswith('/') else href
                    
                    if full_url not in seen_links:
                        # 제목과 날짜를 포함한 텍스트 추출
                        title_text = link.get_text(separator=" ", strip=True)
                        
                        # 너무 짧은 링크(메뉴 등)는 제외
                        if len(title_text) < 10:
                            continue
                            
                        seen_links.add(full_url)
                        all_data.append({
                            "content": title_text,
                            "url": full_url
                        })

            # 20페이지마다 짧은 휴식 (차단 방지)
            if page % 20 == 0:
                time.sleep(0.5)

        except Exception as e:
            print(f"\n❌ {page}페이지 수집 중 건너뜀: {e}")
            continue

    # 데이터 저장
    if all_data:
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["content", "url"])
            writer.writeheader()
            writer.writerows(all_data)
        print(f"\n\n✅ 수집 완료! 총 {len(all_data)}건의 2025년 구간 데이터를 확보했습니다.")
        print(f"📂 파일명: {file_name}")
    else:
        print("\n⚠️ 데이터를 찾지 못했습니다. 구간 설정을 다시 확인해주세요.")

if __name__ == "__main__":
    crawl_digital_2025_fixed_range_all()
