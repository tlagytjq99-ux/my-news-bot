import csv
from SPARQLWrapper import SPARQLWrapper, JSON

def fetch_eu_cellar_sparql():
    # 1. 공식 SPARQL 엔드포인트 설정
    endpoint_url = "https://publications.europa.eu/webapi/rdf/sparql"
    sparql = SPARQLWrapper(endpoint_url)
    
    # 2. 최적화된 쿼리 (2025년 이후의 공식 보도자료 및 정책 문서)
    # 서버 타임아웃을 방지하기 위해 필요한 필드만 SELECT 합니다.
    query = """
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT DISTINCT ?work ?date ?title
    WHERE {
      ?work a cdm:work ;
            cdm:work_date_document ?date ;
            cdm:work_has_title ?title_res .
      ?title_res cdm:title_has_content ?title .
      
      # 2025년 1월 1일 이후 데이터 필터링
      FILTER(?date >= "2025-01-01"^^xsd:date)
      # 영어 제목만 수집
      FILTER(lang(?title) = "en")
      
      # 문서 타입 제한 (보도자료 등 정책 관련)
      ?work cdm:work_has_resource-type <http://publications.europa.eu/resource/authority/resource-type/PRESS_REL> .
    }
    ORDER BY DESC(?date)
    LIMIT 100
    """
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.setTimeout(120) # 인내심을 2분으로 설정

    print(f"🏛️ Cellar SPARQL 엔진 접속 중... (2025년 이후 데이터 추출)", flush=True)
    
    file_name = 'EU_Policy_2025_Full.csv'
    collected_data = []

    try:
        results = sparql.query().convert()
        
        for result in results["results"]["bindings"]:
            work_url = result["work"]["value"]
            date = result["date"]["value"]
            title = result["title"]["value"]
            
            # Cellar URI에서 웹 접근 가능한 URL로 변환
            uuid = work_url.split('/')[-1]
            link = f"https://publications.europa.eu/resource/cellar/{uuid}"

            collected_data.append({
                "date": date,
                "title": title,
                "link": link
            })
            
        print(f"✅ 수집 성공! 총 {len(collected_data)}건의 데이터를 확보했습니다.", flush=True)

    except Exception as e:
        print(f"❌ SPARQL 쿼리 실패: {e}", flush=True)

    # 3. 저장 (데이터가 없어도 헤더 포함 생성)
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
        writer.writeheader()
        if collected_data:
            writer.writerows(collected_data)
        else:
            writer.writerow({"date": "2026-02-09", "title": "No data found with current filters", "link": "N/A"})

if __name__ == "__main__":
    fetch_eu_cellar_sparql()
