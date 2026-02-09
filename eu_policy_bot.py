import requests
import csv
import os

def fetch_eu_direct_official_api():
    # EU 간행물처 공식 검색 API (op.europa.eu 직통)
    # 2025년 발행된(DN=2025*) 영문(LNG=ENG) 문서를 검색합니다.
    api_url = "https://op.europa.eu/en/web/api/search"
    
    params = {
        "q": "DN=2025*", # 2025년 발행 번호를 가진 모든 문서
        "lang": "en",
        "rows": 100,      # 한 번에 100건 수집
        "start": 1,
        "sort": "date_publication_desc" # 발행일 최신순
    }

    file_name = 'EU_Policy_2025_Full.csv'
    all_records = []
    
    print("🎯 [직통 통로] EU 간행물처 공식 API에 직접 연결합니다...", flush=True)

    try:
        response = requests.get(api_url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            # 공식 API는 'results' 안에 데이터를 담고 있습니다.
            results = data.get('results', [])
            
            if results:
                for item in results:
                    title = item.get('title', 'No Title')
                    date = item.get('date_publication', '2025-XX-XX')
                    # 문서 고유 ID를 통해 직접 링크 생성
                    doc_id = item.get('id', '')
                    link = f"https://op.europa.eu/en/publication-detail/-/publication/{doc_id}"
                    
                    all_records.append({
                        "date": date[:10] if date else "2025-XX-XX",
                        "title": title.strip(),
                        "link": link
                    })
                
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                    writer.writeheader()
                    writer.writerows(all_records)
                print(f"✅ [성공] 공식 루트를 통해 {len(all_records)}건을 확보했습니다!", flush=True)
            else:
                print("⚠️ 공식 API에서도 결과가 0건입니다. 쿼리 키워드를 '2024'로 테스트해봅니다.", flush=True)
        else:
            print(f"❌ 접속 오류: {response.status_code}", flush=True)

    except Exception as e:
        print(f"❌ 시스템 오류: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_direct_official_api()
