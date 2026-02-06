import requests
import csv
import time
from deep_translator import GoogleTranslator

def main():
    # 데이터 저장을 위한 리스트
    results = []
    page = 1
    translator = GoogleTranslator(source='en', target='ko')
    
    print("🚀 2025년 트럼프 정부 대통령 문서 '전수 조사' 및 번역 시작...")

    while True:
        api_url = "https://www.federalregister.gov/api/v1/documents.json"
        params = {
            "conditions[publication_date][year]": "2025",
            "conditions[presidential_document_type][]": ["executive_order", "determination", "memorandum", "proclamation"],
            "conditions[president]": "donald-trump",
            "order": "newest",
            "per_page": 100,
            "page": page,
            "fields[]": ["title", "publication_date", "html_url", "type", "agency_names"]
        }

        try:
            response = requests.get(api_url, params=params, timeout=30)
            if response.status_code != 200: break
            
            data = response.json()
            docs = data.get('results', [])
            if not docs: break

            print(f"📄 {page}페이지 수집 중... ({len(docs)}건)")

            for doc in docs:
                title_en = doc.get('title', '')
                
                # 제목 한글 번역 (전수 조사이므로 모든 제목 번역)
                try:
                    title_ko = translator.translate(title_en)
                except:
                    title_ko = "번역 중 오류 발생"

                # 키워드 필터 없이 모든 문서 저장
                results.append({
                    "발행일": doc.get('publication_date'),
                    "문서종류": doc.get('type'),
                    "관련부처": ", ".join(doc.get('agency_names', [])),
                    "제목(한글)": title_ko,
                    "제목(영문)": title_en,
                    "원문링크": doc.get('html_url')
                })
                # 진행 상황 출력
                print(f"   - {doc.get('publication_date')}: {title_ko[:40]}...")
            
            page += 1
            time.sleep(1) # 번역 API 및 서버 부하 방지

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            break

    # 3. CSV 저장
    if results:
        file_name = 'Trump_All_Policies_2025_Full_List.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "문서종류", "관련부처", "제목(한글)", "제목(영문)", "원문링크"])
            writer.writeheader()
            writer.writerows(results)
        print(f"🏁 전수 조사 완료! 총 {len(results)}건의 정책이 '{file_name}'에 저장되었습니다.")

if __name__ == "__main__":
    main()
