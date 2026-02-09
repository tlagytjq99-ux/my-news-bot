import requests
import csv
import os
from datetime import datetime

def fetch_eu_policy():
    # EU Press Corner API 정석 주소
    url = "https://ec.europa.eu/commission/presscorner/api/documents"
    
    # 400 에러 방지를 위해 파라미터 구성을 가장 표준적인 형태로 수정했습니다.
    params = {
        "language": "en",
        "documentType": "IP", # IP: Press Release
        "pagesize": "50",     # 소문자로 변경 시도 및 문자열 처리
        "pagenumber": "1"
    }
    
    # 서버가 '진짜 브라우저'에서 온 요청으로 인식하도록 헤더를 추가합니다. (중요)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print("🇪🇺 EU 정책 보도자료 수집 재시도 중...", flush=True)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        # 로그 확인용 (무슨 데이터가 오는지 찍어봅니다)
        print(f"📡 응답 상태 코드: {response.status_code}", flush=True)
        
        if response.status_code == 200:
            data = response.json()
            # EU API 구조에 따라 'items' 또는 'rows' 등으로 올 수 있으므로 안전하게 추출
            items = data.get('items', [])
            
            results = []
            for item in items:
                results.append({
                    "발행일": item.get('releaseDate'),
                    "제목": item.get('title'),
                    "주제": item.get('fcpTopics')[0].get('name') if item.get('fcpTopics') else "N/A",
                    "링크": f"https://ec.europa.eu/commission/presscorner/detail/en/{item.get('reference')}"
                })
            
            if results:
                file_name = 'EU_Policy_News.csv'
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["발행일", "제목", "주제", "링크"])
                    writer.writeheader()
                    writer.writerows(results)
                print(f"✅ 수집 성공! 총 {len(results)}건 저장 완료.", flush=True)
            else:
                print("⚪ 수집된 데이터가 없습니다. (파라미터 확인 필요)", flush=True)
        else:
            print(f"❌ 접속 실패: {response.status_code}", flush=True)
            print(f"📡 서버 메시지: {response.text[:200]}", flush=True) # 에러 내용 일부 출력
            
    except Exception as e:
        print(f"❌ 에러 발생: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_policy()
