import requests
import csv
import time
from datetime import datetime

def fetch_eu_policy_2025():
    url = "https://ec.europa.eu/commission/presscorner/api/documents"
    
    all_results = []
    page = 1
    target_year = "2025"
    stop_collecting = False
    
    print(f"🇪🇺 [2025 전수 수집] 최신순 역추적 방식으로 전환합니다...", flush=True)
    
    while not stop_collecting:
        # 에러를 유발하던 날짜 파라미터를 제거하고 가장 안전한 기본값만 사용합니다.
        params = {
            "language": "en",
            "documentType": "IP",
            "pageSize": "50",
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
                
                if not items:
                    print("🏁 더 이상 가져올 데이터가 없습니다.", flush=True)
                    break
                
                for item in items:
                    date_str = item.get('releaseDate', '') # 보통 '05/02/2025' 형식
                    
                    # 2025년 데이터인지 확인 (날짜 문자열에 '2025'가 포함되어 있는지 체크)
                    if target_year in date_str:
                        all_results.append({
                            "발행일": date_str,
                            "제목": item.get('title'),
                            "주제": item.get('fcpTopics')[0].get('name') if item.get('fcpTopics') else "N/A",
                            "링크": f"https://ec.europa.eu/commission/presscorner/detail/en/{item.get('reference')}"
                        })
                    # 만약 데이터가 2024년으로 넘어갔다면 수집 중단
                    elif "2024" in date_str:
                        print(f"🛑 2024년 데이터 발견 ({date_str}). 수집을 종료합니다.", flush=True)
                        stop_collecting = True
                        break
                
                if not stop_collecting:
                    print(f"📡 {page}페이지 수집 중... (2025년 데이터 현재 {len(all_results)}건)", flush=True)
                    page += 1
                    time.sleep(0.3)
            else:
                print(f"❌ 접속 실패: {response.status_code}", flush=True)
                break
                
        except Exception as e:
            print(f"❌ 오류 발생: {e}", flush=True)
            break

    # 파일 저장
    if all_results:
        file_name = 'EU_Policy_2025_Final.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "제목", "주제", "링크"])
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\n🎉 [성공] 2025년 데이터 총 {len(all_results)}건을 낚아 올렸습니다!", flush=True)
    else:
        print("\n⚠️ 수집된 2025년 데이터가 없습니다.", flush=True)

if __name__ == "__main__":
    fetch_eu_policy_2025()
