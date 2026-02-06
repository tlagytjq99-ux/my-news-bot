import requests
import xml.etree.ElementTree as ET
import csv
import time
import os
from datetime import datetime, timedelta

def main():
    # 설정파일(YAML)에서 키를 가져오거나 직접 입력
    SERVICE_KEY = os.getenv("MY_SERVICE_KEY", "R+veVpMchPZJob94a/x0z5KlwTOuB+OOlK2GhFGigbo7p/fupVm7zAY14QNDhXHg8mSIEyBJOF1x/1VIvJAwSQ==")
    
    results = []
    curr = datetime(2025, 1, 1)
    end = datetime(2025, 12, 31)
    
    print("🇰🇷 대한민국 정책브리핑 2025 전수 조사 시작...")

    while curr <= end:
        # 가이드북에 따라 최대 3일치만 요청
        batch_end = curr + timedelta(days=2)
        if batch_end > end: batch_end = end
        
        s_str = curr.strftime("%Y%m%d")
        e_str = batch_end.strftime("%Y%m%d")
        
        print(f"📡 구간: {s_str} ~ {e_str}", end=" ", flush=True)
        
        url = "http://apis.data.go.kr/1371000/pressReleaseService/pressReleaseList"
        params = {
            'serviceKey': SERVICE_KEY,
            'startDate': s_str,
            'endDate': e_str,
            'pageNo': 1,
            'numOfRows': 500 # 한 번에 500건까지 (3일치 보도자료는 보통 이 안에 다 들어옴)
        }

        try:
            resp = requests.get(url, params=params, timeout=20)
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
                print(f"✅ ({len(items)}건 완료)")
            else:
                print(f"❌ 오류 코드: {resp.status_code}")
        except Exception as e:
            print(f"❌ 연결 실패: {e}")
        
        curr += timedelta(days=3) # 다음 3일로 이동
        time.sleep(0.3) # API 서버 보호

    # 저장 (한글 깨짐 방지를 위해 utf-8-sig 사용)
    if results:
        file_name = 'Korea_Policy_2025.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "부처", "제목", "링크"])
            writer.writeheader()
            writer.writerows(results)
        print(f"\n🏁 전수 조사 종료! 총 {len(results)}건 저장됨.")

if __name__ == "__main__":
    main()
