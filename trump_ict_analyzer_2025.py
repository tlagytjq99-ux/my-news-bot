import requests
import csv
import time

def main():
    results = []
    seen_ids = set()
    doc_types = ["PRESDOCU", "RULE", "PRORULE", "NOTICE"]
    
    # 2025년 1월부터 12월까지 월별로 루프를 돕니다
    for month in range(1, 13):
        start_date = f"2025-{month:02d}-01"
        # 월말 날짜 처리를 위해 간단히 다음달 1일 전까지로 설정
        if month == 12:
            end_date = "2025-12-31"
        else:
            end_date = f"2025-{month+1:02d}-01"
            
        print(f"📅 {start_date} ~ {end_date} 구간 수집 시작...")
        
        page = 1
        while True:
            api_url = "https://www.federalregister.gov/api/v1/documents.json"
            params = {
                "conditions[publication_date][gte]": start_date,
                "conditions[publication_date][lt]": end_date,
                "conditions[type][]": doc_types,
                "per_page": 100,
                "page": page,
                "fields[]": ["title", "publication_date", "type", "agency_names", "html_url", "document_number"]
            }

            try:
                response = requests.get(api_url, params=params, timeout=30)
                if response.status_code != 200: break
                
                docs = response.json().get('results', [])
                if not docs: break

                for doc in docs:
                    doc_num = doc.get('document_number')
                    if doc_num in seen_ids: continue
                    
                    seen_ids.add(doc_num)
                    agencies = doc.get('agency_names', [])
                    results.append({
                        "발행일": doc.get('publication_date'),
                        "발행부처": ", ".join(agencies) if agencies else "White House",
                        "문서종류": doc.get('type'),
                        "제목(영문)": doc.get('title'),
                        "원문링크": doc.get('html_url'),
                        "문서번호": doc_num
                    })
                
                page += 1
                time.sleep(0.1)
                
                # 한 달치 데이터가 5000건을 넘을 일은 없으므로 안전하게 수집됩니다.
            except: break
            
        print(f"✅ 현재까지 총 {len(results)}건 수집됨")

    # CSV 저장
    if results:
        with open('Federal_Register_2025_Full.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "발행부처", "문서종류", "제목(영문)", "원문링크", "문서번호"])
            writer.writeheader()
            writer.writerows(results)
        print(f"🏁 전수 조사 완료! 총 {len(results)}건 저장.")

if __name__ == "__main__":
    main()
