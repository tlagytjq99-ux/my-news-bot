import feedparser

import csv

import urllib.parse

from datetime import datetime

from googlenewsdecoder import gnewsdecoder

import time



def main():

    # 1. 대통령 실행 조치(Presidential Actions) 페이지를 집중 타겟팅하는 쿼리

    # site 연산자에 경로를 포함시켜 해당 섹션의 인덱싱을 우선적으로 가져옵니다.

    query = 'site:whitehouse.gov/presidential-actions/executive-orders after:2025-01-01'

    encoded_query = urllib.parse.quote(query)

    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"



    # 2. 사진 속 46개 카테고리 대응 키워드 (범용 단어 포함)

    category_map = {

        "AI/Digital": ["AI", "Artificial Intelligence", "Algorithm", "Digital", "Automation"],

        "Semiconductor/Tech": ["Semiconductor", "Chip", "Critical Technology", "Supply Chain"],

        "Energy/Infrastructure": ["Nuclear", "Energy", "Infrastructure", "SMR", "Power"],

        "Cyber/Security": ["Cyber", "Security", "Defense", "Intelligence"],

        "Economy/Trade": ["Tariff", "Trade", "Investment", "Tax", "Finance"]

    }



    print(f"📡 백악관 '대통령 실행 조치' 섹션 2025년 데이터 정밀 스캔 시작...")



    try:

        feed = feedparser.parse(rss_url)

        # 만약 해당 경로 결과가 너무 적으면 전체 경로로 확장해서 다시 시도

        if len(feed.entries) < 3:

            print("💡 특정 섹션 데이터가 적어 백악관 전체 소식으로 확장 검색합니다.")

            query = 'site:whitehouse.gov after:2025-01-01'

            encoded_query = urllib.parse.quote(query)

            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

            feed = feedparser.parse(rss_url)



        results = []

        for entry in feed.entries:

            try:

                pub_date = datetime(*entry.published_parsed[:3])

                if pub_date.year == 2025:

                    title = entry.title.split(' - ')[0].strip()

                    link = entry.link

                    

                    # URL 디코딩

                    try:

                        decoded = gnewsdecoder(link)

                        actual_url = decoded.get('decoded_url', link)

                    except:

                        actual_url = link



                    # 유형 분류

                    matched_types = []

                    for cat, kws in category_map.items():

                        if any(kw.lower() in title.lower() for kw in kws):

                            matched_types.append(cat)

                    

                    # '대통령 실행 조치' 페이지 출처인지 확인 (우선순위 표시)

                    doc_type = "Executive Action" if "/presidential-actions/" in actual_url else "General News"



                    results.append({

                        "발행일": pub_date.strftime('%Y-%m-%d'),

                        "문서유형": doc_type,

                        "기술분류": ", ".join(matched_types) if matched_types else "Other Policy",

                        "제목": title,

                        "원문링크": actual_url

                    })

                time.sleep(0.05)

            except: continue



        # 3. CSV 저장

        file_name = 'whitehouse_2025_tech_report.csv'

        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:

            writer = csv.DictWriter(f, fieldnames=["발행일", "문서유형", "기술분류", "제목", "원문링크"])

            writer.writeheader()

            if results:

                results.sort(key=lambda x: x['발행일'], reverse=True)

                writer.writerows(results)

                print(f"✅ 완료: 총 {len(results)}건의 2025년 데이터를 분류 저장했습니다.")

            else:

                print("⚠️ 2025년 데이터를 찾지 못했습니다.")



    except Exception as e:

        print(f"❌ 오류 발생: {e}")



if __name__ == "__main__":

    main()
