import feedparser
import csv
import urllib.parse
import time
from datetime import datetime
from googletrans import Translator

def get_config_by_country(country):
    """국가별 구글 뉴스 언어(hl) 및 지역(gl) 파라미터"""
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
        "사우디": {"hl": "ar", "gl": "SA"}
    }
    return configs.get(country, {"hl": "en-US", "gl": "US"})

def main():
    # 🎯 50개 기관 전수 조사 리스트
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
        {"국가": "영국", "기관": "DSIT", "도메인": "gov.uk"},
        {"국가": "네덜란드", "기관": "EZK", "도메인": "government.nl"},
        {"국가": "네덜란드", "기관": "Digital", "도메인": "nldigitalgovernment.nl"},
        {"국가": "스웨덴", "기관": "Finance", "도메인": "government.se"},
        {"국가": "핀란드", "기관": "LVM", "도메인": "lvm.fi"},
        {"국가": "핀란드", "기관": "MEE", "도메인": "tem.fi"},
        {"국가": "스위스", "기관": "OFCOM", "도메인": "bakom.admin.ch"},
        {"국가": "스위스", "기관": "WBF", "도메인": "wbf.admin.ch"},
        {"국가": "덴마크", "기관": "DIGST", "도메인": "digst.dk"},
        {"국가": "노르웨이", "기관": "KDD", "도메인": "regjeringen.no"},
        {"국가": "이스라엘", "기관": "IIA", "도메인": "innovationisrael.org.il"},
        {"국가": "캐나다", "기관": "ISED", "도메인": "ised-isde.canada.ca"},
        {"국가": "프랑스", "기관": "Bercy", "도메인": "economie.gouv.fr"},
        {"국가": "프랑스", "기관": "DGE", "도메인": "entreprises.gouv.fr"},
        {"국가": "호주", "기관": "DISR", "도메인": "industry.gov.au"},
        {"국가": "아일랜드", "기관": "DETE", "도메인": "enterprise.gov.ie"},
        {"국가": "오스트리아", "기관": "BMF", "도메인": "bmf.gv.at"},
        {"국가": "벨기에", "기관": "BIPT", "도메인": "bipt.be"},
        {"국가": "대만", "기관": "moda", "도메인": "moda.gov.tw"},
        {"국가": "대만", "기관": "MOEA", "도메인": "moea.gov.tw"},
        {"국가": "UAE", "기관": "TDRA", "도메인": "tdra.gov.ae"},
        {"국가": "사우디", "기관": "MCIT", "도메인": "mcit.gov.sa"}
    ]

    all_final_data = []
    seen_titles = set()
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    
    # 제외 키워드 최소화 (채용 및 로그인만 제외)
    exclude_keywords = ["LOGIN", "SEARCH", "RECRUITMENT", "CONTACT US", "로그인", "채용", "采用"]

    print(f"📡 {collected_date} 글로벌 전수 조사 엔진 가동 (총 {len(gov_agencies)}개 기관)...")

    for agency in gov_agencies:
        config = get_config_by_country(agency['국가'])
        
        # 쿼리를 가장 넓게 잡음 (AI나 디지털이 포함된 모든 소식)
        query = f"site:{agency['도메인']} (AI OR Artificial Intelligence OR Digital OR ICT)"
        encoded_query = urllib.parse.quote(query)
        
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl={config['hl']}&gl={config['gl']}&ceid={config['gl']}:{config['hl']}"

        try:
            feed = feedparser.parse(rss_url)
            count_before = len(all_final_data)
            
            for entry in feed.entries[:10]: # 기관당 최대 10개까지 넉넉히 확인
                raw_title = entry.title.split(' - ')[0].strip()
                
                # 중복 및 최소 노이즈 체크
                if raw_title in seen_titles or any(ex in raw_title.upper() for ex in exclude_keywords):
                    continue

                # 날짜 추출 (실패 시 오늘 날짜)
                pub_date = collected_date
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:3]).strftime('%Y-%m-%d')

                # 번역 (현지어 -> 한국어)
                try:
                    title_ko = raw_title if agency['국가'] == "대한민국" else translator.translate(raw_title, dest='ko').text
                except:
                    title_ko = raw_title
                
                all_final_data.append({
                    "국가": agency["국가"], "기관": agency["기관"], "발행일": pub_date,
                    "제목": title_ko, "원문": raw_title, "링크": entry.link, "수집일": collected_date
                })
                seen_titles.add(raw_title)
            
            added = len(all_final_data) - count_before
            print(f"✅ [{agency['국가']}] {agency['기관']}: {added}건 수집 완료")
            time.sleep(0.5) # 속도를 위해 딜레이 단축

        except Exception as e:
            print(f"❌ {agency['기관']} 연결 실패: {e}")

    # 최신순 정렬
    all_final_data.sort(key=lambda x: x['발행일'], reverse=True)

    # CSV 저장
    file_name = f'global_ict_wide_search_{collected_date}.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["국가", "기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        writer.writerows(all_final_data)
        
    print(f"\n🚀 전체 수집 종료! 총 {len(all_final_data)}건의 데이터가 '{file_name}'에 저장되었습니다.")

if __name__ == "__main__":
    main()
