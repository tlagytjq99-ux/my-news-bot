import requests
import csv
import os
import time

def fetch_eu_data_hub_fixed():
    # 1. API 주소
    api_url = "https://data.europa.eu/api/hub/search/search"
    
    # 2. [수정] 400 에러 방지를 위한 정밀 파라미터 세팅
    params = {
        "filters": "catalogue,dataset,resource", # API 표준 형식으로 수정
        "dataScope": "eu",
        "dateType": "issued",
        "minDate": "2025-01-01T00:00:00.000Z",
        "maxDate": "2025-12-31T23:59:59.000Z",
        "includes": "id,title.en,issued",
        "limit": 50,  # 안정성을 위해 50개씩 끊어서 요청
        "page": 0,
        "sort": "issued-desc" # 최신순 정렬 추가
    }

    file_name = 'EU_Policy_2025_Full.csv'
    all_records = []
    
    print(f"📡 [재가동] EU API 정밀 접속 시도 중... (대상: 2025년 전체)", flush=True)

    try:
        while True:
            response = requests.get(api_url, params=params, timeout=30)
            
            # 응답 로그 출력 (디버깅용)
            if response.status_code != 200:
                print(f"❌ 서버 응답 에러: {response.status_code}", flush=True)
                print(f"❌ 에러 내용: {response.text[:200]}", flush=True)
                break
            
            data = response.json()
            # 데이터 구조 심층 탐색
            results = data.get('result', {}).get('results', [])
            
            if not results:
                print("🏁 수집 완료: 더 이상의 데이터가 없습니다.", flush=True)
                break
            
            for item in results:
                # 제목 추출 (영어 우선, 없으면 기본 제목)
                title_dict = item.get('title', {})
                title = title_dict.get('en') if isinstance(title_dict, dict) else str(title_dict)
                if not title or title == 'None': title = "No English Title"
                
                issued_date = item.get('issued', '2025-XX-XX')
                doc_id = item.get('id', '')
                link = f"https://data.europa.eu/data/datasets/{doc_id}?locale=en"
                
                all_records.append({
                    "date": issued_date[:10],
                    "title": title.strip(),
                    "link": link
                })
            
            print(f"✅ {params['page'] + 1}페이지 완료 (누적 {len(all_records)}건 확보)", flush=True)
            
            # 전수 조사를 위해 페이지를 계속 넘깁니다 (테스트 시 5페이지로 제한 가능)
            params['page'] += 1
            if params['page'] > 100: break # 안전장치: 최대 5000건까지만
            
            time.sleep(0.3) # 서버 부하 방지

    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}", flush=True)

    # 3. 파일 저장 보장 로직
    if all_records:
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(all_records)
        print(f"💾 [최종] {len(all_records)}건의 데이터를 '{file_name}'에 저장했습니다!", flush=True)
    else:
        print("⚠️ 수집된 데이터가 없습니다. 파라미터를 다시 점검해야 합니다.", flush=True)

if __name__ == "__main__":
    fetch_eu_data_hub_fixed()
