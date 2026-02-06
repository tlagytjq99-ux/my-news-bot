import requests
import csv
import time

def main():
    results = []
    seen_ids = set() # 중복 체크용 저장소
    page = 1
    doc_types = ["PRESDOCU", "RULE", "PRORULE", "NOTICE"]
    
    print("🚀 2025년 관보 정밀 수집 시작 (중복 차단 모드)")

    while True:
        api_url = "https://www.federalregister.gov/api/v1/documents.json"
        params = {
            "conditions[publication_date][year]": "2025",
            "conditions[type][]": doc_types,
            "order": "newest",
            "per_page": 100,
            "page": page,
            "fields[]": ["title", "publication_date", "type", "agency_names", "html_url", "document_number"]
        }

        try:
            response = requests.get(api_url, params=params, timeout=30)
            if response.status_code != 200: break
            
            data = response.json()
            docs = data.get('results', [])
            
            # [중요] 데이터가 아예 없거나, 이번 페이지의 첫 데이터가 이미 수집한 거라면 종료
            if not docs or docs[0].get('document_number') in seen_ids:
                print(f"🏁 {page}페이지에서 수집을 마칩니다. (데이터 끝 도달)")
                break

            for doc in docs:
                doc_num = doc.get('document_number')
                if doc_num in seen_ids: continue # 혹시 모를 중복 건너뛰기
                
                seen_ids.add(doc_num)
                agencies = doc.get('agency_names', [])
                agency_text = ", ".join(agencies) if agencies else "White House"

                results.append({
                    "발행일": doc.get('publication_date'),
                    "발행부처": agency_text,
                    "문서종류": doc.get('type'),
                    "제목(영문)": doc.get('title'),
                    "원문링크": doc.get('html_url'),
                    "문서번호": doc_num
                })
            
            print(f"📥 {page}페이지 완료 (실제 누적: {len(results)}건)")
            page += 1
            if page > 500: break # 안전장치: 5만 건 이상은 2025년에 존재할 수 없음

        except Exception as e:
            print(f"❌ 오류: {e}")
            break

    # 저장 (utf-8-sig로 해야 한글/영문 엑셀에서 안 깨짐)
    if results:
        with open('Federal_Register_2025_Final.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "발행부처", "문서종류", "제목(영문)", "원문링크", "문서번호"])
            writer.writeheader()
            writer.writerows(results)
        print(f"✅ 총 {len(results)}건의 중복 없는 데이터를 저장했습니다.")

if __name__ == "__main__":
    main()
