import requests
import csv
import os

def fetch_eu_cellar_last_dance():
    # Cellar SPARQL 엔드포인트
    sparql_url = "https://publications.europa.eu/webapi/rdf/sparql"
    
    # [수정] 날짜 필터를 제거하고, 2025년 데이터를 '검색' 방식으로 추출합니다.
    query = """
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    
    SELECT DISTINCT ?work ?title ?date
    WHERE {
      ?work cdm:work_date_document ?date .
      ?work cdm:work_has_expression ?expr .
      ?expr cdm:expression_title ?title .
      ?expr cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> .
      
      # 2025라는 문자가 포함된 날짜는 일단 다 가져옵니다 (형식 오류 방지)
      FILTER (regex(str(?date), "2025"))
    }
    ORDER BY DESC(?date)
    LIMIT 1000
    """

    file_name = 'EU_Policy_2025_Full.csv'
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "Mozilla/5.0"
    }

    print("🎣 [무한 신뢰 모드] 2025년 키워드가 포함된 모든 데이터를 낚아올립니다...", flush=True)

    try:
        response = requests.get(sparql_url, params={'query': query}, headers=headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {}).get('bindings', [])
            
            all_records = []
            for item in results:
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
            
            if all_records:
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                    writer.writeheader()
                    writer.writerows(all_records)
                print(f"🎯 [성공] {len(all_records)}건의 데이터를 찾아냈습니다! {file_name}을 확인하세요.", flush=True)
            else:
                # 만약 여기서도 0건이면, 2025년 데이터가 아직 'ENG' 언어로 매핑되지 않았을 수 있습니다.
                print("⚠️ 여전히 결과가 0건입니다. DB에 2025년 데이터가 아직 인덱싱 중일 수 있습니다.", flush=True)
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}", flush=True)

    except Exception as e:
        print(f"❌ 오류 발생: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_cellar_last_dance()
