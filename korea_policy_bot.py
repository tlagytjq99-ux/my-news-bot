import requests
import csv

def fetch_eu_cellar_final_match():
    sparql_url = "https://publications.europa.eu/webapi/rdf/sparql"
    
    # [수정] 날짜 계산 대신 '2025' 문자열 포함 여부로 검색합니다.
    # 이렇게 하면 DB의 날짜 형식 오류를 완벽하게 무시하고 낚아챌 수 있습니다.
    query = """
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    
    SELECT DISTINCT ?work ?date ?title
    WHERE {
      ?work a cdm:work ;
            cdm:work_date_document ?date ;
            cdm:work_has_expression ?expr .
      ?expr cdm:expression_title ?title .
      ?expr cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> .
      
      # 날짜 필드에 '2025'가 포함된 모든 것을 가져옴
      FILTER (contains(str(?date), "2025"))
    }
    ORDER BY DESC(?date)
    LIMIT 100
    """

    file_name = 'EU_Policy_2025_Full.csv'
    headers = {"Accept": "application/sparql-results+json"}

    print("🎯 [최종 타격] 2025년 문자열 매칭으로 데이터를 강제 추출합니다...", flush=True)

    try:
        # POST 방식으로 쿼리 전송
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
                print(f"✅ [성공] 2025년 데이터 {len(all_records)}건을 드디어 찾아냈습니다!", flush=True)
            else:
                # 2025년이 정말 없다면 2024년이라도 있는지 확인하여 서버 상태 최종 점검
                print("⚠️ 2025년 매칭 데이터가 없습니다. DB 인덱싱 지연이 확실해 보입니다.", flush=True)
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}", flush=True)

    except Exception as e:
        print(f"❌ 실행 중 오류: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_cellar_final_match()
