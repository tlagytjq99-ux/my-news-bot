import requests
import csv
from SPARQLWrapper import SPARQLWrapper, JSON

def fetch_eu_cellar_2025_full():
    # 1. SPARQL 설정
    sparql = SPARQLWrapper("https://publications.europa.eu/webapi/rdf/sparql")
    
    # 2025년 1월 1일부터 12월 31일까지의 보도자료(PRESS_REL) 수집 쿼리
    query = """
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT DISTINCT ?work ?date ?title
    WHERE {
      ?work a cdm:work ;
            cdm:work_has_resource-type <http://publications.europa.eu/resource/authority/resource-type/PRESS_REL> ;
            cdm:work_date_document ?date ;
            cdm:work_has_title ?title_res .
      ?title_res cdm:title_has_content ?title .
      
      # 날짜 범위 지정: 2025년 전체
      FILTER(?date >= "2025-01-01"^^xsd:date && ?date <= "2025-12-31"^^xsd:date)
      FILTER(lang(?title) = "en")
    }
    ORDER BY DESC(?date)
    """
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    print("🏛️ EU Cellar에서 2025년 정책 데이터를 전수 조사 중...", flush=True)
    
    try:
        results = sparql.query().convert()
        bindings = results["results"]["bindings"]
        
        collected_data = []
        for row in bindings:
            uuid = row["work"]["value"].split('/')[-1]
            collected_data.append({
                "date": row["date"]["value"],
                "title": row["title"]["value"],
                "link": f"https://publications.europa.eu/resource/cellar/{uuid}"
            })
        
        # CSV 저장
        if collected_data:
            with open('EU_Policy_2025_Full.csv', 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                writer.writeheader()
                writer.writerows(collected_data)
            print(f"✅ 수집 완료! 총 {len(collected_data)}건의 데이터를 저장했습니다.", flush=True)
        else:
            print("⚪ 해당 기간의 데이터가 없습니다.", flush=True)

    except Exception as e:
        print(f"❌ 오류 발생: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_cellar_2025_full()
