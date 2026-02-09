import requests
import csv

def fetch_eu_cellar_perfect_guide():
    # 공식 문서에서 지정한 SPARQL 엔드포인트
    sparql_url = "https://publications.europa.eu/webapi/rdf/sparql"
    
    # [가이드 최적화 쿼리]
    # 1. 여러 날짜 필드(document, creation)를 동시에 체크
    # 2. 2025년 키워드 매칭
    # 3. 영어(ENG) 결과만 한정
    query = """
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    
    SELECT DISTINCT ?work ?date ?title
    WHERE {
      {
        ?work cdm:work_date_document ?date .
      } UNION {
        ?work cdm:work_date_creation ?date .
      }
      
      ?work cdm:work_has_expression ?expr .
      ?expr cdm:expression_title ?title .
      ?expr cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> .
      
      FILTER(contains(str(?date), "2025"))
    }
    ORDER BY DESC(?date)
    LIMIT 100
    """

    file_name = 'EU_Policy_2025_Full.csv'
    headers = {"Accept": "application/sparql-results+json"}

    print("📖 [공식 가이드 적용] Cellar DB 심층 쿼리를 시작합니다...", flush=True)

    try:
        response = requests.post(sparql_url, data={'query': query}, headers=headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            bindings = data.get('results', {}).get('bindings', [])
            
            all_records = []
            for item in bindings:
                work_uri = item['work']['value']
                uuid = work_uri.split('/')[-1]
                title = item['title']['value']
                date = item['date']['value']
                
                # 상세 페이지 링크
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
                print(f"✅ [성공] {len(all_records)}건의 데이터를 수집했습니다!", flush=True)
            else:
                print("⚠️ 2025년 데이터가 아직 인덱싱되지 않았습니다. 2024년 말 데이터 수집을 고려해 보세요.", flush=True)
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}", flush=True)

    except Exception as e:
        print(f"❌ 실행 오류: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_cellar_perfect_guide()
