import requests
import csv
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 OECD AI 정책(pi20) 전용 API 엔드포인트
    api_url = "https://www.oecd.org/en/_jcr_content/root/container/container/search.oecd-search-results.json"
    
    # 💡 검색 조건 설정 (AI 정책 태그 pi20)
    params = {
        "facetTags": "oecd-policy-issues:pi20",
        "orderBy": "mostRelevant",
        "page": 0
    }
    
    file_name = 'oecd_ai_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    # 🛡️ OECD 보안 통과를 위한 정밀 헤더 (브라우저 위장)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.oecd.org/en/search.html",
        "X-Requested-With": "XMLHttpRequest"
    }

    print(f"📡 OECD 서버에 데이터 요청 중...")
    new_data = []

    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            items = response.json().get('results', [])
            print(f"🔍 발견된 기사: {len(items)}건")

            for item in items:
                title_en = item.get('title', '')
                link = item.get('url', '')
                if link and not link.startswith('http'):
                    link = "https://www.oecd.org" + link
                
                # 날짜가 없을 경우 오늘 날짜
                pub_date = item.get('date', collected_date)

                # 한국어 번역
                try:
                    title_ko = translator.translate(title_en, dest='ko').text
                except:
                    title_ko = title_en

                new_data.append({
                    "기관": "OECD",
                    "발행일": pub_date,
                    "제목": title_ko,
                    "원문": title_en,
                    "링크": link,
                    "수집일": collected_date
                })
        else:
            print(f"❌ 접속 실패 (코드: {response.status_code})")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    # 💾 결과 저장 (데이터가 없어도 빈 파일은 생성하여 에러 방지)
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        if new_data:
            writer.writerows(new_data)
            print(f"✅ {len(new_data)}건의 보고서 저장 완료!")
        else:
            print("⚠️ 수집된 데이터가 없습니다.")

if __name__ == "__main__":
    main()
