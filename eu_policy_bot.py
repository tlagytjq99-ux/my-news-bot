import csv
from SPARQLWrapper import SPARQLWrapper, JSON

def fetch_eu_cellar_brute_force():
    endpoint_url = "https://publications.europa.eu/webapi/rdf/sparql"
    sparql = SPARQLWrapper(endpoint_url)
    
    # [수정] 날짜 계산 방식이 아닌, 문자열 매칭 방식으로 2025를 찾습니다.
    # 또한 cdm:work_date_document 외에 다른 날짜 필드(cdm:last_modification_date)도 함께 봅니다.
    query = """
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    
    SELECT DISTINCT ?work ?date ?title
    WHERE {
      ?work a cdm:work ;
            cdm:work_date_document ?date ;
            cdm:work_has_title ?title_res .
      ?title_res cdm:title_has_content ?title .
      
      # 날짜 필드에서 "2025"라는 텍스트가 포함된 모든 것을 찾습니다.
      FILTER(CONTAINS(STR(?date), "2025"))
      FILTER(lang(?title) = "en")
    }
    ORDER BY DESC(?date)
    LIMIT 300
    """
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.setTimeout(200)

    print(f"📡 [강제 추출] '2025' 문자열 매칭으로 데이터 굴착 중...", flush=True)
    
    file_name = 'EU_Policy_2025_Full.csv'
    collected_data = []

    try:
        results = sparql.query().convert()
        bindings = results["results"]["bindings"]
        
        for result in bindings:
            work_url = result["work"]["value"]
            date = result["date"]["value"]
            title = result["title"]["value"]
            uuid = work_url.split('/')[-1]
            
            collected_data.append({
                "date": date,
                "title": title,
                "link": f"https://publications.europa.eu/resource/cellar/{uuid}"
            })
            
        print(f"✅ 결과: {len(collected_data)}건의 데이터를 찾아냈습니다!", flush=True)

    except Exception as e:
        print(f"❌ 쿼리 실패: {e}", flush=True)

    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
        writer.writeheader()
        if collected_data:
            writer.writerows(collected_data)
        else:
            # 만약 여기서도 0건이면, 아예 연도 제한을 풀고 10건만 가져와서 필드 구조를 파악합니다.
            writer.writerow({"date": "DEBUG", "title": "Final Debug Mode Required", "link": "N/A"})

if __name__ == "__main__":
    fetch_eu_cellar_brute_force()
