import requests
import csv

def fetch_eu_cellar_final_brute_force():
    sparql_url = "https://publications.europa.eu/webapi/rdf/sparql"
    
    # [전략] 특정 날짜 변수(work_date_document) 대신 
    # ?p ?date 구조를 써서 '날짜' 관련 모든 속성을 다 뒤집니다.
    query = """
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT DISTINCT ?work ?date ?title
    WHERE {
      ?work a cdm:work .
      # 날짜와 관련된 속성(?p)이 무엇이든 ?date에 담습니다.
      ?work ?p ?date .
      FILTER(contains(str(?p), "date"))
      
      ?work cdm:work_has_expression ?expr .
      ?expr cdm:expression_title ?title .
      ?expr cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> .
      
      # 2025년이 포함된 데이터만 필터링
      FILTER(contains(str(?date), "2025"))
    }
    ORDER BY DESC(?date)
    LIMIT 100
    """

    file_name = 'EU_Policy_2025_Final.csv'
    headers = {"Accept": "application/sparql-results+json"}

    print("⛏️ [전수 조사] 모든 날짜 관련 칸을 뒤져 2025년 데이터를 발굴합니다...", flush=True)

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
                print(f"✅ [대성공] {len(all_records)}건의 데이터를 찾아냈습니다!", flush=True)
            else:
                print("⚠️ 2025년 데이터가 아직 물리적으로 DB에 존재하지 않거나 접근이 제한되었습니다.", flush=True)
        else:
            print(f"❌ 서버 연결 실패: {response.status_code}", flush=True)

    except Exception as e:
        print(f"❌ 실행 중 오류: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_cellar_final_brute_force()
