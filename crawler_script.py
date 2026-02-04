import feedparser
import csv
import urllib.parse
import time
from datetime import datetime
from googletrans import Translator
from googlenewsdecoder import gnewsdecoder

# 🎯 핵심 기술 카테고리별 타겟 쿼리 정의
TECH_CATEGORIES = {
    "1. AI/데이터": "(AI OR 'Artificial Intelligence' OR 'Generative AI' OR 'LLM' OR '인공지능' OR '초거대')",
    "2. 반도체/제조": "(Semiconductor OR Chips OR '반도체' OR '파운드리')",
    "3. 통신/6G/인프라": "(6G OR 5G OR 'Network' OR 'Spectrum' OR 'Cloud' OR '주파수' OR '클라우드')",
    "4. 사이버보안": "(Cybersecurity OR 'Cyber Security' OR 'Data Privacy' OR '보안' OR '개인정보')"
}

def main():
    # 대표님이 주신 50개 기관 리스트
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
    seen_links = set()
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"🚀 [인텔리전스 모드] 50개 기관 X 4개 카테고리 심층 수집 시작...")

    for agency in gov_agencies:
        print(f"📡 {agency['국가']} - {agency['기관']} 스캔 중...")
        
        for cat_name, cat_query in TECH_CATEGORIES.items():
            # 기관 도메인별 + 카테고리별 쿼리 생성
            query = f"site:{agency['도메인']} {cat_query}"
            hl = "ko" if agency['국가'] == "대한민국" else "en"
            gl = "KR" if agency['국가'] == "대한민국" else "US"
            
            encoded_query = urllib.parse.quote(query)
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl={hl}&gl={gl}"

            try:
                feed = feedparser.parse(rss_url)
                # 각 카테고리별로 가장 최신 1건만 채택
                for entry in feed.entries[:1]:
                    raw_title = entry.title.split(' - ')[0].strip()
                    # 2024년 이후 데이터만 허용
                    if not (hasattr(entry, 'published_parsed') and entry.published_parsed[0] >= 2024): continue
                    
                    link = entry.link
                    if link in seen_links: continue

                    pub_date = datetime(*entry.published_parsed[:3]).strftime('%Y-%m-%d')
                    
                    # 제목 번역 (한국어 제외)
                    try:
                        title_ko = raw_title if agency['국가'] == "대한민국" else translator.translate(raw_title, dest='ko').text
                    except: title_ko = raw_title

                    # 링크 디코딩
                    try:
                        decoded = gnewsdecoder(link)
                        actual_link = decoded.get('decoded_url', link)
                    except: actual_link = link

                    all_final_data.append({
                        "국가": agency["국가"], "기관": agency["기관"], "상세분류": cat_name,
                        "발행일": pub_date, "제목": title_ko, "원문": raw_title, "링크": actual_link, "수집일": collected_date
                    })
                    seen_links.add(link)
                
                # 구글 뉴스 API 부하 방지 (안정성 확보)
                time.sleep(0.8)
            except Exception as e:
                print(f"   ㄴ {cat_name} 수집 실패: {e}")
                continue

    file_name = f'Global_Deep_ICT_Matrix_{collected_date}.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["국가", "기관", "상세분류", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        writer.writerows(all_final_data)
        
    print(f"\n✅ 매트릭스 리포트 생성 완료! 총 {len(all_final_data)}건의 핵심 정책이 수집되었습니다.")
    print(f"📂 파일명: {file_name}")

if __name__ == "__main__":
    main()
