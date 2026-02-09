import requests
import csv
import time

def fetch_eu_press_final_2025():
    # 400 에러 방지를 위해 가장 안전한 기본 베이스 URL
    base_url = "https://ec.europa.eu/commission/presscorner/api/documents"
    
    all_results = []
    page = 1
    
    print("🇪🇺 [마지막 승부] 2025년 정책 데이터 수집을 재시도합니다...", flush=True)
    
    while True:
        # 파라미터를 URL 뒤에 수동으로 정확히 붙입니다. (대소문자 및 형식 강제 고정)
        # documentType=IP (Press Release), documentType=ME (Memo) 등 중 핵심인 IP만 타겟팅
        request_url = f"{base_url}?language=en&documentType=IP&pageSize=50&pageNumber={page}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*"
        }
        
        try:
            response = requests.get(request_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                if not items:
                    print("🏁 더 이상 가져올 데이터가 없습니다.", flush=True)
                    break
                
                stop_signal = False
                for item in items:
                    date_str = item.get('releaseDate', '') # 예: "05/02/2025"
                    
                    if "2025" in date_str:
                        all_results.append({
                            "날짜": date_str,
                            "제목": item.get('title'),
                            "주제": item.get('fcpTopics')[0].get('name') if item.get('fcpTopics') else "N/A",
                            "링크": f"https://ec.europa.eu/commission/presscorner/detail/en/{item.get('reference')}"
                        })
                    elif "2024" in date_str:
                        stop_signal = True
                        break
                
                print(f"📡 {page}페이지 분석 완료... (2025년 데이터 {len(all_results)}건 누적)", flush=True)
                
                if stop_signal:
                    break
                    
                page += 1
                time.sleep(0.5) # 서버 부하 방지용 휴식
                
            else:
                print(f"❌ 접속 실패: {response.status_code}", flush=True)
                print(f"🔗 시도한 URL: {request_url}", flush=True)
                break
                
        except Exception as e:
            print(f"❌ 시스템 오류: {e}", flush=True)
            break

    if all_results:
        with open('EU_Press_2025.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["날짜", "제목", "주제", "링크"])
            writer.writeheader()
            writer.writerows(all_results)
        print(f"🎉 성공! 2025년 정책 {len(all_results)}건을 CSV로 저장했습니다.", flush=True)
    else:
        print("⚠️ 수집된 데이터가 없습니다. URL 구조를 다시 점검해야 합니다.", flush=True)

if __name__ == "__main__":
    fetch_eu_press_final_2025()
