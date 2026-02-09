import requests
import os

def download_eu_policy_csv():
    # [핵심] 2025년 Cellar 간행물 검색 결과의 'CSV 내보내기' 직접 링크입니다.
    # API가 아니라 완성된 결과 파일을 요청하는 방식이라 에러 확률이 극히 낮습니다.
    download_url = "https://data.europa.eu/api/hub/search/search?q=2025&filters=catalogue:cellar&limit=1000&format=csv"
    
    file_name = 'EU_Policy_2025_Full.csv'
    
    print(f"📥 [다운로드 시작] 2025년 정책 리스트를 파일로 직접 수령합니다...", flush=True)

    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/csv"
        }
        
        response = requests.get(download_url, headers=headers, timeout=60)
        
        if response.status_code == 200:
            # 받아온 내용을 그대로 파일로 저장
            with open(file_name, 'wb') as f:
                f.write(response.content)
            
            # 파일 크기 확인 (데이터가 있는지 검증)
            file_size = os.path.getsize(file_name)
            if file_size > 500: # 헤더 외에 데이터가 더 있다면 성공
                print(f"✅ [성공] {file_name} 저장 완료! (크기: {file_size} bytes)", flush=True)
            else:
                print("⚠️ 파일은 생성되었으나 내용이 비어있을 수 있습니다. 확인이 필요합니다.", flush=True)
        else:
            print(f"❌ 다운로드 실패 (상태 코드: {response.status_code})", flush=True)

    except Exception as e:
        print(f"❌ 오류 발생: {e}", flush=True)

if __name__ == "__main__":
    download_eu_policy_csv()
