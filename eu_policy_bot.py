import requests
import csv
import os

def fetch_eu_cellar_final_integrated():
    # 1. SPARQL 엔드포인트 (대표님이 주신 주소)
    sparql_url = "https://publications.europa.eu/webapi/rdf/sparql"
    
    # [쿼리 수정] 대표님 코드의 형식을 유지하되, 2025년 전체를 타겟팅합니다.
    # 복잡한 resource-type 필터를 빼서 검색 결과가 0건이 나오는 걸 방지했습니다.
    query = """
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT DISTINCT ?work ?date ?title
    WHERE {
      ?work a cdm:work ;
            cdm:work_date_document ?date ;
            cdm:work_has_expression ?expr .
      ?expr cdm:expression_title ?title .
      ?expr cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> .
      
      FILTER(?date >= "2025-01-01"^^xsd:date)
    }
    ORDER BY DESC(?date)
    LIMIT 100
    """

    file_name = 'EU_Policy_2025_Full.csv'
    headers = {"Accept": "application/sparql-results+json"}

    print("🛰️ 대표님 코드 로직으로 Cellar DB 직접 조회를 시작합니다...", flush=True)

    try:
        # SPARQLWrapper 대신 requests로 직접 포스트 요청 (설치 오류 방지)
        response = requests.post(sparql_url, data={'query': query}, headers=headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            bindings = data.get('results', {}).get('bindings', [])
            
            all_records = []
            for item in bindings:
                cellar_url = item['work']['value']
                uuid = cellar_url.split('/')[-1]
                title = item['title']['value']
                date = item['date']['value']
                
                # 대표님 코드의 2단계: 상세 페이지 링크 생성
                link = f"https://op.europa.eu/en/publication-detail/-/publication/{uuid}"
                
                all_records.append({
                    "date": date,
                    "title": title,
                    "link": link
                })

            if all_records:
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                    writer.writeheader()
                    writer.writerows(all_records)
                print(f"✅ [성공] {len(all_records)}건의 정책 데이터를 수집했습니다!", flush=True)
            else:
                print("⚠️ 쿼리는 성공했으나 조건에 맞는 데이터가 없습니다.", flush=True)
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}", flush=True)

    except Exception as e:
        print(f"❌ 실행 중 오류: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_cellar_final_integrated()
