import csv
from SPARQLWrapper import SPARQLWrapper, JSON

def fetch_eu_cellar_sparql_final():
    endpoint_url = "https://publications.europa.eu/webapi/rdf/sparql"
    sparql = SPARQLWrapper(endpoint_url)
    
    # 쿼리 수정: 특정 타입을 지정하지 않고 '2025년 이후의 모든 영어 제목 문서'를 가져옵니다.
    query = """
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT DISTINCT ?work ?date ?title
    WHERE {
      ?work a cdm:work ;
            cdm:work_date_document ?date ;
            cdm:work_has_title ?title_res .
      ?title_res cdm:title_has_content ?title .
      
      # 2025년 1월 1일 이후 데이터
      FILTER(?date >= "2025-01-01"^^xsd:date)
      # 영어 제목만
      FILTER(lang(?title) = "en")
    }
    ORDER BY DESC(?date)
    LIMIT 200
    """
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.setTimeout(180) # 서버 부하를 고려해 대기 시간을 3분으로 늘림

    print(f"🏛️ Cellar SPARQL 엔진 재접속 중... (필터 완화 버전)", flush=True)
    
    file_name = 'EU_Policy_2025_Full.csv'
    collected_data = []

    try:
        results = sparql.query().convert()
        
        for result in results["results"]["bindings"]:
            work_url = result["work"]["value"]
            date = result["date"]["value"]
            title = result["title"]["value"]
            
            uuid = work_url.split('/')[-1]
            link = f"https://publications.europa.eu/resource/cellar/{uuid}"

            collected_data.append({
                "date": date,
                "title": title,
                "link": link
            })
            
        print(f"✅ 수집 성공! 2025년 데이터 {len(collected_data)}건 확보 완료.", flush=True)

    except Exception as e:
        print(f"❌ SPARQL 쿼리 실패: {e}", flush=True)

    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
        writer.writeheader()
        if collected_data:
            writer.writerows(collected_data)
        else:
            # 여전히 0건일 경우를 대비한 가상 데이터
            writer.writerow({"date": "2025-01-01", "title": "No Data Found - Check indexing status", "link": "N/A"})

if __name__ == "__main__":
    fetch_eu_cellar_sparql_final()
