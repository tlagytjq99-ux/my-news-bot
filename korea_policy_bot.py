import requests
import xml.etree.ElementTree as ET
import csv
import os
import time
from datetime import datetime, timedelta

def main():
    # 1. 시크릿에서 키 가져오기 (인코딩된 키 권장)
    SERVICE_KEY = os.getenv("MY_SERVICE_KEY")
    if not SERVICE_KEY:
        print("❌ 에러: MY_SERVICE_KEY를 찾을 수 없습니다.")
        return

    results = []
    # 2025년 전체를 수집하기 위한 날짜 설정
    start_date = datetime(2025, 1, 1)
    end_of_year = datetime(2025, 12, 31)
    
    print("🇰🇷 대한민국 정책브리핑(API) 전수 수집을 시작합니다...")

    current_start = start_date
    while current_start <= end_of_year:
        # 한국 API 특성상 구간을 짧게(15일) 잡아야 응답이 안정적입니다.
        current_end = current_start + timedelta(days=14)
        if current_end > end_of_year:
            current_end = end_of_year
            
        s_str = current_start.strftime("%Y%m%d")
        e_str = current_end.strftime("%Y%m%d")
        
        print(f"📡 구간 수집 중: {s_str} ~ {e_str}", end=" ", flush=True)

        # 필수 파라미터를 URL에 직접 주입 (인코딩 중복 방지)
        url = (
            f"http://apis.data.go.kr/1371000/pressReleaseService/pressReleaseList"
            f"?serviceKey={SERVICE_KEY}"
            f"&startDate={s_str}"
            f"&endDate={e_str}"
            f"&pageNo=1"
            f"&numOfRows=500"
        )

        try:
            # 타임아웃을 넉넉히 주어 서버 지연에 대비합니다.
            resp = requests.get(url, timeout=45)
            
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
                print(f"✅ {len(items)}건 완료")
            else:
                # 인증 오류나 데이터 없음 처리
                if "Unauthorized" in resp.text:
                    print("❌ 인증 오류(401)! 키를 확인하세요.")
                    break
                print("⚪ 데이터 없음")
                
        except Exception as e:
            print(f"❌ 에러 발생: {e}")
        
        current_start = current_end + timedelta(days=1)
        time.sleep(0.3) # 서버 부하 방지용 짧은 휴식

    # 2. 결과 저장
    file_name = 'Korea_Policy_2025.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["발행일", "부처", "제목", "링크"])
        writer.writeheader()
        if results:
            writer.writerows(results)
            print(f"\n🏁 수집 완료! 총 {len(results)}건이 '{file_name}'에 저장되었습니다.")
        else:
            print("\n⚠️ 수집된 데이터가 없습니다.")

if __name__ == "__main__":
    main()
