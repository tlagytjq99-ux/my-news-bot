import feedparser
import csv
import urllib.parse
import time
from datetime import datetime
from googletrans import Translator
from googlenewsdecoder import gnewsdecoder

def is_industry_ict(text):
    """일반 행정/거대 담론을 제외하고 오직 'ICT 산업 기술'에만 집중"""
    t = text.upper()
    
    # ❌ 1. ICT와 무관한 도메인 (에너지, 원자력, 청소년, 노동, 보건 일반 등)
    non_ict_sectors = [
        "NUCLEAR", "REACTOR", "YOUTH", "LABOR", "CLIMATE", "ENERGY", "TRACFIN", 
        "VISA", "ENTRY", "IMMIGRATION", "SOCIAL INSURANCE", "HEALTHCARE", "VACCINE",
        "원자로", "원자력", "청소년", "노동", "기후", "에너지", "사회보험", "비자", "입국", "백신"
    ]
    if any(sector in t for sector in non_ict_sectors):
        return False

    # ✅ 2. 실질적 ICT 핵심 기술 (이 단어들이 제목에 직접 나타나야 함)
    # 단순 'Digital'이나 'ICT' 단독 사용은 필터링 강도를 높이기 위해 제외하거나 조합함
    ict_core_tech = [
        "AI ", "GEN AI", "LLM", "SEMICONDUCTOR", "CHIPS", "6G", "5G", "QUANTUM", 
        "CYBER", "ROBOT", "UAM", "PLATFORM", "SOFTWARE", "SAAS", "DATA CENTER",
        "반도체", "인공지능", "양자", "로봇", "소프트웨어", "데이터센터", "보안", "자율주행"
    ]
    
    # 핵심 기술어가 하나라도 포함되어야 함
    return any(tech in t for tech in ict_core_tech)

def classify_ict_refined(text):
    """13대 정밀 분류 로직"""
    t = text.upper()
    categories = {
        "1-1. 인프라 및 네트워크": ["6G", "5G", "CLOUD", "NETWORK", "데이터센터", "주파수"],
        "1-2. 지능형 플랫폼 및 데이터": ["GENERATIVE AI", "LLM", "BIG DATA", "데이터", "지능형", "GEN AI"],
        "1-3. 산업 융합 및 미래 기술": ["ROBOT", "DIGITAL TWIN", "로봇", "양자", "QUANTUM"],
        "2-1. IT 솔루션 및 서비스": ["SAAS", "B2B", "SOFTWARE", "소프트웨어", "솔루션"],
        "2-2. 통신 인프라 및 단말기": ["TELECOM", "SMARTPHONE", "통신", "단말", "기기"],
        "2-3. 정책 및 거버넌스": ["REGULATION", "AI ACT", "PRIVACY", "규제", "정책", "거버넌스"],
        "3-1. 엔터테인먼트 및 플랫폼": ["OTT", "STREAMING", "WEBTOON", "콘텐츠", "플랫폼"],
        "3-2. 광고 및 교육": ["ADTECH", "EDTECH", "LMS", "교육", "광고"],
        "3-3. 플랫폼 및 권리": ["COPYRIGHT", "NFT", "저작권", "지식재산", "IP"],
        "4-1. 이동수단 및 항공": ["EV", "UAM", "AUTONOMOUS", "자율주행", "모빌리티"],
        "4-2. 에너지 및 자원": ["SMART GRID", "RENEWABLE", "에너지", "그리드"],
        "4-3. 제조 및 기계": ["FACTORY", "IOT", "제조", "반도체", "SEMICONDUCTOR"],
        "4-4. 생명과학 및 소비재": ["HEALTH", "BIO", "헬스케어", "바이오"]
    }
    for cat, keywords in categories.items():
        if any(kw in t for kw in keywords): return cat
    return "기타 ICT 일반"

def main():
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

    print(f"📡 {collected_date} ICT 산업 현안 정밀 수집 모드 가동...")

    for agency in gov_agencies:
        # 검색 쿼리에서 'Policy'나 'Strategy'를 빼고 실제 기술 키워드 중심 검색
        query = f"site:{agency['도메인']} (AI OR Semiconductor OR '6G' OR Cybersecurity OR Quantum)"
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=US"

        try:
            feed = feedparser.parse(rss_url)
            collected_count = 0
            for entry in feed.entries:
                if collected_count >= 1: break 

                raw_title = entry.title.split(' - ')[0].strip()
                if raw_title in seen_titles: continue
                if not (hasattr(entry, 'published_parsed') and entry.published_parsed[0] >= 2024): continue
                
                # 🚀 3차 보정 필터: 산업 기술명이 직접 포함되어야 함
                if not is_industry_ict(raw_title):
                    continue

                pub_date = datetime(*entry.published_parsed[:3]).strftime('%Y-%m-%d')
                try:
                    title_ko = raw_title if agency['국가'] == "대한민국" else translator.translate(raw_title, dest='ko').text
                except: title_ko = raw_title

                category = classify_ict_refined(title_ko + " " + raw_title)
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
            
            print(f"✅ [{agency['국가']}] {agency['기관']} 산업 필터 완료")
            time.sleep(0.3)
        except: continue

    file_name = f'Global_ICT_Industry_Focus_{collected_date}.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["국가", "기관", "ICT 분류", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        writer.writerows(all_final_data)
        
    print(f"\n🚀 작업 완료! 진짜 ICT 뉴스만 담긴 리포트가 '{file_name}'에 저장되었습니다.")

if __name__ == "__main__":
    main()
