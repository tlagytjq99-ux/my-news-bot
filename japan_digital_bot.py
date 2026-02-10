import requests
from bs4 import BeautifulSoup
import csv
import time

def crawl_digital_2025_no_limit():
    start_page = 21
    end_page = 188
    file_name = 'Japan_Digital_2025_Full_Archive.csv'
    base_url = "https://www.digital.go.jp/news?page="
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    
    unique_links = set() # 중복 체크용
    all_data = []

    print(f"🚀 [한계 돌파] {start_page} ~ {end_page} 페이지의 모든 데이터를 샅샅이 뒤집니다.")

    for page in range(start_page, end_page + 1):
        url = f"{base_url}{page}"
        print(f"📡 {page}/{end_page} 페이지 분석 중... (현재 누적 {len(all_data)}건)", end='\r')
        
        try:
            res = requests.get(url, headers=headers, timeout=20)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 디지털청 뉴스 리스트의 핵심은 <a> 태그 안에 <span>이나 <time>이 섞여 있는 구조입니다.
            # 모든 <a> 태그를 전수 조사합니다.
            for a in soup.find_all('a', href=True):
                href = a['href']
                
                # 뉴스나 보도자료 주소 패턴만 타겟팅
                if '/news/' in href or '/press/' in href:
                    full_url = "https://www.digital.go.jp" + href if href.startswith('/') else href
                    
                    # 이미 수집한 링크면 패스
                    if full_url in unique_links:
                        continue
                        
                    # 제목 추출 (내부의 텍스트를 모두 합침)
                    title = a.get_text(separator=" ", strip=True)
                    
                    # 날짜 추출 시도: 해당 링크 부모나 자식 요소에서 '2025'가 있는지 확인
                    # <a> 태그 내부 혹은 근처 텍스트에서 날짜 패턴 탐색
                    context_text = a.parent.get_text() if a.parent else title
                    
                    if "2025" in context_text or "令和7" in context_text:
                        # 너무 짧거나 메뉴 항목인 경우 제외
                        if len(title) < 10: continue
                        
                        # 날짜 텍스트만 깔끔하게 정제 (예: 2025.02.10)
                        date_match = re.search(r'2025[-./]\d{1,2}[-./]\d{1,2}', context_text)
                        date_val = date_match.group() if date_match else "2025-Policy"
                        
                        unique_links.add(full_url)
                        all_data.append({
                            "date": date_val,
                            "title": title,
                            "link": full_url
                        })

            if page % 30 == 0:
                time.sleep(1)

        except Exception as e:
            print(f"\n❌ {page}페이지 오류: {e}")
            continue

    # 데이터 저장
    if all_data:
        # 날짜순 정렬
        all_data.sort(key=lambda x: x['date'], reverse=True)
        
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(all_data)
        print(f"\n\n✅ [임무 완수] 총 {len(all_data)}건의 데이터를 확보했습니다!")
    else:
        print("\n⚠️ 데이터 수집 실패")

if __name__ == "__main__":
    import re # re 모듈 추가
    crawl_digital_2025_no_limit()
