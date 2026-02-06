import requests
import xml.etree.ElementTree as ET
import csv
import os
import time

def main():
    SERVICE_KEY = os.getenv("MY_SERVICE_KEY")
    results = []
    
    # 1페이지부터 시작해서 2025년 데이터가 끝날 때까지 수집
    page = 1
    target_year = "2025"
    keep_going = True

    print(f"🇰🇷 정책브리핑 역방향 전수 조사 시작 (최신순 -> 2025년까지)")

    while keep_going:
        # 날짜 필터 없이 페이지당 100건씩 요청
        url = (
            f"http://apis.data.go.kr/1371000/pressReleaseService/pressReleaseList"
            f"?serviceKey={SERVICE_KEY}"
            f"&pageNo={page}"
            f"&numOfRows=100"
        )

        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200 and "NewsItem" in resp.text:
                root = ET.fromstring(resp.content)
                items = root.findall('.//NewsItem')
                
                if not items:
                    print("\n🏁 더 이상 가져올 데이터가 없습니다.")
                    break

                for item in items:
                    pub_date = item.findtext('ApproveDate') # 예: 2025-05-20 14:00:00
                    
                    # 2025년 데이터만 골라내기
                    if target_year in pub_date:
                        results.append({
                            "발행일": pub_date,
                            "부처": item.findtext('MinisterCode'),
                            "제목": item.findtext('Title'),
                            "링크": item.findtext('OriginalUrl')
                        })
                    
                    # 2024년 데이터가 나오기 시작하면 중단 (이미 2025년은 다 지나왔으므로)
                    elif "2024" in pub_date:
                        keep_going = False
                        break

                print(f"📥 {page}페이지 수집 중... (현재까지 2025년 데이터: {len(results)}건)", end="\r")
                page += 1
                
                # 너무 많은 페이지를 넘기면 시간이 오래 걸리니 제한 (최대 200페이지 = 2만건)
                if page > 200: 
                    keep_going = False

            else:
                print(f"\n❌ API 응답 이상 (코드: {resp.status_code})")
                break
                
        except Exception as e:
            print(f"\n❌ 에러 발생: {e}")
            break
        
        time.sleep(0.1)

    # 파일 저장
    file_name = 'Korea_Policy_2025.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["발행일", "부처", "제목", "링크"])
        writer.writeheader()
        if results:
            writer.writerows(results)
            print(f"\n\n✅ 완료! 2025년 데이터 총 {len(results)}건을 찾아서 저장했습니다.")
        else:
            # 아예 안나올 경우를 대비해 샘플이라도 출력
            print("\n\n⚠️ 2025년 데이터가 검색되지 않았습니다. API 응답 확인 필요.")
            print(f"DEBUG: 마지막 응답 샘플 -> {resp.text[:200]}")

if __name__ == "__main__":
    main()
