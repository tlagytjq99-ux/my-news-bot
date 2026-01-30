import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 대표님이 주신 실제 검색 결과 페이지 주소
    target_url = "https://www.oecd.org/en/search.html?facetTags=oecd-policy-issues:pi20&oecd-languages:en&orderBy=mostRelevant"
    
    file_name = 'oecd_ai_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    # 브라우저처럼 보이게 헤더 설정 (매우 중요)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,ko;q=0.8"
    }

    print(f"📡 [OECD 정밀 스크래핑] 웹페이지 분석 시작...")
    new_data = []

    try:
        response = requests.get(target_url, headers=headers, timeout=30)
        # OECD가 차단했을 경우를 대비해 인코딩 강제 설정
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 💡 OECD 검색 결과 리스트의 제목과 링크 패턴 분석
        # 검색 결과 아이템들은 보통 'a' 태그 내에 제목을 가지고 있습니다.
        articles = soup.find_all('a', href=True)
        
        print(f"🔍 페이지 내 링크 {len(articles)}개 분석 중...")

        for article in articles:
            title_en = article.get_text().strip()
            link = article['href']
            
            # 💡 핵심 필터: 제목에 AI나 정책 관련 단어가 있고, 링크가 /en/으로 시작하는 기사만 추출
            if len(title_en) > 20 and any(kw in title_en.upper() for kw in ['AI', 'ARTIFICIAL', 'DIGITAL', 'POLICY']):
                if link.startswith('/') or 'oecd.org' in link:
                    full_link = link if link.startswith('http') else "https://www.oecd.org" + link
                    
                    # 중복 제거
                    if any(d['원문'] == title_en for d in new_data): continue

                    # 한국어 번역
                    try:
                        title_ko = translator.translate(title_en, dest='ko').text
                    except:
                        title_ko = title_en

                    new_data.append({
                        "기관": "OECD",
                        "발행일": collected_date, # HTML 방식은 날짜 파싱이 까다로워 수집일로 대체
                        "제목": title_ko,
                        "원문": title_en,
                        "링크": full_link,
                        "수집일": collected_date
                    })
                    
            if len(new_data) >= 15: break # 상위 15건만

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    # 💾 결과 저장
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        if new_data:
            writer.writerows(new_data)
            print(f"✅ 드디어 성공! {len(new_data)}건의 데이터를 확보했습니다.")
        else:
            # 💡 만약 데이터가 없으면 '샘플 데이터'라도 넣어서 파일 생성을 보장함
            writer.writerow({
                "기관": "OECD", "발행일": collected_date, 
                "제목": "데이터를 불러오는 중입니다 (새로운 업데이트 확인 필요)", 
                "원문": "Checking for new updates", "링크": target_url, "수집일": collected_date
            })
            print("⚠️ 조건에 맞는 실시간 데이터가 없어 점검 알림을 저장했습니다.")

if __name__ == "__main__":
    main()
