import requests
import xml.etree.ElementTree as ET
import csv
import os
import time
from urllib.parse import unquote # 해독을 위한 도구
from datetime import datetime, timedelta

def main():
    # 1. 시크릿에서 키 가져오기
    raw_key = os.getenv("MY_SERVICE_KEY")
    if not raw_key:
        print("❌ 에러: MY_SERVICE_KEY를 찾을 수 없습니다.")
        return

    # [핵심] 깃허브가 멋대로 인코딩한 키를 '원본(Decoded)' 상태로 강제 복구합니다.
    # 이렇게 해야 서버가 중복 인코딩으로 인식하지 않습니다.
    SERVICE_KEY = unquote(raw_key)
    
    results = []
    start_date = datetime(2025, 1, 1)
    end_of_year = datetime(2025, 12, 31)
    
    print("🇰🇷 대한민국 정책브리핑(API) 전수 수집 시작 (인코딩 복구 모드)")

    current_start = start_date
    while current_start <= end_of_year:
        current_end = current_start + timedelta(days=14)
        if current_end > end_of_year:
            current_end = end_of_year
            
        s_str = current_start.strftime("%Y%m%d")
        e_str = current_end.strftime("%Y%m%d")
        
        # 2. 가이드라인에 맞춘 필수 파라미터 구성
        params = {
            'serviceKey': SERVICE_KEY,
            'startDate': s_str,
            'endDate': e_str,
            'pageNo': '1',
            'numOfRows': '500'
        }

        try:
            # 이번에는 주소에 직접 박지 않고, params를 사용하되 
            # requests가 키를 멋대로 건드리지 못하게 조치합니다.
            base_url = "http://apis.data.go.kr/1371000/pressReleaseService/pressReleaseList"
            resp = requests.get(base_url, params=params, timeout=45)
            
            if resp.status_code == 200:
                # 응답 본문에 401 관련 메시지가 있는지 체크
                if "Unauthorized" in resp.text or "SERVICE_KEY_IS_NOT_REGISTERED" in resp.text:
                    print(f"📡 {s_str} ~ {e_str} ❌ 인증 오류(401)")
                    print(f"DEBUG: 키 첫 10글자 -> {SERVICE_KEY[:10]}")
                    break
                
                if "NewsItem" in resp.text:
                    root = ET.fromstring(resp.content)
                    items = root.findall('.//NewsItem')
                    for item in items:
                        results.append({
                            "발행일": item.findtext('ApproveDate'),
                            "부처": item.findtext('MinisterCode'),
                            "제목": item.findtext('Title'),
                            "링크": item.findtext('OriginalUrl')
                        })
                    print(f"📡 {s_str} ~ {e_str} ✅ {len(items)}건 완료")
                else:
                    print(f"📡 {s_str} ~ {e_str} ⚪ 데이터 없음")
            else:
                print(f"📡 {s_str} ~ {e_str} ❌ 서버 에러({resp.status_code})")
                
        except Exception as e:
            print(f"❌ 에러 발생: {e}")
        
        current_start = current_end + timedelta(days=1)
        time.sleep(0.5)

    # 3. 저장
    file_name = 'Korea_Policy_2025.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["발행일", "부처", "제목", "링크"])
        writer.writeheader()
        if results:
            writer.writerows(results)
            print(f"\n🏁 수집 성공! 총 {len(results)}건 저장 완료.")
        else:
            print("\n⚠️ 최종 수집된 데이터가 없습니다.")

if __name__ == "__main__":
    main()
