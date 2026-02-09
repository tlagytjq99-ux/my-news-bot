import requests
import json
import os

def fetch_eu_policies_2025():
    # EU Cellar SPARQL 엔드포인트
    url = "http://publications.europa.eu/webapi/rdf/sparql"
    
    # 2025년에 발행된 문서의 제목, 날짜, 원문 링크를 가져오는 쿼리
    query = """
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT DISTINCT ?work ?title ?date
    WHERE {
        ?work cdm:work_date_document ?date .
        ?work cdm:resource_legal_title ?title .
        FILTER(?date >= "2025-01-01"^^xsd:date && ?date <= "2025-12-31"^^xsd:date)
        FILTER(LANG(?title) = "en")
    }
    ORDER BY DESC(?date)
    LIMIT 100
    """
    
    params = {
        'query': query,
        'format': 'application/sparql-results+json'
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        with open('eu_policies_2025.json', 'w', encoding='utf-8') as f:
            json.dump(data['results']['bindings'], f, ensure_ascii=False, indent=4)
        print(f"Successfully saved {len(data['results']['bindings'])} records.")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    fetch_eu_policies_2025()
