import requests
import csv
import time

def main():
    results = []
    page = 1
    
    # 수집할 문서 유형 정의
    # PRESDOCU: 대통령 문서, RULE: 최종 규칙, PRORULE: 규칙 제정 예고, NOTICE: 일반 공고
    doc_types = ["PRESDOCU", "RULE", "PRORULE", "NOTICE"]
    
    print(f"🚀 2025년 전수 조사 시작 (대상: {', '.join(doc_types)})")
    print("⚡ 번역 단계를 제외하여 수집 속도가 대폭 향상되었습니다.")

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
            if response.status_code != 200:
                print(f"⚠️ {page}페이지 호출 실패 (코드: {response.status_code})")
                break
            
            data = response.json()
            docs = data.get('results', [])
            if not docs:
                break

            print(f"📥 {page}페이지 수집 중... (현재 누적: {len(results) + len(docs)}건)")

            for doc in docs:
                agencies = doc.get('agency_names', [])
                agency_text = ", ".join(agencies) if agencies else "White House / Presidential"

                # 문서 유형 한글 매핑 (데이터 정리용)
                type_map = {
                    "Rule": "최종 규칙(Rule)",
                    "Proposed Rule": "규칙 제정 예고(Proposed Rule)",
                    "Notice": "공고(Notice)",
                    "Presidential Document": "대통령 문서"
                }
                doc_type_en = doc.get('type', '')
                doc_type_ko = type_map.get(doc_type_en, doc_type_en)

                results.append({
                    "발행일": doc.get('publication_date'),
                    "발행부처": agency_text,
                    "문서종류": doc_type_ko,
                    "제목(영문)": doc.get('title'),
                    "원문링크": doc.get('html_url'),
                    "문서번호": doc.get('document_number')
                })
            
            page += 1
            # 번역을 안 하므로 대기 시간을 줄여도 안전합니다 (0.2초)
            time.sleep(0.2) 

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            break

    # CSV 저장
    if results:
        file_name = 'Federal_Register_2025_Full_Scraping.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "발행부처", "문서종류", "제목(영문)", "원문링크", "문서번호"])
            writer.writeheader()
            writer.writerows(results)
        print(f"\n🏁 전수 조사 완료! 총 {len(results)}건의 데이터를 '{file_name}'에 저장했습니다.")
    else:
        print("\n⚠️ 수집된 데이터가 없습니다.")

if __name__ == "__main__":
    main()
