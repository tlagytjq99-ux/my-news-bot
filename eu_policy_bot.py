import requests
import csv
import os
from datetime import datetime

def fetch_eu_policy():
    # EU API 엔드포인트
    url = "https://ec.europa.eu/commission/presscorner/api/documents"
    
    # 400 에러의 주범은 보통 대문자가 섞인 파라미터명입니다.
    # 모든 키(key)를 소문자로, 값(value)은 API가 기대하는 문자열로 정확히 맞췄습니다.
    params = {
        "language": "en",
        "documenttype": "IP",  # 보도자료 코드 (소문자 key)
        "pagesize": "50",      # 문자열로 전달
        "pagenumber": "1"
    }
    
    # 브라우저인 척 위장하는 헤더
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Cache-Control": "no-cache"
    }
    
    print("🇪🇺 EU API 정밀 타격 수집 시작...", flush=True)
    
    try:
        # 주소 뒤에 파라미터를 붙여서 직접 호출하는 방식과 동일하게 수행
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        print(f"📡 응답 상태 코드: {response.status_code}", flush=True)
        
        if response.status_code == 200:
            data = response.json()
            # EU API 응답 구조: 보통 'items' 리스트 안에 데이터가 담깁니다.
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
                print(f"✅ [대성공] EU 정책 {len(results)}건 수집 완료!", flush=True)
            else:
                print("⚪ 데이터가 비어있습니다. API 응답 구조를 재확인해야 합니다.", flush=True)
                print(f"📡 서버 응답 샘플: {str(data)[:200]}", flush=True)
        else:
            print(f"❌ 접속 실패: {response.status_code}", flush=True)
            # 400 에러 시 서버가 보낸 원인 파악을 위해 URL 출력
            print(f"🔗 요청한 URL 확인: {response.url}", flush=True)
            
    except Exception as e:
        print(f"❌ 예외 발생: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_policy()
