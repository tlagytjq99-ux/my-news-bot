import requests
import xml.etree.ElementTree as ET
import csv
import os
import time

def main():
    # 깃허브 시크릿에 넣으신 그 인코딩 키를 가져옵니다.
    SERVICE_KEY = os.getenv("MY_SERVICE_KEY")
    
    results = []
    page = 1
    target_year = "2025"
    keep_going = True

    # 대표님이 확인하신 바로 그 요청 주소!
    base_url = "http://apis.data.go.kr/1371000/pressReleaseService/pressReleaseList"

    print(f"🚀 인증 성공 확인! 2025년 데이터 수집을 시작합니다.")

    while keep_going:
        # 인증키를 URL에 직접 넣는 가장 확실한 방식
        request_url = (
            f"{base_url}?serviceKey={SERVICE_KEY}"
            f"&pageNo={page}"
            f"&numOfRows=100"
        )

        try:
            resp = requests.get(request_url, timeout=30)
            
            if resp.status_code == 200 and "NewsItem" in resp.text:
                root = ET.fromstring(resp.content)
                items = root.findall('.//NewsItem')
                
                if not items:
                    print("\n🏁 모든 페이지를 훑었습니다.")
                    break

                for item in items:
                    pub_date = item.findtext('ApproveDate')
                    if not pub_date: continue
                    
                    # 2025년 데이터만 선별해서 담기
                    if target_year in pub_date:
                        results.append({
                            "발행일": pub_date,
                            "부처": item.findtext('MinisterCode'),
                            "제목": item.findtext('Title'),
                            "링크": item.findtext('OriginalUrl')
                        })
                    
                    # 2024년이 보이기 시작하면 과거 데이터이므로 종료
                    elif "2024" in pub_date:
                        keep_going = False
                        break

                print(f"📥 {page}페이지 분석 중... (2025년 누적: {len(results)}건)", end="\r")
                page += 1
            else:
                print(f"\n📡 데이터 수집 중단 (더 이상 항목이 없거나 오류 발생)")
                break
                
        except Exception as e:
            print(f"\n❌ 에러: {e}")
            break
        
        time.sleep(0.1)

    # 최종 결과 저장
    file_name = 'Korea_Policy_2025.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["발행일", "부처", "제목", "링크"])
        writer.writeheader()
        if results:
            writer.writerows(results)
            print(f"\n\n✅ 수집 완료! 총 {len(results)}건을 'Korea-Policy-2025-Data'에 담았습니다.")
        else:
            print("\n\n⚠️ 2025년 데이터를 찾지 못했습니다. API 응답을 다시 확인해 주세요.")

if __name__ == "__main__":
    main()
