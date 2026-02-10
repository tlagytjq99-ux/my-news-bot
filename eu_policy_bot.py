import requests
import csv

def fetch_eu_2023_api_fixed():
    # EU Cellar SPARQL 공식 엔드포인트
    sparql_url = "https://publications.europa.eu/webapi/rdf/sparql"
    
    # [수정 포인트] 
    # 1. cdm:work_date_document를 텍스트로 비교하여 인식률 향상
    # 2. 복잡한 title 경로를 cdm:expression_title로 단순화
    query = """
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

    SELECT DISTINCT ?work ?date ?title
    WHERE {
      ?work a cdm:work .
      ?work cdm:work_date_document ?date .
      
      # 날짜 형식 오류를 방지하기 위해 문자열로 2023 확인
      FILTER (contains(str(?date), "2023"))
      
      ?work cdm:work_has_expression ?expr .
      ?expr cdm:expression_title ?title .
      ?expr cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> .
    }
    ORDER BY DESC(?date)
    LIMIT 100
    """

    file_name = 'EU_Policy_2023_Archive.csv'
    headers = {"Accept": "application/sparql-results+json"}

    print("⛏️ [API 재시도] 2023년 데이터를 가장 확실한 경로로 재추출합니다...", flush=True)

    try:
        # 쿼리를 전송합니다.
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
                
                all_records.append({"date": date, "title": title, "link": link})

            if all_records:
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                    writer.writeheader()
                    writer.writerows(all_records)
                print(f"✅ [성공] 2023년 데이터 {len(all_records)}건을 API로 수집했습니다!", flush=True)
                print(f"📌 첫 번째 데이터: {all_records[0]['title']}", flush=True)
            else:
                print("⚠️ 2023년 데이터가 여전히 잡히지 않습니다. 필드명을 '작성일'로 변경해 보겠습니다.", flush=True)
        else:
            print(f"❌ API 서버 응답 오류: {response.status_code}", flush=True)

    except Exception as e:
        print(f"❌ 실행 중 오류: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_2023_api_fixed()
