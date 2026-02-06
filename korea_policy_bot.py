import requests
import xml.etree.ElementTree as ET
import csv
import os
import time
from datetime import datetime, timedelta

def main():
    # 시크릿에서 키 가져오기
    SERVICE_KEY = os.getenv("MY_SERVICE_KEY")
    
    results = []
    # [수정] 2025년 1월 1일부터 전수 조사
    curr = datetime(2025, 1, 1)
    end = datetime(2025, 12, 31)
    
    print(f"🇰🇷 대한민국 정책브리핑 전수 조사 시작 (2025-01-01 ~ 12-31)")

    while curr <= end:
        batch_end = curr + timedelta(days=9) # 10일씩 넉넉히
        if batch_end > end: batch_end = end
        
        s_str = curr.strftime("%Y%m%d")
        e_str = batch_end.strftime("%Y%m%d")
        
        # 인코딩 키를 URL에 직접 주입 (대표님이 뚫으신 방식)
        target_url = (
            f"http://apis.data.go.kr/1371000/pressReleaseService/pressReleaseList"
            f"?serviceKey={SERVICE_KEY}"
            f"&startDate={s_str}"
            f"&endDate={e_str}"
            f"&pageNo=1"
            f"&numOfRows=1000"
        )

        try:
            resp = requests.get(target_url, timeout=30)
            if resp.status_code == 200 and "NewsItem" in resp.text:
                root = ET.fromstring(resp.content)
                items = root.findall('.//NewsItem')
                for item in items:
                    results.append({
                        "발행일": item.findtext('ApproveDate'),
                        "부처": item.findtext('MinisterCode'),
                        "제목": item.findtext('Title'),
                        "링크": item.findtext('OriginalUrl')
                    })
                print(f"📡 {s_str} ~ {e_str}: ✅ {len(items)}건 완료")
            else:
                print(f"📡 {s_str} ~ {e_str}: ⚪ 데이터 없음")
        except Exception as e:
            print(f"❌ {s_str} 구간 에러: {e}")
        
        curr += timedelta(days=10)
        time.sleep(0.2)

    # [핵심] 결과가 있든 없든 무조건 파일을 생성하여 'No files found' 에러 방지
    file_name = 'Korea_Policy_2025.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["발행일", "부처", "제목", "링크"])
        writer.writeheader()
        if results:
            writer.writerows(results)
            print(f"\n🏁 총 {len(results)}건 수집 완료!")
        else:
            print("\n⚠️ 수집된 데이터가 없습니다. (빈 파일을 생성했습니다)")

if __name__ == "__main__":
    main()
