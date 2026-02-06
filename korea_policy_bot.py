import requests
import xml.etree.ElementTree as ET
import csv
import os
import time
from datetime import datetime, timedelta

def main():
    # 시크릿에서 인코딩 키 가져오기
    SERVICE_KEY = os.getenv("MY_SERVICE_KEY")
    
    results = []
    # 시작 날짜를 2025년 1월 1일로 설정
    curr = datetime(2025, 1, 1)
    end = datetime.now() # 오늘까지
    
    print("🇰🇷 대한민국 정책브리핑 2025-2026 전수 조사 시작...")

    while curr <= end:
        batch_end = curr + timedelta(days=5) # 넉넉하게 5일씩 끊어서
        if batch_end > end: batch_end = end
        
        s_str = curr.strftime("%Y%m%d")
        e_str = batch_end.strftime("%Y%m%d")
        
        print(f"📡 구간: {s_str} ~ {e_str}", end=" ", flush=True)
        
        # 인코딩 키를 그대로 사용하는 URL 방식
        target_url = (
            f"http://apis.data.go.kr/1371000/pressReleaseService/pressReleaseList"
            f"?serviceKey={SERVICE_KEY}"
            f"&startDate={s_str}"
            f"&endDate={e_str}"
            f"&pageNo=1"
            f"&numOfRows=1000" # 넉넉하게
        )

        try:
            resp = requests.get(target_url, timeout=30)
            if resp.status_code == 200:
                # 데이터 존재 확인
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
                    print(f"✅ ({len(items)}건)")
                else:
                    print("⚪ (데이터 없음)")
            else:
                print(f"❌ 오류({resp.status_code})")
                
        except Exception as e:
            print(f"❌ 에러: {e}")
        
        curr += timedelta(days=6) # 다음 구간으로
        time.sleep(0.2)

    # 결과 저장
    if results:
        file_name = 'Korea_Policy_2025.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "부처", "제목", "링크"])
            writer.writeheader()
            writer.writerows(results)
        print(f"\n🏁 총 {len(results)}건 수집 완료! 파일이 생성되었습니다.")
    else:
        print("\n⚠️ 수집된 데이터가 하나도 없습니다. 날짜나 키를 다시 확인해주세요.")

if __name__ == "__main__":
    main()
