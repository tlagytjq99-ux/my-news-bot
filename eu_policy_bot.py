import requests
import csv

def fetch_eu_raw_api_and_filter():
    sparql_url = "https://publications.europa.eu/webapi/rdf/sparql"
    
    # [초단순 쿼리] 
    # 필터를 모두 제거했습니다. 그냥 최신순으로 50개만 가져옵니다.
    query = """
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

    SELECT DISTINCT ?work ?date ?title
    WHERE {
      ?work a cdm:work .
      ?work cdm:work_date_document ?date .
      ?work cdm:work_has_expression ?expr .
      ?expr cdm:expression_title ?title .
      ?expr cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> .
    }
    ORDER BY DESC(?date)
    LIMIT 50
    """

    file_name = 'EU_Policy_Archive_Fixed.csv'
    headers = {"Accept": "application/sparql-results+json"}

    print("🎣 [투망식 수집] DB에서 최신 데이터 50개를 무조건 긁어옵니다...", flush=True)

    try:
        response = requests.post(sparql_url, data={'query': query}, headers=headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            bindings = data.get('results', {}).get('bindings', [])
            
            all_records = []
            print(f"📡 DB로부터 {len(bindings)}개의 응답을 받았습니다.", flush=True)

            for item in bindings:
                work_uri = item['work']['value']
                uuid = work_uri.split('/')[-1]
                title = item['title']['value']
                date = item['date']['value']
                link = f"https://op.europa.eu/en/publication-detail/-/publication/{uuid}"
                
                # 수집된 데이터의 날짜가 언제인지 상관없이 일단 담습니다.
                all_records.append({"date": date, "title": title, "link": link})

            if all_records:
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                    writer.writeheader()
                    writer.writerows(all_records)
                print(f"✅ [대성공] {len(all_records)}건의 데이터를 파일에 저장했습니다!", flush=True)
                print(f"📅 확인된 날짜 범위: {all_records[-1]['date']} ~ {all_records[0]['date']}", flush=True)
                print(f"📌 첫 번째 제목: {all_records[0]['title']}", flush=True)
            else:
                print("⚠️ 데이터는 가져왔으나 형식이 맞지 않습니다.", flush=True)
        else:
            print(f"❌ API 서버 응답 오류: {response.status_code}", flush=True)

    except Exception as e:
        print(f"❌ 실행 중 오류: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_raw_api_and_filter()
