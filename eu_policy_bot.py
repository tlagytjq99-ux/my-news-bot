import requests
import csv
import os
import time

def fetch_eu_core_policy_only():
    api_url = "https://data.europa.eu/api/hub/search/search"
    
    # 2025년 데이터 요청 파라미터
    params = {
        "filters": "catalogue,dataset,resource",
        "dataScope": "eu",
        "dateType": "issued",
        "minDate": "2025-01-01T00:00:00.000Z",
        "maxDate": "2025-12-31T23:59:59.000Z",
        "includes": "id,title.en,description.en,issued,publisher", # publisher 정보 추가
        "limit": 100,
        "page": 0
    }

    file_name = 'EU_Policy_2025_Full.csv'
    all_records = []
    
    # [핵심] 우리가 신뢰하는 EU 본부 기관 키워드 (여기에 해당해야 수집)
    core_publishers = [
        "European Commission", 
        "European Parliament", 
        "Council of the European Union", 
        "European External Action Service",
        "European Environment Agency",
        "Publications Office of the European Union",
        "Eurostat" # 통계지만 EU 전체 통계이므로 포함
    ]

    print("🏛️ EU 본부(Commission 등) 발행 정책 데이터만 선별 수집을 시작합니다.", flush=True)

    while True:
        try:
            response = requests.get(api_url, params=params, timeout=30)
            if response.status_code != 200:
                break
            
            data = response.json()
            results = data.get('result', {}).get('results', [])
            
            if not results:
                break
            
            for item in results:
                # 발행자 정보 확인
                publisher_info = item.get('publisher', {})
                publisher_name = str(publisher_info.get('label', ''))
                
                # [필터 로직] 발행자 이름에 핵심 EU 기관 키워드가 있는지 확인
                is_core_eu = any(org in publisher_name for org in core_publishers)
                
                # 이탈리아 등 국가기관(예: ISTAT, Ministry of...)은 여기서 걸러짐
                if is_core_eu:
                    title = item.get('title', {}).get('en', 'No English Title')
                    issued_date = item.get('issued', 'N/A')
                    doc_id = item.get('id', '')
                    link = f"https://data.europa.eu/data/datasets/{doc_id}?locale=en"
                    
                    all_records.append({
                        "date": issued_date[:10],
                        "title": title,
                        "link": link
                    })
            
            print(f"📦 현재 페이지: {params['page']}, 필터링 후 누적: {len(all_records)}건", flush=True)
            
            params['page'] += 1
            time.sleep(0.1)

            # 너무 오래 걸릴 수 있으므로 테스트를 위해 일정량 수집 시 중단하고 싶다면 
            # 아래 주석을 해제하세요. (전수조사시는 주석 유지)
            # if params['page'] > 50: break 

        except Exception as e:
            print(f"❌ 오류: {e}", flush=True)
            break

    # CSV 저장
    if all_records:
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(all_records)
        print(f"🎯 선별 수집 성공! 총 {len(all_records)}건의 EU 본부 데이터를 저장했습니다.", flush=True)

if __name__ == "__main__":
    fetch_eu_core_policy_only()
