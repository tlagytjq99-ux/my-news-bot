import requests
import csv
import os

def fetch_eu_cellar_sparql():
    # Cellar 공식 SPARQL 엔드포인트
    sparql_url = "https://publications.europa.eu/webapi/rdf/sparql"
    
    # 2025년 영어 정책 문서를 가져오는 SPARQL 쿼리
    query = """
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT DISTINCT ?work ?title ?date
    WHERE {
      ?work cdm:work_date_document ?date .
      ?work cdm:work_has_resource-type ?type .
      ?work cdm:work_has_expression ?expr .
      ?expr cdm:expression_title ?title .
      ?expr cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> .
      
      FILTER(?date >= "2025-01-01"^^xsd:date && ?date <= "2025-12-31"^^xsd:date)
    }
    ORDER BY DESC(?date)
    LIMIT 1000
    """

    file_name = 'EU_Policy_2025_Full.csv'
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "Mozilla/5.0"
    }

    print("🚀 [Cellar SPARQL 타격] 2025년 정책 DB에 직접 쿼리를 전송합니다...", flush=True)

    try:
        response = requests.get(sparql_url, params={'query': query}, headers=headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {}).get('bindings', [])
            
            all_records = []
            for item in results:
                # Cellar 고유 ID 추출 (URI에서 ID만 분리)
                work_uri = item['work']['value']
                cellar_id = work_uri.split('/')[-1]
                
                title = item['title']['value']
                date = item['date']['value']
                link = f"https://op.europa.eu/en/publication-detail/-/publication/{cellar_id}"
                
                all_records.append({
                    "date": date,
                    "title": title,
                    "link": link
                })
            
            # 저장 로직
            if all_records:
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                    writer.writeheader()
                    writer.writerows(all_records)
                print(f"✅ [성공] 총 {len(all_records)}건의 데이터를 성공적으로 수집하여 {file_name}에 저장했습니다!", flush=True)
            else:
                print("⚠️ 쿼리는 성공했으나 결과가 0건입니다.", flush=True)
        else:
            print(f"❌ SPARQL 서버 응답 오류: {response.status_code}", flush=True)
            print(f"상세 내용: {response.text[:200]}", flush=True)

    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_cellar_sparql()
