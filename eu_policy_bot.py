import requests
import csv

def fetch_eu_cellar_2025_relaxed():
    url = "https://publications.europa.eu/webapi/rdf/sparql"
    
    # [수정 핵심] 날짜 필터링을 가장 범용적인 'dc:date'로 변경하고 형식을 유연하게 잡았습니다.
    sparql_query = """
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT DISTINCT ?work ?title ?date
    WHERE {
      ?work a cdm:resource_legal .
      ?work dc:date ?date .
      ?work cdm:work_has_title ?title_res .
      ?title_res cdm:title_has_value ?title .
      
      # 2025년으로 시작하는 모든 날짜 텍스트를 검색
      FILTER(strstarts(str(?date), "2025"))
      
      # 영어 제목만 필터링 (가독성을 위해)
      FILTER(lang(?title) = "en")
    }
    ORDER BY DESC(?date)
    LIMIT 100
    """
    
    params = {
        "query": sparql_query,
        "format": "application/sparql-results+json"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/sparql-results+json"
    }
    
    print("🏛️ [Cellar 2차 공략] 2025년 법령 및 규제 전수 조사 중...", flush=True)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            rows = data.get('results', {}).get('bindings', [])
            
            results = []
            for row in rows:
                results.append({
                    "날짜": row.get('date', {}).get('value'),
                    "제목": row.get('title', {}).get('value'),
                    "상세주소": f"https://publications.europa.eu/resource/cellar/{row.get('work', {}).get('value').split('/')[-1]}"
                })
            
            if results:
                file_name = 'EU_Cellar_2025_Final.csv'
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["날짜", "제목", "상세주소"])
                    writer.writeheader()
                    writer.writerows(results)
                print(f"🎉 성공! 2025년 법적 문서 {len(results)}건을 찾아냈습니다.", flush=True)
            else:
                print("⚪ 여전히 2025년 데이터가 잡히지 않습니다. Cellar 시스템 반영 속도가 보도자료보다 늦을 수 있습니다.", flush=True)
        else:
            print(f"❌ 접속 실패: {response.status_code}", flush=True)
            print(f"📡 서버 응답: {response.text[:200]}", flush=True)
            
    except Exception as e:
        print(f"❌ 오류: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_cellar_2025_relaxed()
