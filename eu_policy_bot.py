import requests
import csv
import os

def fetch_eu_cellar_final_push():
    sparql_url = "https://publications.europa.eu/webapi/rdf/sparql"
    
    # [전략 변경] 날짜 필터를 아예 제거하고, 최신 발행 문서 1000개를 무조건 가져옵니다.
    query = """
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    
    SELECT DISTINCT ?work ?title ?date
    WHERE {
      ?work cdm:work_date_document ?date .
      ?work cdm:work_has_expression ?expr .
      ?expr cdm:expression_title ?title .
      ?expr cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> .
    }
    ORDER BY DESC(?date)
    LIMIT 1000
    """

    file_name = 'EU_Policy_2025_Full.csv'
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "Mozilla/5.0"
    }

    print("🎣 [최신순 전수 수집] DB에서 최신 데이터 1,000건을 통째로 견인합니다...", flush=True)

    try:
        response = requests.get(sparql_url, params={'query': query}, headers=headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {}).get('bindings', [])
            
            all_records = []
            for item in results:
                date_val = item['date']['value']
                # [필터] 가져온 데이터 중 2025년이 포함된 것만 골라 담기
                if "2025" in date_val:
                    work_uri = item['work']['value']
                    cellar_id = work_uri.split('/')[-1]
                    title = item['title']['value']
                    
                    link = f"https://op.europa.eu/en/publication-detail/-/publication/{cellar_id}"
                    
                    all_records.append({
                        "date": date_val,
                        "title": title,
                        "link": link
                    })
            
            if all_records:
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                    writer.writeheader()
                    writer.writerows(all_records)
                print(f"🎯 [성공] 2025년 데이터 {len(all_records)}건을 선별하여 저장했습니다!", flush=True)
            else:
                # 여기까지 왔는데 0건이면 DB에 기록된 최신 날짜가 언제인지 확인해봅니다.
                latest_date = results[0]['date']['value'] if results else "데이터 없음"
                print(f"⚠️ 2025년 데이터가 선별되지 않았습니다. (DB 최신 날짜 샘플: {latest_date})", flush=True)
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}", flush=True)

    except Exception as e:
        print(f"❌ 오류 발생: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_cellar_final_push()
