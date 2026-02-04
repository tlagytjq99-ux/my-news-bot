import feedparser
import csv
import urllib.parse
import time
from datetime import datetime
from googletrans import Translator
from googlenewsdecoder import gnewsdecoder

def main():
    # 🎯 도메인 주소에서 https:// 및 하위 경로를 제거하여 검색 정확도를 높였습니다.
    gov_agencies = [
        {"국가": "미국", "기관": "백악관", "도메인": "whitehouse.gov"},
        {"국가": "미국", "기관": "DOC (상무부)", "도메인": "commerce.gov"},
        {"국가": "미국", "기관": "NTIA", "도메인": "ntia.gov"},
        {"국가": "중국", "기관": "CAC (사이버공간관리국)", "도메인": "cac.gov.cn"},
        {"국가": "중국", "기관": "MIIT (공업정보화부)", "도메인": "miit.gov.cn"},
        {"국가": "대한민국", "기관": "과학기술정보통신부", "도메인": "msit.go.kr"},
        {"국가": "대한민국", "기관": "산업통상자원부", "도메인": "motie.go.kr"},
        {"국가": "싱가포르", "기관": "MDDI", "도메인": "mddi.gov.sg"},
        {"국가": "싱가포르", "기관": "IMDA", "도메인": "imda.gov.sg"},
        {"국가": "독일", "기관": "BMDV", "도메인": "bmdv.bund.de"},
        {"국가": "독일", "기관": "BMWK", "도메인": "bmwk.de"},
        {"국가": "일본", "기관": "MIC (총무성)", "도메인": "soumu.go.jp"},
        {"국가": "일본", "기관": "디지털청", "도메인": "digital.go.jp"},
        {"국가": "일본", "기관": "METI (경제산업성)", "도메인": "meti.go.jp"},
        {"국가": "영국", "기관": "DSIT", "도메인": "www.gov.uk/government/organisations/department-for-science-innovation-and-technology"},
        {"국가": "영국", "기관": "DBT", "도메인": "www.gov.uk/government/organisations/department-for-business-and-trade"},
        {"국가": "네덜란드", "기관": "EZK", "도메인": "government.nl"},
        {"국가": "스웨덴", "기관": "Ministry of Finance", "도메인": "government.se"},
        {"국가": "핀란드", "기관": "LVM", "도메인": "lvm.fi"},
        {"국가": "핀란드", "기관": "MEE", "도메인": "tem.fi"},
        {"국가": "스위스", "기관": "OFCOM", "도메인": "bakom.admin.ch"},
        {"국가": "덴마크", "기관": "Digitaliseringsstyrelsen", "도메인": "digst.dk"},
        {"국가": "노르웨이", "기관": "KDD", "도메인": "regjeringen.no"},
        {"국가": "이스라엘", "기관": "IIA", "도메인": "innovationisrael.org.il"},
        {"국가": "캐나다", "기관": "ISED", "도메인": "ised-isde.canada.ca"},
        {"국가": "프랑스", "기관": "Bercy", "도메인": "economie.gouv.fr"},
        {"국가": "호주", "기관": "DISR", "도메인": "industry.gov.au"},
        {"국가": "대만", "기관": "moda", "도메인": "moda.gov.tw"},
        {"국가": "UAE", "기관": "TDRA", "도메인": "tdra.gov.ae"},
        {"국가": "사우디", "기관": "MCIT", "도메인": "mcit.gov.sa"}
    ]

    all_final_data = []
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    file_name = f'global_ict_policy_intelligence_{collected_date}.csv'

    print(f"📡 개선된 쿼리로 {len(gov_agencies)}개 기관 재수집 시작...")

    for agency in gov_agencies:
        print(f"🔍 [{agency['국가']}] {agency['기관']} 탐색 중...")
        
        # 💡 [개선] intitle 제약을 제거하고 검색 키워드를 확장했습니다.
        # 이렇게 하면 제목에 AI가 없어도 본문 내용에 관련 키워드가 있으면 수집됩니다.
        query = f'site:{agency["도메인"]} ("Artificial Intelligence" OR AI OR ICT OR "Digital Policy")'
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

        try:
            feed = feedparser.parse(rss_url)
            count = 0

            for entry in feed.entries:
                if count >= 3: break 
                
                title_en = entry.title.split(' - ')[0]
                
                # 링크 해독
                try:
                    decoded = gnewsdecoder(entry.link)
                    actual_link = decoded.get('decoded_url', entry.link)
                except:
                    actual_link = entry.link

                # 발행일 처리
                pub_date = "N/A"
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:3]).strftime('%Y-%m-%d')

                # 번역 처리
                try:
                    title_ko = title_en if agency['국가'] == "대한민국" else translator.translate(title_en.strip(), dest='ko').text
                except:
                    title_ko = title_en
                
                all_final_data.append({
                    "국가": agency["국가"],
                    "기관": agency["기관"],
                    "발행일": pub_date,
                    "제목": title_ko,
                    "원문": title_en,
                    "링크": actual_link,
                    "수집일": collected_date
                })
                count += 1

            time.sleep(1.5) # 차단 방지를 위해 시간을 약간 더 늘렸습니다.

        except Exception as e:
            print(f"❌ {agency['기관']} 오류: {e}")

    # 💾 결과 저장
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["국가", "기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        writer.writerows(all_final_data)
        
    print(f"\n✅ 수집 완료! {len(all_final_data)}건 저장 완료.")

if __name__ == "__main__":
    main()
