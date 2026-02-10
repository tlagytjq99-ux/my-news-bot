import requests
import csv

def fetch_eu_2023_via_api():
    # EU Cellar SPARQL 공식 엔드포인트
    sparql_url = "https://publications.europa.eu/webapi/rdf/sparql"
    
    # [쿼리 전략] 2023년에 발행된(date_document) 영어(ENG) 문서 중 'work' 타입만 추출
    query = """
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT DISTINCT ?work ?date ?title
    WHERE {
      ?work a cdm:work .
      ?work cdm:work_date_document ?date .
      
      # 2023년 데이터로 한정
      FILTER(str(?date) >= "2023-01-01" && str(?date) <= "2023-12-31")
      
      ?work cdm:work_has_expression ?expr .
      ?expr cdm:expression_title ?title .
      ?expr cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> .
    }
    ORDER BY DESC(?date)
    LIMIT 100
    """

    file_name = 'EU_Policy_2023_Archive.csv'
    headers = {"Accept": "application/sparql-results+json"}

    print("⛏️ [API 호출] 2023년 EU 공식 DB에서 정책 데이터를 추출합니다...", flush=True)

    try:
        response = requests.post(sparql_url, data={'query': query}, headers=headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            bindings = data.get('results', {}).get('bindings', [])
            
            all_records = []
            for item in bindings:
                work_uri = item['work']['value']
                uuid = work_uri.split('/')[-1] # 고유 식별자 추출
                title = item['title']['value']
                date = item['date']['value']
                # 상세 페이지 링크 생성
                link = f"https://op.europa.eu/en/publication-detail/-/publication/{uuid}"
                
                all_records.append({"date": date, "title": title, "link": link})

            if all_records:
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                    writer.writeheader()
                    writer.writerows(all_records)
                print(f"✅ [성공] 2023년 데이터 {len(all_records)}건을 확보했습니다!", flush=True)
                print(f"📑 샘플: {all_records[0]['title']}", flush=True)
            else:
                print("⚠️ 2023년 조건에 맞는 데이터가 API상에 존재하지 않습니다.", flush=True)
        else:
            print(f"❌ API 서버 응답 오류: {response.status_code}", flush=True)

    except Exception as e:
        print(f"❌ 실행 중 오류: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_2023_via_api()
