import requests
import csv
import time
import os

def fetch_eu_cellar_publications():
    # Cellar 데이터를 포함한 EU 데이터 허브의 검색 엔드포인트
    api_url = "https://data.europa.eu/api/hub/search/search"
    
    # [Cellar 최적화 파라미터] 
    # 주신 가이드의 핵심인 'cellar' 카탈로그를 명시적으로 타겟팅합니다.
    params = {
        "filters": "catalogue:cellar",
        "dataScope": "eu",
        "dateType": "issued",
        "minDate": "2025-01-01T00:00:00.000Z",
        "maxDate": "2025-12-31T23:59:59.000Z",
        "includes": "id,title.en,issued,description.en,publisher",
        "limit": 50,
        "page": 0,
        "sort": "issued-desc"
    }

    file_name = 'EU_Policy_2025_Full.csv'
    all_records = []
    
    print(f"🏛️ [Cellar 정밀 수집] 2025년 정책 간행물 저장소 접속 중...", flush=True)

    try:
        while True:
            # 400 에러를 피하기 위해 가장 깔끔한 형태로 요청 전송
            response = requests.get(api_url, params=params, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ API 응답 오류 ({response.status_code})", flush=True)
                break
            
            data = response.json()
            results = data.get('result', {}).get('results', [])
            
            if not results:
                print("🏁 수집 완료: 더 이상 가져올 간행물이 없습니다.", flush=True)
                break
            
            for item in results:
                # 제목 추출 로직 강화
                title_dict = item.get('title', {})
                title = title_dict.get('en') if isinstance(title_dict, dict) else str(title_dict)
                
                # 'None'이거나 제목이 없는 경우 제외
                if not title or title == 'None':
                    continue

                issued_date = item.get('issued', '2025-XX-XX')
                doc_id = item.get('id', '')
                
                # Cellar 고유 주소를 활용한 직접 링크 생성
                # 이 링크는 PDF 및 원문 열람 페이지로 바로 연결됩니다.
                link = f"https://op.europa.eu/en/publication-detail/-/publication/{doc_id}"
                
                all_records.append({
                    "date": issued_date[:10],
                    "title": title.strip(),
                    "link": link
                })
            
            print(f"✅ {params['page'] + 1}페이지 완료 (누적 {len(all_records)}건)", flush=True)
            
            params['page'] += 1
            # 전수 조사를 위해 페이지 제한 없이 끝까지 돌리거나, 
            # 안전을 위해 우선 50페이지(2500건)까지 설정
            if params['page'] >= 50: break 
            
            time.sleep(0.3)

    except Exception as e:
        print(f"❌ 실행 오류: {e}", flush=True)

    # 최종 저장
    if all_records:
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(all_records)
        print(f"💾 [성공] {len(all_records)}건의 Cellar 데이터를 '{file_name}'에 저장했습니다.", flush=True)
    else:
        print("⚠️ 수집된 데이터가 없습니다. 필터를 다시 확인해봐야 합니다.", flush=True)

if __name__ == "__main__":
    fetch_eu_cellar_publications()
