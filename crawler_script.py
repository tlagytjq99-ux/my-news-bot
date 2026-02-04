import feedparser
import csv
import urllib.parse
import time
from datetime import datetime
from googletrans import Translator
from googlenewsdecoder import gnewsdecoder

def check_detailed_keywords(text):
    """대표님이 정의한 13대 상세 분류 체계 (기술 AND 맥락 조합)"""
    t = text.upper()
    
    # [분류 로직] (기술 키워드 리스트, 맥락 키워드 리스트)
    categories = {
        "1-1. 인프라 및 네트워크": (["6G", "5G-ADVANCED", "CLOUD NATIVE"], ["ARCHITECTURE", "STANDARDIZATION", "표준", "구조"]),
        "1-2. 지능형 플랫폼 및 데이터": (["GENERATIVE AI", "LLM", "BIG DATA", "GEN AI"], ["ENTERPRISE", "SOLUTION", "기업", "솔루션"]),
        "1-3. 산업 융합 및 미래 기술": (["ROBOTICS", "HUMANOID", "CONNECTED CAR", "DIGITAL TWIN"], ["INDUSTRY 4.0", "COMMERCIALIZATION", "상용화", "미래"]),
        "2-1. IT 솔루션 및 서비스": (["SAAS", "B2B SOFTWARE", "ITSM"], ["MARKET SHARE", "CLIENT CASE", "점유율", "사례"]),
        "2-2. 통신 인프라 및 단말기": (["TELECOM EQUIPMENT", "SMARTPHONE", "BROADBAND"], ["VENDOR", "INFRASTRUCTURE", "투자", "인프라"]),
        "2-3. 정책 및 거버넌스": (["DIGITAL REGULATION", "AI ACT", "DATA PRIVACY"], ["COMPLIANCE", "GOVERNMENT POLICY", "정부", "정책"]),
        "3-1. 엔터테인먼트 및 플랫폼": (["OTT", "STREAMING", "WEBTOON", "CONTENT"], ["IP", "SUBSCRIPTION", "지식재산", "구독"]),
        "3-2. 광고 및 교육": (["ADTECH", "EDTECH", "LMS"], ["PERSONALIZATION", "ADVERTISING", "개인화", "광고"]),
        "3-3. 플랫폼 및 권리": (["DIGITAL COPYRIGHT", "NFT", "CONTENT PROTECTION"], ["MONETIZATION", "LEGAL CASE", "수익화", "소송"]),
        "4-1. 이동수단 및 항공": (["ELECTRIC VEHICLE", "EV", "UAM", "LOGISTICS"], ["ICT INTEGRATION", "AUTONOMOUS", "통합", "자율"]),
        "4-2. 에너지 및 자원": (["SMART GRID", "ENERGY MANAGEMENT", "RENEWABLE"], ["EFFICIENCY", "SUSTAINABILITY", "효율", "지속가능"]),
        "4-3. 제조 및 기계": (["SMART FACTORY", "INDUSTRIAL IOT", "MAINTENANCE"], ["AUTOMATION", "MANUFACTURING", "자동화", "제조"]),
        "4-4. 생명과학 및 소비재": (["DIGITAL HEALTH", "AGRITECH", "BIOINFORMATICS"], ["AI-DRIVEN", "INNOVATION", "기반", "혁신"])
    }

    for cat, (techs, contexts) in categories.items():
        if any(tech in t for tech in techs) and any(ctx in t for ctx in contexts):
            return cat
    return None

def main():
    # 🎯 대표님의 50개 주요 정책 기관 리스트
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
    
    print(f"📡 {collected_date} 전문 분류 기반 대량 수집 시스템 가동...")

    for agency in gov_agencies:
        # 더 넓은 수집을 위해 검색어 최적화
        query = f"site:{agency['도메인']} (AI OR Digital OR ICT OR Technology OR Policy)"
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=US"

        try:
            feed = feedparser.parse(rss_url)
            collected_count = 0
            for entry in feed.entries:
                if collected_count >= 20: break # 기관당 최대 20건으로 확대 (제한 사실상 해제)
                
                raw_title = entry.title.split(' - ')[0].strip()
                if raw_title in seen_titles: continue

                # 날짜 필터 (2024년 이후)
                if not (hasattr(entry, 'published_parsed') and entry.published_parsed[0] >= 2024): continue
                pub_date = datetime(*entry.published_parsed[:3]).strftime('%Y-%m-%d')

                # 번역 및 분류 판단
                try:
                    title_ko = raw_title if agency['국가'] == "대한민국" else translator.translate(raw_title, dest='ko').text
                except: title_ko = raw_title
                
                # 🚀 핵심: 대표님의 13대 AND 조건 분류 로직 적용
                category = check_detailed_keywords(title_ko + " " + raw_title)
                if not category: continue # 조건에 맞지 않으면 과감히 제외

                try:
                    decoded = gnewsdecoder(entry.link)
                    actual_link = decoded.get('decoded_url', entry.link)
                except: actual_link = entry.link

                all_final_data.append({
                    "국가": agency["국가"], "기관": agency["기관"], "ICT 분류": category,
                    "발행일": pub_date, "제목": title_ko, "원문": raw_title, "링크": actual_link, "수집일": collected_date
                })
                seen_titles.add(raw_title)
                collected_count += 1
            print(f"✅ [{agency['국가']}] {agency['기관']} 완료 ({collected_count}건)")
            time.sleep(0.3)
        except: continue

    # 국가 -> 기관 -> 발행일 순 정렬
    all_final_data.sort(key=lambda x: (x['국가'], x['기관'], x['발행일']))

    file_name = f'Global_ICT_Expert_Report_{collected_date}.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["국가", "기관", "ICT 분류", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        writer.writerows(all_final_data)
        
    print(f"\n🚀 작업 완료! 총 {len(all_final_data)}건의 전문 분류 데이터가 저장되었습니다.")

if __name__ == "__main__":
    main()
