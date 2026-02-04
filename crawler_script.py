import feedparser
import csv
import urllib.parse
import time
from datetime import datetime
from googletrans import Translator
from googlenewsdecoder import gnewsdecoder

def classify_ict(title_text):
    """대표님이 정의한 4대 ICT 분류 체계 자동 매핑"""
    t = title_text.upper()
    
    # 1. 융합 및 하이테크 (미래 기술)
    high_tech = ["6G", "5G-ADVANCED", "CLOUD NATIVE", "GENERATIVE AI", "LLM", "BIG DATA", "ROBOTICS", "HUMANOID", "CONNECTED CAR", "DIGITAL TWIN", "AI", "인공지능", "차세대", "하이테크"]
    # 2. IT 및 통신 (전통 IT/정책)
    it_telecom = ["SAAS", "B2B SOFTWARE", "ITSM", "TELECOM", "SMARTPHONE", "BROADBAND", "DIGITAL REGULATION", "AI ACT", "DATA PRIVACY", "거버넌스", "규제", "보안", "보호", "통신"]
    # 3. 콘텐츠 및 저작권
    contents = ["OTT", "STREAMING", "WEBTOON", "IMMERSIVE", "ADTECH", "EDTECH", "DIGITAL COPYRIGHT", "NFT", "저작권", "IP", "플랫폼", "콘텐츠", "미디어"]
    # 4. 수직 산업 (타 산업 융합)
    vertical = ["ELECTRIC VEHICLE", "EV", "UAM", "SMART LOGISTICS", "SMART GRID", "ENERGY MANAGEMENT", "SMART FACTORY", "INDUSTRIAL IOT", "DIGITAL HEALTH", "AGRITECH", "제조", "에너지", "항공", "스마트"]

    if any(kw in t for kw in high_tech): return "1. 융합 및 하이테크"
    elif any(kw in t for kw in contents): return "3. 콘텐츠 및 저작권"
    elif any(kw in t for kw in vertical): return "4. 수직 산업"
    elif any(kw in t for kw in it_telecom): return "2. IT 및 통신"
    else: return "기타 ICT 일반"

def get_config_by_country(country):
    configs = {
        "대한민국": {"hl": "ko", "gl": "KR"}, "일본": {"hl": "ja", "gl": "JP"}, "중국": {"hl": "zh-CN", "gl": "CN"},
        "대만": {"hl": "zh-TW", "gl": "TW"}, "프랑스": {"hl": "fr", "gl": "FR"}, "독일": {"hl": "de", "gl": "DE"},
        "네덜란드": {"hl": "nl", "gl": "NL"}, "핀란드": {"hl": "fi", "gl": "FI"}, "노르웨이": {"hl": "no", "gl": "NO"},
        "스웨덴": {"hl": "sv", "gl": "SE"}, "덴마크": {"hl": "da", "gl": "DK"}, "이스라엘": {"hl": "he", "gl": "IL"},
        "UAE": {"hl": "ar", "gl": "AE"}, "사우디": {"hl": "ar", "gl": "SA"}, "오스트리아": {"hl": "de", "gl": "AT"}
    }
    return configs.get(country, {"hl": "en-US", "gl": "US"})

