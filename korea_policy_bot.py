import requests
import xml.etree.ElementTree as ET
import csv
import os
from datetime import datetime, timedelta

def main():
    # 시크릿에서 키 가져오기
    SERVICE_KEY = os.getenv("MY_SERVICE_KEY")
    
    # 테스트 구간: 최근 10일치만 수집해보기
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10)
    
    s_str = start_date.strftime("%Y%m%d")
    e_str = end_date.strftime("%Y%m%d")
    
    print(f"🇰🇷 최근 데이터 수집 테스트 시작 ({s_str} ~ {e_str})...")

    # URL 직접 구성 (인증 에러 방지용)
    target_url = (
        f"http://apis.data.go.kr/1371000/pressReleaseService/pressReleaseList"
        f"?serviceKey={SERVICE_KEY}"
        f"&startDate={s_str}"
        f"&endDate={e_str}"
        f"&pageNo=1"
        f"&numOfRows=100"
    )

    try:
        resp = requests.get(target_url, timeout=30)
        print(f"📡 API 응답 상태: {resp.status_code}")
        
        if resp.status_code == 200:
            # 응답 본문이 비어있는지 확인
            if "NewsItem" not in resp.text:
                print("⚠️ 데이터는 성공적으로 받았으나, 해당 기간에 보도자료가 없습니다.")
                return

            root = ET.fromstring(resp.content)
            items = root.findall('.//NewsItem')
            
            results = []
            for item in items:
                results.append({
                    "발행일": item.findtext('ApproveDate'),
                    "부처": item.findtext('MinisterCode'),
                    "제목": item.findtext('Title'),
                    "링크": item.findtext('OriginalUrl')
                })
            
            if results:
                file_name = 'Korea_Policy_2025.csv'
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["발행일", "부처", "제목", "링크"])
                    writer.writeheader()
                    writer.writerows(results)
                print(f"✅ 수집 성공! {len(results)}건의 파일을 생성했습니다.")
            else:
                print("❌ 수집된 아이템이 없습니다.")
        else:
            print(f"❌ API 호출 실패 (상태코드: {resp.status_code})")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    main()
