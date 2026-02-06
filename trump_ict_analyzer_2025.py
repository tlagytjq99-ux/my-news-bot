import requests
import csv
import time
from deep_translator import GoogleTranslator

def main():
    results = []
    page = 1
    translator = GoogleTranslator(source='en', target='ko')
    
    print("🚀 2025년 부처별 정책 전수 조사 및 번역 시작...")

    while True:
        api_url = "https://www.federalregister.gov/api/v1/documents.json"
        params = {
            "conditions[publication_date][year]": "2025",
            "conditions[type][]": ["PRESDOCU", "RULE"],
            "order": "newest",
            "per_page": 100,
            "page": page,
            "fields[]": ["title", "publication_date", "type", "agency_names", "html_url"]
        }

        try:
            response = requests.get(api_url, params=params, timeout=30)
            if response.status_code != 200: break
            
            docs = response.json().get('results', [])
            if not docs: break

            print(f"📄 {page}페이지 수집 중...")

            for doc in docs:
                title_en = doc.get('title', '')
                
                # 부처 정보 추출 (여러 부처가 공동 발행하는 경우 쉼표로 연결)
                agencies = doc.get('agency_names', [])
                agency_text = ", ".join(agencies) if agencies else "백악관/대통령"

                # 제목 번역
                try:
                    title_ko = translator.translate(title_en)
                except:
                    title_ko = "번역 오류"

                results.append({
                    "발행일": doc.get('publication_date'),
                    "발행부처": agency_text, # 부처 정보 추가
                    "문서종류": "최종규칙(Rule)" if doc.get('type') == "Rule" else "대통령문서",
                    "제목(한글)": title_ko,
                    "제목(영문)": title_en,
                    "원문링크": doc.get('html_url')
                })
            
            page += 1
            time.sleep(0.8)

        except Exception as e:
            print(f"❌ 오류: {e}")
            break

    # CSV 저장
    if results:
        file_name = 'Federal_Register_2025_By_Agency.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "발행부처", "문서종류", "제목(한글)", "제목(영문)", "원문링크"])
            writer.writeheader()
            writer.writerows(results)
        print(f"🏁 완료! '{file_name}' 파일을 확인하세요.")

if __name__ == "__main__":
    main()
