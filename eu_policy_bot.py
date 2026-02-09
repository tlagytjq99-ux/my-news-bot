import requests
import csv
import time

def fetch_eu_realtime_2025():
    # 실시간 보도자료/정책 발표 API
    url = "https://ec.europa.eu/commission/presscorner/api/documents"
    
    all_results = []
    page = 1
    
    print("🇪🇺 [실시간 타격] 2025년 EU 신규 정책 및 보도자료 수집을 시작합니다...", flush=True)
    
    while True:
        # 400 에러를 피하기 위해 대소문자를 완벽히 맞춘 파라미터 규격
        params = {
            "language": "en",
            "documentType": "IP", # IP는 Press Release(신규 정책 발표)를 의미합니다.
            "pageSize": "50",
            "pageNumber": str(page)
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                if not items: break
                
                stop_signal = False
                for item in items:
                    date_str = item.get('releaseDate', '')
                    
                    # 2025년 데이터만 추출
                    if "2025" in date_str:
                        all_results.append({
                            "날짜": date_str,
                            "제목": item.get('title'),
                            "주제": item.get('fcpTopics')[0].get('name') if item.get('fcpTopics') else "N/A",
                            "링크": f"https://ec.europa.eu/commission/presscorner/detail/en/{item.get('reference')}"
                        })
                    # 2024년 데이터가 나오기 시작하면 종료
                    elif "2024" in date_str:
                        stop_signal = True
                        break
                
                print(f"📡 {page}페이지 분석 완료... (현재 2025년 정책 {len(all_results)}건 확보)", flush=True)
                
                if stop_signal:
                    print("🛑 2024년 데이터 구간에 진입하여 수집을 완료합니다.", flush=True)
                    break
                    
                page += 1
                time.sleep(0.3)
            else:
                print(f"❌ 접속 실패: {response.status_code}", flush=True)
                break
        except Exception as e:
            print(f"❌ 오류 발생: {e}", flush=True)
            break

    if all_results:
        # 파일명을 2025년 전수 데이터로 명시
        with open('EU_2025_Policy_List.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["날짜", "제목", "주제", "링크"])
            writer.writeheader()
            writer.writerows(all_results)
        print(f"🎉 성공! 2025년 EU 핵심 정책 {len(all_results)}건을 획득했습니다!", flush=True)
    else:
        print("⚪ 수집된 데이터가 없습니다.", flush=True)

if __name__ == "__main__":
    fetch_eu_realtime_2025()