def main():
    # 🎯 대표님의 50개 주요 정책 기관 리스트 전수 반영
    gov_agencies = [
        {"국가": "미국", "기관": "백악관", "도메인": "whitehouse.gov"}, {"국가": "미국", "기관": "DOC", "도메인": "commerce.gov"},
        {"국가": "미국", "기관": "NTIA", "도메인": "ntia.gov"}, {"국가": "중국", "기관": "CAC", "도메인": "cac.gov.cn"},
        {"국가": "중국", "기관": "MIIT", "도메인": "miit.gov.cn"}, {"국가": "대한민국", "기관": "과학기술정보통신부", "도메인": "msit.go.kr"},
        {"국가": "대한민국", "기관": "산업통상자원부", "도메인": "motie.go.kr"}, {"국가": "싱가포르", "기관": "MDDI", "도메인": "mddi.gov.sg"},
        {"국가": "싱가포르", "기관": "IMDA", "도메인": "imda.gov.sg"}, {"국가": "독일", "기관": "BMDV", "도메인": "bmdv.bund.de"},
        {"국가": "독일", "기관": "BMWK", "도메인": "bmwk.de"}, {"국가": "일본", "기관": "MIC", "도메인": "soumu.go.jp"},
        {"국가": "일본", "기관": "디지털청", "도메인": "digital.go.jp"}, {"국가": "일본", "기관": "METI", "도메인": "meti.go.jp"},
        {"국가": "영국", "기관": "DSIT", "도메인": "gov.uk"}, {"국가": "영국", "기관": "DBT", "도메인": "gov.uk"},
        {"국가": "네덜란드", "기관": "EZK", "도메인": "government.nl"}, {"국가": "네덜란드", "기관": "Digitalisation", "도메인": "nldigitalgovernment.nl"},
        {"국가": "스웨덴", "기관": "Finance", "도메인": "government.se"}, {"국가": "스웨덴", "기관": "Enterprise", "도메인": "government.se"},
        {"국가": "핀란드", "기관": "LVM", "도메인": "lvm.fi"}, {"국가": "핀란드", "기관": "MEE", "도메인": "tem.fi"},
        {"국가": "스위스", "기관": "OFCOM", "도메인": "bakom.admin.ch"}, {"국가": "스위스", "기관": "WBF", "도메인": "wbf.admin.ch"},
        {"국가": "덴마크", "기관": "Digitaliseringsstyrelsen", "도메인": "digst.dk"}, {"국가": "덴마크", "기관": "Erhvervsministeriet", "도메인": "em.dk"},
        {"국가": "노르웨이", "기관": "KDD", "도메인": "regjeringen.no"}, {"국가": "노르웨이", "기관": "NFD", "도메인": "regjeringen.no"},
        {"국가": "이스라엘", "기관": "IIA", "도메인": "innovationisrael.org.il"}, {"국가": "이스라엘", "기관": "MoC", "도메인": "gov.il"},
        {"국가": "이스라엘", "기관": "Economy", "도메인": "gov.il"}, {"국가": "캐나다", "기관": "ISED", "도메인": "ised-isde.canada.ca"},
        {"국가": "캐나다", "기관": "TBS", "도메인": "canada.ca"}, {"국가": "프랑스", "기관": "Bercy", "도메인": "economie.gouv.fr"},
        {"국가": "프랑스", "기관": "DG Entreprises", "도메인": "entreprises.gouv.fr"}, {"국가": "호주", "기관": "DITRDCA", "도메인": "infrastructure.gov.au"},
        {"국가": "호주", "기관": "DISR", "도메인": "industry.gov.au"}, {"국가": "아일랜드", "기관": "DECC", "도메인": "gov.ie"},
        {"국가": "아일랜드", "기관": "DETE", "도메인": "enterprise.gov.ie"}, {"국가": "오스트리아", "기관": "BMF", "도메인": "bmf.gv.at"},
        {"국가": "오스트리아", "기관": "BMAW", "도메인": "bmaw.gv.at"}, {"국가": "벨기에", "기관": "연방혁신기술부", "도메인": "belspo.be"},
        {"국가": "벨기에", "기관": "BIPT", "도메인": "bipt.be"}, {"국가": "벨기에", "기관": "FPS Economy", "도메인": "economie.fgov.be"},
        {"국가": "대만", "기관": "moda", "도메인": "moda.gov.tw"}, {"국가": "대만", "기관": "MOEA", "도메인": "moea.gov.tw"},
        {"국가": "UAE", "기관": "TDRA", "도메인": "tdra.gov.ae"}, {"국가": "UAE", "기관": "MoIAT", "도메인": "moiat.gov.ae"},
        {"국가": "사우디", "기관": "MCIT", "도메인": "mcit.gov.sa"}, {"국가": "사우디", "기관": "MIM", "도메인": "mim.gov.sa"}
    ]

    all_final_data = []
    seen_titles = set()
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    
    # 🚀 수집 필수 키워드 (분류 체계 전문 용어 통합)
    must_include = [
        "AI", "DIGITAL", "ICT", "DATA", "POLICY", "인공지능", "디지털", "데이터", "전략", "기술",
        "6G", "5G", "CLOUD", "LLM", "ROBOT", "UAM", "SAAS", "OTT", "IP", "EV", "보안", "규제",
        "플랫폼", "저작권", "스마트", "제조", "혁신", "네트워크", "SECURITY", "CHIPS", "반도체"
    ]
    exclude_keywords = ["게시판 인쇄", "로그인", "LOGIN", "SEARCH", "RECRUITMENT", "채용", "采用", "FAQ"]

    print(f"📡 {collected_date} 전 세계 50개 부처 ICT 정책 전수 모니터링 가동...")

    for agency in gov_agencies:
        config = get_config_by_country(agency['국가'])
        query = f"site:{agency['도메인']} (AI OR Digital OR ICT OR Tech OR Policy)"
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl={config['hl']}&gl={config['gl']}&ceid={config['gl']}:{config['hl']}"

        try:
            feed = feedparser.parse(rss_url)
            collected_count = 0
            for entry in feed.entries:
                if collected_count >= 2: break 
                raw_title = entry.title.split(' - ')[0].strip()
                if raw_title in seen_titles or any(ex in raw_title.upper() for ex in exclude_keywords): continue

                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    if entry.published_parsed[0] < 2024: continue
                    pub_date = datetime(*entry.published_parsed[:3]).strftime('%Y-%m-%d')
                else: continue

                try:
                    title_ko = raw_title if agency['국가'] == "대한민국" else translator.translate(raw_title, dest='ko').text
                except: title_ko = raw_title
                
                # 하나라도 필수 키워드가 포함되어야 수집
                if not any(word in (title_ko + raw_title).upper() for word in must_include): continue

                ict_category = classify_ict(title_ko + " " + raw_title)
                try:
                    decoded = gnewsdecoder(entry.link)
                    actual_link = decoded.get('decoded_url', entry.link)
                except: actual_link = entry.link

                all_final_data.append({
                    "국가": agency["국가"], "기관": agency["기관"], "ICT 분류": ict_category,
                    "발행일": pub_date, "제목": title_ko, "원문": raw_title, "링크": actual_link, "수집일": collected_date
                })
                seen_titles.add(raw_title)
                collected_count += 1
            print(f"✅ [{agency['국가']}] {agency['기관']} 완료")
            time.sleep(0.5)
        except: continue

    all_final_data.sort(key=lambda x: (x['국가'], x['기관'], x['발행일']))

    file_name = f'Global_ICT_Intelligence_Report_{collected_date}.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["국가", "기관", "ICT 분류", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        writer.writerows(all_final_data)
        
    print(f"\n🚀 작업 종료! 총 {len(all_final_data)}건의 고순도 정책 데이터가 '{file_name}'에 저장되었습니다.")

if __name__ == "__main__":
    main()
