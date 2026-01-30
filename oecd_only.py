import requests
import csv
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 OECD 내부 검색 API 엔드포인트 (대표님이 주신 검색 조건 그대로)
    api_url = "https://www.oecd.org/en/_jcr_content/root/container/container/search.oecd-search-results.json"
    
    # 💡 검색 필터 파라미터 (pi20 = AI 정책)
    params = {
        "facetTags": [
            "oecd-content-types:news/press-releases",
            "oecd-policy-issues:pi20",
            "oecd-languages:en"
        ],
        "orderBy": "mostRelevant",
        "page": 0
    }
    
    file_name = 'oecd_ai_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"📡 [OECD API 직접 타격] 데이터 수집 시작...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    try:
        response = requests.get(api_url, params=params, headers=headers)
        if response.status_code != 200:
            print(f"❌ 접속 실패: {response.status_code}")
            return

        data = response.json()
        items = data.get('results', [])
        
        new_data = []
        print(f"🔍 총 {len(items)}건의 결과 발견. 분석 및 번역 중...")

        for item in items:
            title_en = item.get('title', '')
            link = item.get('url', '')
            if not link.startswith('http'):
                link = "https://www.oecd.org" + link
            
            # 날짜 추출
            published_date = item.get('date', collected_date)

            # 한국어 번역
            try:
                title_ko = translator.translate(title_en, src='en', dest='ko').text
            except:
                title_ko = title_en

            new_data.append({
                "기관": "OECD",
                "발행일": published_date,
                "제목": title_ko,
                "원문": title_en,
                "링크": link,
                "수집일": collected_date
            })

        # 💾 저장
        if new_data:
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
                writer.writeheader()
                writer.writerows(new_data)
            print(f"✅ 성공! {len(new_data)}건의 OECD AI 리포트를 엑셀로 저장했습니다.")
        else:
            print("💡 조건에 맞는 데이터가 없습니다.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    main()
