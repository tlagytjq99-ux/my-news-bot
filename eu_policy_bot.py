import requests
import csv
import time
import sys
from datetime import datetime

def fetch_eu_policy_2025():
    url = "https://ec.europa.eu/commission/presscorner/api/documents"
    
    # 수집 결과를 담을 리스트
    all_results = []
    page = 1
    
    print("🇪🇺 [전수 수집] 2025년 EU 정책 데이터 수집을 시작합니다...", flush=True)
    
    while True:
        # 파라미터 설정: 2025년 1월 1일(fromDate)부터 현재까지
        params = {
            "language": "en",
            "documentType": "IP",
            "fromDate": "01/01/2025", # EU API는 일/월/년 형식을 선호합니다.
            "pageSize": "100",        # 한 번에 100건씩 팍팍 가져옵니다.
            "pageNumber": str(page)
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                if not items: # 더 이상 가져올 데이터가 없으면 종료
                    break
                
                for item in items:
                    all_results.append({
                        "발행일": item.get('releaseDate'),
                        "제목": item.get('title'),
                        "주제": item.get('fcpTopics')[0].get('name') if item.get('fcpTopics') else "N/A",
                        "링크": f"https://ec.europa.eu/commission/presscorner/detail/en/{item.get('reference')}"
                    })
                
                print(f"📡 {page}페이지 수집 완료... (현재까지 총 {len(all_results)}건)", flush=True)
                
                # 다음 페이지로 이동
                page += 1
                time.sleep(0.2) # 서버 부하 방지
                
            elif response.status_code == 400:
                print(f"❌ 400 에러 발생: 파라미터를 확인하세요. URL: {response.url}", flush=True)
                break
            else:
                print(f"❌ 서버 에러: {response.status_code}", flush=True)
                break
                
        except Exception as e:
            print(f"❌ 실행 중 오류: {e}", flush=True)
            break

    # 최종 결과 저장
    if all_results:
        file_name = 'EU_Policy_2025_All.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "제목", "주제", "링크"])
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\n🎉 [수집 종료] 2025년 데이터 총 {len(all_results)}건 저장 완료!", flush=True)
    else:
        print("\n⚠️ 수집된 데이터가 하나도 없습니다.", flush=True)

if __name__ == "__main__":
    fetch_eu_policy_2025()
