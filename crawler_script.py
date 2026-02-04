import feedparser
import csv
import urllib.parse
import time
from datetime import datetime
from googletrans import Translator
from googlenewsdecoder import gnewsdecoder

def get_config_by_country(country):
    configs = {
        "대한민국": {"hl": "ko", "gl": "KR"},
        "일본": {"hl": "ja", "gl": "JP"},
        "중국": {"hl": "zh-CN", "gl": "CN"},
        "대만": {"hl": "zh-TW", "gl": "TW"},
        "프랑스": {"hl": "fr", "gl": "FR"},
        "독일": {"hl": "de", "gl": "DE"},
        "네덜란드": {"hl": "nl", "gl": "NL"},
        "핀란드": {"hl": "fi", "gl": "FI"},
        "이스라엘": {"hl": "he", "gl": "IL"},
        "UAE": {"hl": "ar", "gl": "AE"},
        "사우디": {"hl": "ar", "gl": "SA"}
    }
    return configs.get(country, {"hl": "en-US", "gl": "US"})

def main():
    # 🎯 50개 기관 리스트 (전체 포함 필수)
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
        {"국가": "스웨덴", "기관": "Finance", "도메인": "government.se"},
        {"국가": "핀란드", "기관": "LVM", "도메인": "lvm.fi"},
        {"국가": "핀란드", "기관": "MEE", "도메인": "tem.fi"},
        {"국가": "스위스", "기관": "OFCOM", "도메인": "bakom.admin.ch"},
        {"국가": "덴마크", "기관": "DIGST", "도메인": "digst.dk"},
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
    seen_titles = set()
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    
    # 🚫 노이즈 차단 목록 (강화)
    exclude_keywords = [
        "게시판 인쇄", "로그인", "LOGIN", "SEARCH", "RECRUITMENT", "채용", "採用", 
        "CONTACT US", "ABOUT US", "홈페이지", "HOME", "FAQ", "Q&A", "FORM", 
        "비밀번호", "PASSWORD", "SIGN IN", "SIGN UP", "OFFICIAL SITE"
    ]

    # ✅ 필수 기술 키워드 (이 단어들이 있어야 정책으로 간주)
    must_include = ["AI", "인공지능", "디지털", "DIGITAL", "ICT", "DATA", "데이터", "POLICY", "정책", "STRATEGY", "전략"]

    print(f"📡 {collected_date} 기관별 정렬 및 필터링 수집 가동...")

    for agency in gov_agencies:
        config = get_config_by_country(agency['국가'])
        query = f"site:{agency['도메인']} (AI OR Digital OR ICT)"
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl={config['hl']}&gl={config['gl']}&ceid={config['gl']}:{config['hl']}"

        try:
            feed = feedparser.parse(rss_url)
            collected_count = 0
            
            for entry in feed.entries:
                if collected_count >= 2: break 
                
                raw_title = entry.title.split(' - ')[0].strip()
                upper_title = raw_title.upper()
                
                # [필터] 중복, 노이즈, 키워드 미포함 시 패스
                if raw_title in seen_titles: continue
                if any(ex in upper_title for ex in exclude_keywords): continue
                if not any(must in upper_title for must in must_include): continue

                # [필터] 날짜 (2024년 이후만)
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_year = entry.published_parsed[0]
                    if pub_year < 2024: continue
                    pub_date = datetime(*entry.published_parsed[:3]).strftime('%Y-%m-%d')
                else: continue

                # 원본 링크 디코딩
                try:
                    decoded = gnewsdecoder(entry.link)
                    actual_link = decoded.get('decoded_url', entry.link)
                except: actual_link = entry.link

                # 번역
                try:
                    title_ko = raw_title if agency['국가'] == "대한민국" else translator.translate(raw_title, dest='ko').text
                except: title_ko = raw_title
                
                all_final_data.append({
                    "국가": agency["국가"], "기관": agency["기관"], "발행일": pub_date,
                    "제목": title_ko, "원문": raw_title, "링크": actual_link, "수집일": collected_date
                })
                seen_titles.add(raw_title)
                collected_count += 1
            
            print(f"✅ [{agency['국가']}] {agency['기관']} 완료")
            time.sleep(0.5)
        except: continue

    # 🗂️ 핵심 수정: 국가별 -> 기관별 가나다순 정렬
    all_final_data.sort(key=lambda x: (x['국가'], x['기관'], x['발행일']), reverse=False)

    file_name = f'global_ict_report_sorted_{collected_date}.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["국가", "기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        writer.writerows(all_final_data)
        
    print(f"\n🚀 정렬 완료! '{file_name}' 파일을 확인해 보세요.")

if __name__ == "__main__":
    main()
