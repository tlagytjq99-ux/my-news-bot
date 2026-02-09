import requests
import csv
import time
import sys
from datetime import datetime

def fetch_eu_policy():
    # EU Press Corner API (기계용 주소)
    url = "https://ec.europa.eu/commission/presscorner/api/documents"
    
    # 파라미터 설정 (영어, 보도자료 'IP' 타입, 50개씩)
    params = {
        "language": "en",
        "documentType": "IP", 
        "pageSize": 50,
        "pageNumber": 1
    }
    
    print("🇪🇺 EU 정책 보도자료 수집 시작...", flush=True)
    
    try:
        # API 호출
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            results = []
            for item in items:
                # 데이터 추출 및 정리
                results.append({
                    "발행일": item.get('releaseDate'),
                    "제목": item.get('title'),
                    "주제": item.get('fcpTopics')[0].get('name') if item.get('fcpTopics') else "N/A",
                    "링크": f"https://ec.europa.eu/commission/presscorner/detail/en/{item.get('reference')}"
                })
            
            # CSV 파일로 저장
            if results:
                file_name = 'EU_Policy_News.csv'
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["발행일", "제목", "주제", "링크"])
                    writer.writeheader()
                    writer.writerows(results)
                print(f"✅ 수집 성공! 총 {len(results)}건의 EU 정책을 '{file_name}'에 저장했습니다.", flush=True)
            else:
                print("⚪ 수집된 데이터가 없습니다.", flush=True)
        else:
            print(f"❌ 접속 실패 (상태 코드: {response.status_code})", flush=True)
            
    except Exception as e:
        print(f"❌ 에러 발생: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_policy()
