import requests
from bs4 import BeautifulSoup
import csv
import os

def crawl_digital_agency_2026():
    # 일문 보도자료 페이지
    url = "https://www.digital.go.jp/news/press"
    file_name = 'Japan_Digital_Policy_2025.csv'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    print("🎯 [데이터 정밀 추적] 일본 디지털청 스캔 중...")

    try:
        res = requests.get(url, headers=headers, timeout=20)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')

        # 디지털청 리스트의 실제 구조: article 태그 또는 특정 클래스 내의 a 태그
        # 더 넓은 범위로 찾기 위해 h3와 연결된 링크를 타겟팅합니다.
        items = soup.find_all('a') 

        policy_data = []
        for a in items:
            # 제목과 날짜가 포함된 텍스트 추출
            text = a.get_text(strip=True)
            href = a.get('href', '')
            
            # 2025년 또는 2026년 날짜 형식이 포함된 뉴스 링크만 필터링
            if href.startswith('/news/') and any(yr in text for yr in ['2025', '2026', '令和7', '令和8']):
                policy_data.append({
                    "date": text[:10], # 앞부분 날짜만 대략 추출
                    "title": text[10:].strip(),
                    "link": "https://www.digital.go.jp" + href if href.startswith('/') else href
                })

        # [중요] 중복 제거 및 저장
        unique_data = list({v['link']: v for v in policy_data}.values())

        # 파일이 생성되지 않는 에러 방지를 위해 무조건 생성 프로세스 가동
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            if unique_data:
                writer.writerows(unique_data)
                print(f"✅ {len(unique_data)}건의 데이터를 파일에 썼습니다.")
            else:
                print("⚠️ 수집된 데이터가 없습니다. 빈 파일을 생성합니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        # 에러가 나도 빈 파일을 만들어야 다음 깃 단계가 깨지지 않습니다.
        if not os.path.exists(file_name):
            with open(file_name, 'w', encoding='utf-8-sig') as f:
                f.write("date,title,link\n")

if __name__ == "__main__":
    crawl_digital_agency_2026()
