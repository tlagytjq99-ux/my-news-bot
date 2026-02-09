import requests
import csv
import os
import time

def fetch_eu_cellar_emergency():
    # Cellar 데이터를 포함한 웹 API 검색 엔드포인트
    api_url = "https://data.europa.eu/api/hub/search/search"
    
    # [특급 처방] 복잡한 필터링 문법을 모두 버리고, 가장 단순한 파라미터만 사용합니다.
    params = {
        "q": "2025", # 검색어 자체에 연도를 넣습니다.
        "filters": "catalogue:cellar",
        "dataScope": "eu",
        "limit": 50,
        "page": 0,
        "sort": "modified-desc" # 수정일 기준 최신순
    }

    file_name = 'EU_Policy_2025_Full.csv'
    all_records = []
    
    print("🆘 [긴급 모드] SPARQL 대신 웹 API 검색으로 2025년 데이터를 강제 소환합니다...", flush=True)

    try:
        response = requests.get(api_url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('result', {}).get('results', [])
            
            if results:
                for item in results:
                    # 제목 추출
                    title_dict = item.get('title', {})
                    title = title_dict.get('en') if isinstance(title_dict, dict) else str(title_dict)
                    
                    # 날짜 추출 (issued 또는 modified)
                    date_val = item.get('issued', item.get('modified', '2025-XX-XX'))
                    doc_id = item.get('id', '')
                    link = f"https://op.europa.eu/en/publication-detail/-/publication/{doc_id}"
                    
                    all_records.append({
                        "date": date_val[:10],
                        "title": title.strip() if title else "No Title",
                        "link": link
                    })
                
                # CSV 저장
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                    writer.writeheader()
                    writer.writerows(all_records)
                print(f"🎯 [성공] 드디어 {len(all_records)}건의 데이터를 확보했습니다! {file_name}을 확인하세요.", flush=True)
            else:
                print("⚠️ 웹 API 검색 결과도 0건입니다. 키워드를 '2024'로 바꿔서 서버 생존 확인이 필요합니다.", flush=True)
        else:
            print(f"❌ API 접속 실패 ({response.status_code})", flush=True)

    except Exception as e:
        print(f"❌ 오류 발생: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_cellar_emergency()
