import feedparser
import csv
import urllib.parse
import time
from datetime import datetime
from googletrans import Translator
from googlenewsdecoder import gnewsdecoder

def main():
    # 🎯 1. 대표님이 주신 정부기관 전체 리스트 (도메인 기반)
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
        {"국가": "영국", "기관": "DSIT", "도메인": "gov.uk/government/organisations/department-for-science-innovation-and-technology"},
        {"국가": "영국", "기관": "DBT", "도메인": "gov.uk/government/organisations/department-for-business-and-trade"},
        {"국가": "네덜란드", "기관": "EZK", "도메인": "government.nl/ministries/ministry-of-economic-affairs-and-climate-policy"},
        {"국가": "네덜란드", "기관": "Ministry of Digitalisation", "도메인": "nldigitalgovernment.nl"},
        {"국가": "스웨덴", "기관": "Ministry of Finance", "도메인": "government.se/government-of-sweden/ministry-of-finance"},
        {"국가": "스웨덴", "기관": "Ministry of Climate and Enterprise", "도메인": "government.se/government-of-sweden/ministry-of-climate-and-enterprise"},
        {"국가": "핀란드", "기관": "LVM", "도메인": "lvm.fi"},
        {"국가": "핀란드", "기관": "MEE", "도메인": "tem.fi"},
        {"국가": "스위스", "기관": "OFCOM", "도메인": "bakom.admin.ch"},
        {"국가": "스위스", "기관": "WBF", "도메인": "wbf.admin.ch"},
        {"국가": "덴마크", "기관": "Digitaliseringsstyrelsen", "도메인": "digst.dk"},
        {"국가": "덴마크", "기관": "Erhvervsministeriet", "도메인": "em.dk"},
        {"국가": "노르웨이", "기관": "KDD", "도메인": "regjeringen.no/en/dep/kdd"},
        {"국가": "노르웨이", "기관": "NFD", "도메인": "regjeringen.no/en/dep/nfd"},
        {"국가": "이스라엘", "기관": "IIA", "도메인": "innovationisrael.org.il"},
        {"국가": "이스라엘", "기관": "MoC", "도메인": "gov.il/en/departments/ministry_of_communications"},
        {"국가": "이스라엘", "기관": "Ministry of Economy", "도메인": "gov.il/en/departments/ministry_of_economy"},
        {"국가": "캐나다", "기관": "ISED", "도메인": "ised-isde.canada.ca"},
        {"국가": "캐나다", "기관": "TBS", "도메인": "canada.ca/en/treasury-board-secretariat"},
        {"국가": "프랑스", "기관": "Bercy", "도메인": "economie.gouv.fr"},
        {"국가": "프랑스", "기관": "DG Entreprises", "도메인": "entreprises.gouv.fr"},
        {"국가": "호주", "기관": "DITRDCA", "도메인": "infrastructure.gov.au"},
        {"국가": "호주", "기관": "DISR", "도메인": "industry.gov.au"},
        {"국가": "아일랜드", "기관": "DECC", "도메인": "gov.ie/en/organisation/department-of-the-environment-climate-and-communications"},
        {"국가": "아일랜드", "기관": "DETE", "도메인": "enterprise.gov.ie"},
        {"국가": "오스트리아", "기관": "BMF", "도메인": "bmf.gv.at"},
        {"국가": "오스트리아", "기관": "BMAW", "도메인": "bmwet.gv.at"},
        {"국가": "벨기에", "기관": "연방혁신기술부", "도메인": "belspo.be"},
        {"국가": "벨기에", "기관": "BIPT", "도메인": "bipt.be"},
        {"국가": "벨기에", "기관": "FPS Economy", "도메인": "economie.fgov.be"},
        {"국가": "대만", "기관": "moda", "도메인": "moda.gov.tw"},
        {"국가": "대만", "기관": "MOEA", "도메인": "moea.gov.tw"},
        {"국가": "UAE", "기관": "TDRA", "도메인": "tdra.gov.ae"},
        {"국가": "UAE", "기관": "MoIAT", "도메인": "moiat.gov.ae"},
        {"국가": "사우디", "기관": "MCIT", "도메인": "mcit.gov.sa"},
        {"국가": "사우디", "기관": "MIM", "도메인": "mim.gov.sa"}
    ]

    all_final_data = []
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    file_name = f'global_gov_ai_intelligence_{collected_date}.csv'

    print(f"📡 총 {len(gov_agencies)}개 정부기관 AI 데이터 수집을 시작합니다...")

    for agency in gov_agencies:
        print(f"🔍 [{agency['국가']}] {agency['기관']} 탐색 중...")
        
        # 🎯 검색 쿼리 구성 (해당 도메인 내 AI 관련 핵심 키워드)
        query = f'site:{agency["도메인"]} (intitle:"Artificial Intelligence" OR intitle:AI OR intitle:Algorithm)'
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

        try:
            feed = feedparser.parse(rss_url)
            count = 0

            for entry in feed.entries:
                if count >= 3: break # 기관별 최신 3건만 수집 (효율성)
                
                title_en = entry.title.split(' - ')[0]
                
                # 💡 구글 뉴스 암호 해독
                try:
                    decoded = gnewsdecoder(entry.link)
                    actual_link = decoded.get('decoded_url', entry.link)
                except:
                    actual_link = entry.link

                # 발행일 처리
                pub_date = "N/A"
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d')

                # 번역 (한국 기관은 번역 제외)
                try:
                    if agency['국가'] == "대한민국":
                        title_ko = title_en
                    else:
                        title_ko = translator.translate(title_en.strip(), dest='ko').text
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

            # 과도한 요청 방지를 위한 매너 타임
            time.sleep(1.2)

        except Exception as e:
            print(f"❌ {agency['기관']} 수집 실패: {e}")

    # 💾 CSV 결과 저장
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["국가", "기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        writer.writerows(all_final_data)
        
    print(f"\n✅ 수집 완료! 총 {len(all_final_data)}건의 정책 데이터가 '{file_name}'에 저장되었습니다.")

if __name__ == "__main__":
    main()
