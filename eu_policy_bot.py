import requests
import csv

def fetch_eu_cellar_2025():
    # Cellar SPARQL 엔드포인트 주소
    url = "https://publications.europa.eu/webapi/rdf/sparql"
    
    # 2025년 1월 1일 이후의 법령(Work)을 찾는 SPARQL 쿼리
    sparql_query = """
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    
    SELECT DISTINCT ?work ?title ?date
    WHERE {
      ?work a cdm:resource_legal ;
            cdm:resource_legal_date_entry-into-force ?date ;
            cdm:work_has_title ?title_resource .
      ?title_resource cdm:title_has_value ?title .
      FILTER(?date >= "2025-01-01"^^xsd:date)
    }
    ORDER BY DESC(?date)
    LIMIT 100
    """
    
    params = {
        "query": sparql_query,
        "format": "application/sparql-results+json"
    }
    
    print("🏛️ EU Cellar 창고에서 2025년 최신 법령을 검색 중...", flush=True)
    
    try:
        response = requests.get(url, params=params, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            rows = data.get('results', {}).get('bindings', [])
            
            results = []
            for row in rows:
                results.append({
                    "날짜": row.get('date', {}).get('value'),
                    "제목": row.get('title', {}).get('value'),
                    "Cellar_ID": row.get('work', {}).get('value').split('/')[-1]
                })
            
            if results:
                with open('EU_Cellar_2025.csv', 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["날짜", "제목", "Cellar_ID"])
                    writer.writeheader()
                    writer.writerows(results)
                print(f"🎉 성공! 2025년 법령 {len(results)}건을 창고에서 꺼내왔습니다!", flush=True)
            else:
                print("⚪ 2025년 데이터가 아직 창고에 반영되지 않았거나 쿼리 조건이 너무 엄격합니다.", flush=True)
        else:
            print(f"❌ 접속 실패: {response.status_code}", flush=True)
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_cellar_2025()
