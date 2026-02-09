import requests
import xml.etree.ElementTree as ET
import csv
import os
import time
from datetime import datetime, timedelta

def main():
    # 1. 깃허브 시크릿에서 'MY_SERVICE_KEY'라는 이름으로 키를 가져옵니다.
    SERVICE_KEY = os.getenv("MY_SERVICE_KEY")
    if not SERVICE_KEY:
        print("❌ 에러: GitHub Secrets에서 'MY_SERVICE_KEY'를 설정해주세요.")
        return

    results = []
    # 2025년 전체 수집 범위 설정
    current_start = datetime(2025, 1, 1)
    final_end = datetime(2025, 12, 31)
    
    print(f"🇰🇷 정책브리핑 API 전수 수집 시작 (2025년 / 3일 단위 정밀 수집)")

    while current_start <= final_end:
        # 가이드[P.12] 준수: 검색 기간은 반드시 3일 이내여야 함 (당일 포함 3일이므로 +2일)
        current_end = current_start + timedelta(days=2)
        if current_end > final_end:
            current_end = final_end
            
        s_str = current_start.strftime("%Y%m%d")
        e_str = current_end.strftime("%Y%m%d")
        
        # 가이드 명세에 따른 요청 URL 조립
        target_url = (
            f"http://apis.data.go.kr/1371000/pressReleaseService/pressReleaseList"
            f"?serviceKey={SERVICE_KEY}"
            f"&startDate={s_str}"
            f"&endDate={e_str}"
            f"&pageNo=1"
            f"&numOfRows=500"
        )

        try:
            # 타임아웃 30초 설정 (한국 공공데이터 서버 속도 고려)
            resp = requests.get(target_url, timeout=30)
            
            if resp.status_code == 200:
                # 가이드[P.11] 에러 메시지 확인 (키 등록 대기 중일 경우)
                if "SERVICE_KEY_IS_NOT_REGISTERED" in resp.text:
                    print(f"📡 {s_str} ~ {e_str} ❌ 서버 키 미등록 상태 (발급 후 1시간 정도 소요됩니다)")
                    break
                
                # 데이터가 정상적으로 들어온 경우
                if "NewsItem" in resp.text:
                    root = ET.fromstring(resp.content)
                    items = root.findall('.//NewsItem')
                    for item in items:
                        results.append({
                            "발행일": item.findtext('ApproveDate'), # 승인일
                            "부처": item.findtext('MinisterCode'), # 부처명
                            "제목": item.findtext('Title'),       # 제목
                            "링크": item.findtext('OriginalUrl')   # 원문 주소
                        })
                    print(f"📡 {s_str} ~ {e_str} ✅ {len(items)}건 완료")
                else:
                    print(f"📡 {s_str} ~ {e_str} ⚪ 해당 기간 데이터 없음")
            else:
                print(f"📡 {s_str} ~ {e_str} ❌ HTTP 에러({resp.status_code})")
                
        except Exception as e:
            print(f"❌ 접속 중 오류 발생: {e}")
        
        # 다음 3일 구간으로 이동 (예: 1~3일 다음은 4~6일)
        current_start = current_end + timedelta(days=1)
        # 가이드의 권고대로 서버 부하 방지를 위해 아주 짧게 쉽니다.
        time.sleep(0.3) 

    # 2. 수집된 결과 저장
    if results:
        file_name = 'Korea_Policy_2025_All.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "부처", "제목", "링크"])
            writer.writeheader()
            writer.writerows(results)
        print(f"\n🎉 [수집 완료] 총 {len(results)}건의 데이터를 '{file_name}'에 저장했습니다!")
    else:
        print("\n⚠️ 수집된 데이터가 없습니다. 시크릿 설정이나 키 활성화 시간을 확인해주세요.")

if __name__ == "__main__":
    main()
