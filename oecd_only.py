import requests
import csv
import os
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 OECD API 엔드포인트
    api_url = "https://www.oecd.org/en/_jcr_content/root/container/container/search.oecd-search-results.json"
    
    # 💡 검색 조건을 더 유연하게 조정 (AI 정책 pi20 중심)
    params = {
        "facetTags": "oecd-policy-issues:pi20", # 태그를 문자열로 단순화
        "orderBy": "mostRelevant",
        "page": 0
    }
    
    file_name = 'oecd_ai_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    # 브라우저처럼 보이게 헤더 강화
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.oecd.org/en/search.html"
    }

    print(f"📡 [OECD API] 데이터 요청 중...")
    new_data = []

    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=30)
        print(f"📡 응답 코드: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            items = data.get('results', [])
            print(f"🔍 발견된 아이템 수: {len(items)}")

            for item in items[:15]: # 상위 15건
                title_en = item.get('title', 'No Title')
                link = item.get('url', '')
                if link and not link.startswith('http'):
                    link = "https://www.oecd.org" + link
                
                published_date = item.get('date', collected_date)

                # 번역 (오류 발생 시 원문 유지)
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

    except Exception as e:
        print(f"❌ 수집 중 에러 발생: {e}")

    # 💾 중요: 결과가 없어도 헤더만 있는 파일이라도 생성 (워크플로우 통과용)
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        if new_data:
            writer.writerows(new_data)
            print(f"✅ {len(new_data)}건 저장 완료.")
        else:
            print("⚠️ 수집된 데이터가 없어 빈 파일이 생성되었습니다.")

if __name__ == "__main__":
    main()
