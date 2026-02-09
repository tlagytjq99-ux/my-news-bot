import requests
import csv

def fetch_eu_cellar_recovery():
    # 공식 SPARQL 엔드포인트
    sparql_url = "https://publications.europa.eu/webapi/rdf/sparql"
    
    # [수정] 2024년 데이터까지 범위를 넓혀서 서버 응답을 강제로 끌어냅니다.
    query = """
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    
    SELECT DISTINCT ?work ?date ?title
    WHERE {
      ?work cdm:work_date_document ?date .
      ?work cdm:work_has_expression ?expr .
      ?expr cdm:expression_title ?title .
      ?expr cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> .
      
      # 2024년 혹은 2025년 데이터 모두 수집
      FILTER (contains(str(?date), "2024") || contains(str(?date), "2025"))
    }
    ORDER BY DESC(?date)
    LIMIT 100
    """

    file_name = 'EU_Policy_Check.csv'
    headers = {"Accept": "application/sparql-results+json"}

    print("🔍 [서버 점검] 2024-2025년 통합 데이터를 조회합니다...", flush=True)

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
                print(f"✅ [성공] {len(all_records)}건의 데이터를 찾았습니다! 파일명: {file_name}", flush=True)
                print(f"📌 샘플 데이터 날짜: {all_records[0]['date']}", flush=True)
            else:
                print("⚠️ 2024년 데이터조차 없습니다. 엔드포인트 자체를 점검해야 합니다.", flush=True)
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}", flush=True)

    except Exception as e:
        print(f"❌ 실행 오류: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_cellar_recovery()
