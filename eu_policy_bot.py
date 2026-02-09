import requests
import csv
import time

def fetch_eu_final_standard():
    # [수정] 서버가 거부할 수 없는 '완벽한 인코딩'이 반영된 URL입니다.
    # catalogue=cellar와 q=2025를 가장 기본 형식으로 결합했습니다.
    base_url = "https://data.europa.eu/api/hub/search/search"
    params = {
        "q": "2025",
        "filter": "dataset",
        "facets": '{"catalog":["cellar"]}', # 필터 대신 facets 구조 사용 (400 에러 방지)
        "limit": 50,
        "sort": "modified-desc"
    }

    file_name = 'EU_Policy_2025_Full.csv'
    all_records = []
    
    print("🔥 [최후의 수단] 400 에러 방지용 정밀 URL로 재접속합니다...", flush=True)

    try:
        # headers를 추가하여 브라우저에서 접속하는 것처럼 위장합니다.
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        }
        
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            # 결과값 경로 재설정 (result -> results)
            results = data.get('result', {}).get('results', [])
            
            if results:
                for item in results:
                    title_dict = item.get('title', {})
                    title = title_dict.get('en', 'No English Title')
                    
                    # 날짜와 ID 추출
                    date_val = item.get('modified', item.get('issued', '2025-XX-XX'))
                    doc_id = item.get('id', '')
                    
                    # Cellar 공식 문서 뷰어 링크
                    link = f"https://op.europa.eu/en/publication-detail/-/publication/{doc_id}"
                    
                    all_records.append({
                        "date": date_val[:10],
                        "title": str(title).strip(),
                        "link": link
                    })
                
                # 파일 저장
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                    writer.writeheader()
                    writer.writerows(all_records)
                print(f"✅ [대성공] {len(all_records)}건의 데이터를 파일에 담았습니다!", flush=True)
            else:
                print("⚠️ 접속은 성공했으나 검색 결과가 없습니다.", flush=True)
        else:
            print(f"❌ 여전히 에러 발생 (코드: {response.status_code})", flush=True)
            print(f"서버 메시지: {response.text[:200]}", flush=True)

    except Exception as e:
        print(f"❌ 시스템 오류: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_final_standard()
