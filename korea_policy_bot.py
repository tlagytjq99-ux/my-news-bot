import requests
import xml.etree.ElementTree as ET
import csv
import os
import time

def main():
    # 1. 시크릿에서 인코딩 키 가져오기
    SERVICE_KEY = os.getenv("MY_SERVICE_KEY")
    
    results = []
    page = 1
    target_year = "2025"
    keep_going = True

    # [핵심] 대표님이 받으신 '요청주소'를 그대로 사용 (보안을 위해 https 권장)
    base_url = "http://apis.data.go.kr/1371000/pressReleaseService/pressReleaseList"

    print(f"🇰🇷 정책브리핑 전수 조사 시작 (공공데이터포털 표준 주소 적용)")

    while keep_going:
        # [치트키] 인증키를 URL 맨 앞에 배치하여 인코딩 오류 방지
        request_url = (
            f"{base_url}?serviceKey={SERVICE_KEY}"
            f"&pageNo={page}"
            f"&numOfRows=100"
            f"&type=xml" # 명시적으로 XML 요청
        )

        try:
            # 깃허브 가상 환경에서 발생할 수 있는 SSL 인증 무시 옵션 추가
            resp = requests.get(request_url, timeout=30, verify=True)
            
            if resp.status_code == 200:
                # 401 Unauthorized 문자열이 본문에 섞여 나오는지 체크
                if "Unauthorized" in resp.text or "401" in resp.text:
                    print(f"\n❌ {page}페이지에서 인증 거부됨 (401)")
                    break
                
                if "NewsItem" in resp.text:
                    root = ET.fromstring(resp.content)
                    items = root.findall('.//NewsItem')
                    
                    if not items: break

                    for item in items:
                        pub_date = item.findtext('ApproveDate')
                        if not pub_date: continue
                        
                        if target_year in pub_date:
                            results.append({
                                "발행일": pub_date,
                                "부처": item.findtext('MinisterCode'),
                                "제목": item.findtext('Title'),
                                "링크": item.findtext('OriginalUrl')
                            })
                        elif "2024" in pub_date: # 2024년이 보이기 시작하면 수집 종료
                            keep_going = False
                            break

                    print(f"📥 {page}페이지 수집 중... (2025년 누적: {len(results)}건)", end="\r")
                    page += 1
                else:
                    print("\n🏁 더 이상 데이터가 없습니다.")
                    break
            else:
                print(f"\n❌ 서버 응답 실패 (코드: {resp.status_code})")
                break
                
        except Exception as e:
            print(f"\n❌ 연결 에러: {e}")
            break
        
        time.sleep(0.1)

    # 최종 저장
    file_name = 'Korea_Policy_2025.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["발행일", "부처", "제목", "링크"])
        writer.writeheader()
        if results:
            writer.writerows(results)
            print(f"\n\n✅ 수집 완료! 총 {len(results)}건의 2025년 데이터를 저장했습니다.")
        else:
            print("\n\n⚠️ 결과가 없습니다. 키 활성화 여부를 다시 확인해 주세요.")

if __name__ == "__main__":
    main()
