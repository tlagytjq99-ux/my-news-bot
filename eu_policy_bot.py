import requests
import csv
import time

def fetch_eu_real_policy_2025():
    api_url = "https://data.europa.eu/api/hub/search/search"
    
    # [핵심 변경] filters에 'publisher'와 'catalogue'를 엄격하게 제한합니다.
    # 'publications-office-of-the-european-union' 카탈로그가 정책 보고서의 핵심입니다.
    params = {
        "filters": "catalogue:publications-office-of-the-european-union", # 정책 간행물 전용
        "dataScope": "eu",
        "dateType": "issued",
        "minDate": "2025-01-01T00:00:00.000Z",
        "maxDate": "2025-12-31T23:59:59.000Z",
        "includes": "id,title.en,issued,description.en",
        "limit": 50,
        "page": 0,
        "sort": "issued-desc"
    }

    file_name = 'EU_Policy_2025_Full.csv'
    all_records = []
    
    print("🏛️ [정책 특화 모드] EU 본부 정책 간행물만 정밀 수집합니다...", flush=True)

    try:
        while True:
            response = requests.get(api_url, params=params, timeout=30)
            if response.status_code != 200: break
            
            data = response.json()
            results = data.get('result', {}).get('results', [])
            if not results: break
            
            for item in results:
                title_dict = item.get('title', {})
                # 영어 제목이 있는 것만 골라내어 노이즈 제거
                title = title_dict.get('en')
                if not title: continue 
                
                issued_date = item.get('issued', '2025-XX-XX')
                doc_id = item.get('id', '')
                # 간행물 뷰어 링크로 직행
                link = f"https://op.europa.eu/en/publication-detail/-/publication/{doc_id}"
                
                all_records.append({
                    "date": issued_date[:10],
                    "title": title.strip(),
                    "link": link
                })
            
            print(f"✅ {params['page'] + 1}페이지 분석 완료... (현재 {len(all_records)}건)", flush=True)
            
            params['page'] += 1
            if params['page'] > 20: break # 일단 1,000건 정도만 먼저 확인
            time.sleep(0.2)

    except Exception as e:
        print(f"❌ 오류: {e}", flush=True)

    if all_records:
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(all_records)
        print(f"💾 저장 완료! 이제 파일에서 '진짜 정책' 제목들을 확인해 보세요.", flush=True)

if __name__ == "__main__":
    fetch_eu_real_policy_2025()
