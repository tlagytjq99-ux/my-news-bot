import requests
import csv
import time

def fetch_us_data():
    results = []
    # 중복 수집을 방지하기 위한 장치
    seen_documents = set()
    
    # 관심 있는 문서 유형: 대통령 문서, 규칙, 규칙예고, 공고
    doc_types = ["PRESDOCU", "RULE", "PRORULE", "NOTICE"]
    
    print("🇺🇸 [미국 관보 2025] 데이터 전수 조사 재시작...")

    # 1월부터 12월까지 순차적으로 접근 (API 부하 분산)
    for month in range(1, 13):
        start_date = f"2025-{month:02d}-01"
        if month == 12:
            end_date = "2025-12-31"
        else:
            end_date = f"2025-{month+1:02d}-01"
            
        print(f"\n📅 분석 구간: {start_date} ~ {end_date}")
        
        page = 1
        while True:
            api_url = "https://www.federalregister.gov/api/v1/documents.json"
            params = {
                "conditions[publication_date][gte]": start_date,
                "conditions[publication_date][lt]": end_date,
                "conditions[type][]": doc_types,
                "per_page": 100,  # 한 번에 100개씩 안전하게
                "page": page,
                "fields[]": ["title", "publication_date", "type", "agency_names", "html_url", "document_number"]
            }

            try:
                # 15초 안에 응답 없으면 다시 시도하도록 설정
                response = requests.get(api_url, params=params, timeout=15)
                
                if response.status_code != 200:
                    print(f"⚠️ {page}페이지 응답 오류 (코드: {response.status_code})")
                    break
                
                data = response.json()
                docs = data.get('results', [])
                
                if not docs: # 해당 월의 데이터가 끝났으면 다음 달로
                    break

                # 진행 상황 실시간 출력 (대표님이 로그에서 보실 내용)
                print(f"📥 {month}월 수집 중... ({page}페이지 / 누적: {len(results)}건)", end="\r", flush=True)

                for doc in docs:
                    doc_id = doc.get('document_number')
                    if doc_id not in seen_documents:
                        seen_documents.add(doc_id)
                        agencies = doc.get('agency_names', [])
                        results.append({
                            "발행일": doc.get('publication_date'),
                            "부처": ", ".join(agencies) if agencies else "White House",
                            "종류": doc.get('type'),
                            "제목": doc.get('title'),
                            "원문링크": doc.get('html_url')
                        })
                
                page += 1
                time.sleep(0.2) # 미국 서버가 화내지 않게 잠깐씩 쉬어줌
                
            except Exception as e:
                print(f"\n❌ 통신 중 에러 발생: {e}")
                time.sleep(5) # 에러 시 잠시 대기 후 다음 단계 시도
                break
                
    # 파일 저장
    if results:
        file_name = 'Federal_Register_2025_Master.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "부처", "종류", "제목", "원문링크"])
            writer.writeheader()
            writer.writerows(results)
        print(f"\n\n✅ 수집 완료! 총 {len(results)}건의 데이터를 '{file_name}'에 담았습니다.")

if __name__ == "__main__":
    fetch_us_data()
