import requests
import xml.etree.ElementTree as ET
import csv
import time
from datetime import datetime, timedelta

def main():
    # 1. 대표님이 주신 키를 제가 직접 넣었습니다. 
    # 특수문자 처리를 위해 unquote 없이 원본 그대로 사용합니다.
    SERVICE_KEY = "R+veVpMchPZJob94a/x0z5KlwTOuB+OOlK2GhFGigbo7p/fupVm7zAY14QNDhXHg8mSIEyBJOF1x/1VIvJAwSQ=="
    
    results = []
    curr = datetime(2025, 1, 1)
    end = datetime(2025, 12, 31)
    
    print("🇰🇷 대한민국 정책브리핑 2025 수집 시작 (인증 우회 방식)...")

    while curr <= end:
        batch_end = curr + timedelta(days=2)
        if batch_end > end: batch_end = end
        
        s_str = curr.strftime("%Y%m%d")
        e_str = batch_end.strftime("%Y%m%d")
        
        # 2. [필살기] URL에 키와 날짜를 수동으로 조합합니다. 
        # requests가 키를 인코딩하지 못하도록 문자열을 통째로 만듭니다.
        target_url = (
            f"http://apis.data.go.kr/1371000/pressReleaseService/pressReleaseList"
            f"?serviceKey={SERVICE_KEY}"
            f"&startDate={s_str}"
            f"&endDate={e_str}"
            f"&pageNo=1"
            f"&numOfRows=500"
        )
        
        print(f"📡 구간: {s_str} ~ {e_str}", end=" ", flush=True)

        try:
            # params 인자를 쓰지 않고 완성된 URL만 넣어서 호출합니다.
            resp = requests.get(target_url, timeout=30)
            
            # 응답 본문에 에러 메시지가 있는지 확인
            if "SERVICE_KEY_IS_NOT_REGISTERED_ERROR" in resp.text:
                print("❌ 에러: 공공데이터 포털에 키가 아직 등록 안 됨 (1시간 대기 필요)")
                break
            
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                items = root.findall('.//NewsItem')
                for item in items:
                    results.append({
                        "발행일": item.findtext('ApproveDate'),
                        "부처": item.findtext('MinisterCode'),
                        "제목": item.findtext('Title'),
                        "링크": item.findtext('OriginalUrl')
                    })
                print(f"✅ ({len(items)}건)")
            elif resp.status_code == 401:
                print("❌ 여전히 401 에러... (키 활성화 대기 필요)")
                break
            else:
                print(f"❌ 응답 실패 ({resp.status_code})")
                break
                
        except Exception as e:
            print(f"❌ 오류: {e}")
            break
        
        curr += timedelta(days=3)
        time.sleep(0.5)

    if results:
        with open('Korea_Policy_2025.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "부처", "제목", "링크"])
            writer.writeheader()
            writer.writerows(results)
        print(f"\n🏁 완료! 총 {len(results)}건 저장.")

if __name__ == "__main__":
    main()
