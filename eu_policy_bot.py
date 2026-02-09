import requests
import csv
import time
from datetime import datetime

def fetch_eu_policy_2025():
    # EU API 엔드포인트
    url = "https://ec.europa.eu/commission/presscorner/api/documents"
    
    all_results = []
    page = 1
    
    print("🇪🇺 [2025 전수 수집] 날짜 형식 수정 후 재시도합니다...", flush=True)
    
    while True:
        # [수정 핵심] 날짜 형식을 YYYY-MM-DD 포맷으로 변경하고, 모든 파라미터 규격을 맞췄습니다.
        params = {
            "language": "en",
            "documentType": "IP",
            "fromDate": "2025-01-01", # 이 형식이 API 표준입니다.
            "pageSize": "50",
            "pageNumber": str(page)
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*"
        }
        
        try:
            # 400 에러 방지를 위해 요청 전송
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                if not items:
                    print(f"🏁 {page}페이지에 데이터가 없습니다. 수집을 종료합니다.", flush=True)
                    break
                
                for item in items:
                    all_results.append({
                        "발행일": item.get('releaseDate'),
                        "제목": item.get('title'),
                        "주제": item.get('fcpTopics')[0].get('name') if item.get('fcpTopics') else "N/A",
                        "링크": f"https://ec.europa.eu/commission/presscorner/detail/en/{item.get('reference')}"
                    })
                
                print(f"📡 {page}페이지 수집 완료 (누적 {len(all_results)}건)", flush=True)
                page += 1
                time.sleep(0.3)
                
            else:
                print(f"❌ 에러 발생: {response.status_code}", flush=True)
                print(f"🔗 문제의 URL: {response.url}", flush=True)
                break
                
        except Exception as e:
            print(f"❌ 시스템 오류: {e}", flush=True)
            break

    if all_results:
        file_name = 'EU_Policy_2025_Final.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "제목", "주제", "링크"])
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\n🎉 성공! 2025년 데이터 총 {len(all_results)}건을 저장했습니다.", flush=True)
    else:
        print("\n⚠️ 데이터를 가져오지 못했습니다. URL을 브라우저에서 확인이 필요합니다.", flush=True)

if __name__ == "__main__":
    fetch_eu_policy_2025()
