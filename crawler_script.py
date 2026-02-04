import feedparser
import csv
import urllib.parse
import time
from datetime import datetime
from googletrans import Translator
from googlenewsdecoder import gnewsdecoder

def get_config_by_country(country):
    """국가별 구글 뉴스 언어(hl) 및 지역(gl) 파라미터 설정"""
    configs = {
        "대한민국": {"hl": "ko", "gl": "KR"},
        "일본": {"hl": "ja", "gl": "JP"},
        "중국": {"hl": "zh-CN", "gl": "CN"},
        "대만": {"hl": "zh-TW", "gl": "TW"},
        "프랑스": {"hl": "fr", "gl": "FR"},
        "독일": {"hl": "de", "gl": "DE"},
        "오스트리아": {"hl": "de", "gl": "AT"},
        "네덜란드": {"hl": "nl", "gl": "NL"},
        "노르웨이": {"hl": "no", "gl": "NO"},
        "스웨덴": {"hl": "sv", "gl": "SE"},
        "덴마크": {"hl": "da", "gl": "DK"},
        "핀란드": {"hl": "fi", "gl": "FI"},
        "이스라엘": {"hl": "he", "gl": "IL"},
        "UAE": {"hl": "ar", "gl": "AE"},
        "사우디": {"hl": "ar", "gl": "SA"},
        "벨기에": {"hl": "nl", "gl": "BE"} # 벨기에는 네덜란드어/프랑스어 중 선택 가능
    }
    return configs.get(country, {"hl": "en-US", "gl": "US"})

def get_localized_query(agency):
    """국가별 현지어 키워드 최적화"""
    country = agency['국가']
    domain = agency['도메인']
    
    keywords = {
        "대한민국": '("인공지능" OR AI OR "디지털" OR "데이터")',
        "일본": '("人工知能" OR AI OR "デジタル政策" OR "ICT")',
        "중국": '("人工智能" OR AI OR "数字化" OR "通信")',
        "대만": '("人工智能" OR AI OR "數位化" OR "資通訊")',
        "독일": '("Künstliche Intelligenz" OR KI OR "Digitalisierung")',
        "오스트리아": '("Künstliche Intelligenz" OR KI OR "Digitalisierung")',
        "프랑스": '("Intelligence Artificielle" OR IA OR "Numérique")',
        "네덜란드": '("Kunstmatige Intelligentie" OR AI OR "Digitalisering")',
        "벨기에": '("Kunstmatige Intelligentie" OR AI OR "Digitalisering")'
    }
    kw = keywords.get(country, '("Artificial Intelligence" OR AI OR "Digital Policy" OR ICT)')
    return f'site:{domain} {kw}'

