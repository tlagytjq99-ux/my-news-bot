import requests
import xml.etree.ElementTree as ET
import csv
import time
from datetime import datetime, timedelta
from urllib.parse import unquote

def main():
    # 1. 대표님이 주신 디코딩 키를 변수에 넣습니다.
    # (앞뒤 공백이 없도록 .strip()을 추가했습니다)
    raw_key = "R+veVpMchPZJob94a/x0z5KlwTOuB+OOlK2GhFGigbo7p/fupVm7zAY14QNDhXHg8mSIEyBJOF1x/1VIvJAwSQ=="
    decoded_key = raw_key.strip()
    
    results = []
    curr = datetime(2025, 1, 1)
    end = datetime(2025, 12, 31)
    
    print("🇰🇷 대한민국 정책브리핑 2025 전수 조사 시작...")

    # API 세션 생성 (성능 및 안정성 향상)
    session = requests.Session()

    while curr <= end:
        batch_end = curr + timedelta(days=2)
        if batch_end > end: batch_end = end
        
        s_str = curr.strftime("%Y%m%d")
        e_str = batch_end.strftime("%Y%m%d")
        
        print(f"📡 구간: {s_str} ~ {e_str}", end=" ", flush=True)
        
        # [핵심 수정] params에 넣지 않고 URL에 직접 키를 포함시킵니다.
        # 이렇게 해야 파이썬이 키의 '+'나 '/' 기호를 멋대로 변환하지 않습니다.
        url = f"http://apis.data.go.kr/1371000/pressReleaseService/pressReleaseList?serviceKey={decoded_key}"
        
        params = {
            'startDate': s_str,
            'endDate': e_str,
            'pageNo': 1,
            'numOfRows': 500
        }

        try:
            # 401 에러 방지를 위해 직접 구성한 URL 사용
            resp = session.get(url, params=params, timeout=30)
            
            if resp.status_code == 200:
                # 응답 내용 확인
                if "SERVICE_KEY_IS_NOT_REGISTERED_ERROR" in resp.text:
                    print("❌ 등록되지 않은 키입니다. (활성화까지 최대 1시간 소요)")
                    break
                
                root = ET.fromstring(resp.content)
                items = root.findall('.//NewsItem')
                
                for item in items:
                    results.append({
                        "발행일": item.findtext('ApproveDate'),
                        "부처": item.findtext('MinisterCode'),
                        "제목": item.findtext('Title'),
                        "링크": item.findtext('OriginalUrl')
                    })
                print(f"✅ ({len(items)}건 완료)")
            
            elif resp.status_code == 401:
                print("❌ 401 인증 실패 (인코딩/디코딩 키 교체 시도 필요)")
                break
            else:
                print(f"❌ 오류 코드: {resp.status_code}")
                break
                
        except Exception as e:
            print(f"❌ 연결 실패: {e}")
            break
        
        curr += timedelta(days=3)
        time.sleep(0.5)

    # 파일 저장
    if results:
        file_name = 'Korea_Policy_2025.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "부처", "제목", "링크"])
            writer.writeheader()
            writer.writerows(results)
        print(f"\n🏁 수집 완료! 총 {len(results)}건 저장됨.")

if __name__ == "__main__":
    main()
