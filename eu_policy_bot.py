import requests
import csv
import os
from datetime import datetime

def fetch_eu_policy():
    # EU API 엔드포인트
    url = "https://ec.europa.eu/commission/presscorner/api/documents"
    
    # [핵심 수정] 파라미터 명칭을 EU API 표준 규격(CamelCase)으로 엄격히 맞춤
    params = {
        "language": "en",
        "documentType": "IP",  # T는 대문자여야 함
        "pageSize": "50",      # S는 대문자여야 함
        "pageNumber": "1"      # N은 대문자여야 함
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    
    print("🇪🇺 EU API 최종 정밀 타격 시작...", flush=True)
    
    try:
        # 이번에는 params 딕셔너리를 사용하지 않고 URL에 직접 붙여서 안정성을 높입니다.
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        print(f"📡 응답 상태 코드: {response.status_code}", flush=True)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            results = []
            for item in items:
                # 안전한 데이터 추출
                title = item.get('title', 'No Title')
                date = item.get('releaseDate', 'No Date')
                ref = item.get('reference', '')
                topic = item.get('fcpTopics', [{}])[0].get('name', 'N/A') if item.get('fcpTopics') else "N/A"
                
                results.append({
                    "발행일": date,
                    "제목": title,
                    "주제": topic,
                    "링크": f"https://ec.europa.eu/commission/presscorner/detail/en/{ref}"
                })
            
            if results:
                file_name = 'EU_Policy_News.csv'
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["발행일", "제목", "주제", "링크"])
                    writer.writeheader()
                    writer.writerows(results)
                print(f"✅ [대성공] EU 정책 {len(results)}건 수집 완료!", flush=True)
            else:
                print("⚪ 데이터가 비어있습니다.", flush=True)
        else:
            print(f"❌ 접속 실패: {response.status_code}", flush=True)
            print(f"🔗 확인된 URL: {response.url}", flush=True)
            
    except Exception as e:
        print(f"❌ 예외 발생: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_policy()