def main():
    # 🎯 50개 기관 전체 리스트
    gov_agencies = [
        {"국가": "미국", "기관": "백악관", "도메인": "whitehouse.gov"},
        {"국가": "미국", "기관": "DOC", "도메인": "commerce.gov"},
        {"국가": "미국", "기관": "NTIA", "도메인": "ntia.gov"},
        {"국가": "중국", "기관": "CAC", "도메인": "cac.gov.cn"},
        {"국가": "중국", "기관": "MIIT", "도메인": "miit.gov.cn"},
        {"국가": "대한민국", "기관": "과학기술정보통신부", "도메인": "msit.go.kr"},
        {"국가": "대한민국", "기관": "산업통상자원부", "도메인": "motie.go.kr"},
        {"국가": "싱가포르", "기관": "MDDI", "도메인": "mddi.gov.sg"},
        {"국가": "싱가포르", "기관": "IMDA", "도메인": "imda.gov.sg"},
        {"국가": "독일", "기관": "BMDV", "도메인": "bmdv.bund.de"},
        {"국가": "독일", "기관": "BMWK", "도메인": "bmwk.de"},
        {"국가": "일본", "기관": "MIC", "도메인": "soumu.go.jp"},
        {"국가": "일본", "기관": "디지털청", "도메인": "digital.go.jp"},
        {"국가": "일본", "기관": "METI", "도메인": "meti.go.jp"},
        {"국가": "영국", "기관": "DSIT", "도메인": "gov.uk/government/organisations/department-for-science-innovation-and-technology"},
        {"국가": "영국", "기관": "DBT", "도메인": "gov.uk/government/organisations/department-for-business-and-trade"},
        {"국가": "네덜란드", "기관": "EZK", "도메인": "government.nl"},
        {"국가": "네덜란드", "기관": "Digitalisation", "도메인": "nldigitalgovernment.nl"},
        {"국가": "스웨덴", "기관": "Finance", "도메인": "government.se/government-of-sweden/ministry-of-finance"},
        {"국가": "스웨덴", "기관": "Climate", "도메인": "government.se/government-of-sweden/ministry-of-climate-and-enterprise"},
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
        {"국가": "이스라엘", "기관": "Economy", "도메인": "gov.il/en/departments/ministry_of_economy"},
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
    seen_titles = set()
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    
    # 🛡️ 강력한 노이즈 필터 (영문/현지어 대응)
    noise_keywords = ["HOMEPAGE", "PRESS RELEASES", "NEWS", "ABOUT", "CONTACT", "SEARCH", "LOGIN", "TOP PAGE", "HOME", "ARCHIVE"]

    print(f"📡 {collected_date} 글로벌 50개 기관 현지어 강화 수집 시작...")

    for agency in gov_agencies:
        config = get_config_by_country(agency['국가'])
        query = get_localized_query(agency)
        encoded_query = urllib.parse.quote(query)
        
        # 국가별 hl(언어), gl(지역) 파라미터 적용
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl={config['hl']}&gl={config['gl']}&ceid={config['gl']}:{config['hl']}"

        try:
            feed = feedparser.parse(rss_url)
            count = 0

            for entry in feed.entries:
                if count >= 3: break # 기관당 최대 3건
                
                raw_title = entry.title.split(' - ')[0].strip()
                
                # 1. 중복 및 노이즈 필터
                if raw_title in seen_titles or any(noise in raw_title.upper() for noise in noise_keywords):
                    continue
                if len(raw_title.split()) < 2: continue

                # 2. 날짜 필터 (2024년 이후)
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    if entry.published_parsed[0] < 2024: continue
                    pub_date = datetime(*entry.published_parsed[:3]).strftime('%Y-%m-%d')
                else:
                    continue

                # 3. 링크 해독
                try:
                    decoded = gnewsdecoder(entry.link)
                    actual_link = decoded.get('decoded_url', entry.link)
                except:
                    actual_link = entry.link

                # 4. 한국어 번역
                try:
                    title_ko = raw_title if agency['국가'] == "대한민국" else translator.translate(raw_title, dest='ko').text
                except:
                    title_ko = raw_title
                
                all_final_data.append({
                    "국가": agency["국가"], "기관": agency["기관"], "발행일": pub_date,
                    "제목": title_ko, "원문": raw_title, "링크": actual_link, "수집일": collected_date
                })
                seen_titles.add(raw_title)
                count += 1
            
            print(f"✅ [{agency['국가']}] {agency['기관']} 완료")
            time.sleep(1.2) # 구글 차단 방지

        except Exception as e:
            print(f"❌ {agency['기관']} 수집 실패: {e}")

    # 5. 최신 발행일 순으로 전체 정렬
    all_final_data.sort(key=lambda x: x['발행일'], reverse=True)

    # 6. CSV 저장
    file_name = f'global_ict_comprehensive_{collected_date}.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["국가", "기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        writer.writerows(all_final_data)
        
    print(f"\n🚀 전체 수집 완료! 총 {len(all_final_data)}개의 정제된 데이터가 '{file_name}'에 저장되었습니다.")

if __name__ == "__main__":
    main()
