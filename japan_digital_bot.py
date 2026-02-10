import requests
from bs4 import BeautifulSoup
import csv
import time

def crawl_digital_2025_ultimate_wall_breaker():
    start_page = 21
    end_page = 188
    file_name = 'Japan_Digital_2025_Full_Archive.csv'
    base_url = "https://www.digital.go.jp/news?page="
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        'Referer': 'https://www.digital.go.jp/news'
    }
    
    all_data = []
    seen_links = set()

    print(f"🚀 [벽 깨기 모드] {start_page} ~ {end_page} 페이지의 모든 '생존 링크'를 수집합니다.")

    for page in range(start_page, end_page + 1):
        url = f"{base_url}{page}"
        print(f"📡 {page}/{end_page} 페이지 텍스트 분해 중... (현재 {len(all_data)}건)", end='\r')
        
        try:
            # 세션을 사용하여 쿠키와 연결 유지 (차단 방지)
            with requests.Session() as session:
                res = session.get(url, headers=headers, timeout=30)
                res.encoding = 'utf-8'
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # [핵심 변경] 특정 클래스를 찾지 않고 페이지의 모든 <a> 태그를 타겟팅
                all_links = soup.find_all('a', href=True)
                
                for a in all_links:
                    href = a['href']
                    
                    # 뉴스나 보도자료 주소가 포함된 모든 링크를 수집
                    # 'news', 'press', 'policies', 'announcement', 'topics' 등 모든 경로 허용
                    if any(path in href for path in ['/news/', '/press/', '/policies/', '/topics/', '/announcement/']):
                        full_url = "https://www.digital.go.jp" + href if href.startswith('/') else href
                        
                        if full_url not in seen_links:
                            # <a> 태그 내부의 모든 텍스트를 공백 포함해서 추출
                            title = a.get_text(" ", strip=True)
                            
                            # 메뉴나 푸터에 있는 짧은 링크 필터링 (최소 12자 이상)
                            if len(title) < 12:
                                continue
                                
                            seen_links.add(full_url)
                            all_data.append({
                                "title": title,
                                "link": full_url
                            })

            # 페이지마다 0.2초만 쉬어서 속도 확보
            time.sleep(0.2)

        except Exception as e:
            continue

    # 데이터 저장
    if all_data:
        # 날짜순 정렬 시도 (텍스트 안에 날짜가 있을 경우를 위해)
        all_data.sort(key=lambda x: x['title'], reverse=True)
        
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["title", "link"])
            writer.writeheader()
            writer.writerows(all_data)
        print(f"\n\n✅ [성공] 총 {len(all_data)}건의 데이터를 수집했습니다!")
    else:
        print("\n⚠️ 수집된 데이터가 없습니다.")

if __name__ == "__main__":
    crawl_digital_2025_ultimate_wall_breaker()
