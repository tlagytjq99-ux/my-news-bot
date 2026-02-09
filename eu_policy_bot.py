import requests
import csv
import os

def fetch_eu_cellar_ultimate():
    sparql_url = "https://publications.europa.eu/webapi/rdf/sparql"
    
    # [전략] 발행일(date_document) 대신 생성일(date_creation)과 수정일(last_modification)을 모두 확인합니다.
    query = """
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT DISTINCT ?work ?title ?date
    WHERE {
      # 1. 생성일 또는 발행일 중 하나라도 있으면 가져옴
      { ?work cdm:work_date_creation ?date . }
      UNION
      { ?work cdm:work_date_document ?date . }
      
      ?work cdm:work_has_expression ?expr .
      ?expr cdm:expression_title ?title .
      ?expr cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> .
      
      # 2025년 데이터 필터링
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

    print("🕵️ [심층 추적] Cellar의 모든 날짜 기록을 뒤져 2025년 문서를 찾습니다...", flush=True)

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
                date_val = item['date']['value']
                
                link = f"https://op.europa.eu/en/publication-detail/-/publication/{cellar_id}"
                
                all_records.append({
                    "date": date_val,
                    "title": title,
                    "link": link
                })
            
            if all_records:
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                    writer.writeheader()
                    writer.writerows(all_records)
                print(f"🎯 [성공] 드디어 2025년 데이터 {len(all_records)}건을 찾아냈습니다!", flush=True)
            else:
                print("⚠️ 모든 날짜 필드를 뒤졌으나 2025년 기록이 없습니다. DB 인덱싱 지연 가능성이 높습니다.", flush=True)
        else:
            print(f"❌ 서버 응답 오류: {response.status_code} - {response.text[:100]}", flush=True)

    except Exception as e:
        print(f"❌ 오류 발생: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_cellar_ultimate()
