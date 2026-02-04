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
        "오스트리아": {"hl": "de", "gl": "AT"},
        "네덜란드": {"hl": "nl", "gl": "NL"},
        "노르웨이": {"hl": "no", "gl": "NO"},
        "스웨덴": {"hl": "sv", "gl": "SE"},
        "덴마크": {"hl": "da", "gl": "DK"},
        "핀란드": {"hl": "fi", "gl": "FI"},
        "이스라엘": {"hl": "he", "gl": "IL"},
        "UAE": {"hl": "ar", "gl": "AE"},
        "사우디": {"hl": "ar", "gl": "SA"},
        "벨기에": {"hl": "nl", "gl": "BE"}
    }
    return configs.get(country, {"hl": "en-US", "gl": "US"})

def get_localized_query(agency):
    country = agency['국가']
    domain = agency['도메인']
    keywords = {
        "대한민국": '("인공지능" OR AI OR "디지털" OR "데이터")',
        "일본": '("人工知能" OR AI OR "デジタル政策" OR "ICT")',
        "중국": '("人工智能" OR AI OR "数字化" OR "通信")',
        "대만": '("人工智能" OR AI OR "數位化" OR "資通訊")',
        "독일": '("Künstliche Intelligenz" OR KI OR "Digitalisierung")',
        "프랑스": '("Intelligence Artificielle" OR IA OR "Numérique")',
        "네덜란드": '("Kunstmatige Intelligentie" OR AI OR "Digitalisering")'
    }
    kw = keywords.get(country, '("Artificial Intelligence" OR AI OR "Digital Policy" OR ICT)')
    return f'site:{domain} {kw}'

def main():
    # 50개 기관 리스트 (이전과 동일하여 중략, 실제 코드 실행 시 전체 포함 필요)
    gov_agencies = [
        {"국가": "미국", "기관": "백악관", "도메인": "whitehouse.gov"},
        {"국가": "대한민국", "기관": "과학기술정보통신부", "도메인": "msit.go.kr"},
        {"국가": "일본", "기관": "디지털청", "도메인": "digital.go.jp"},
        # ... (이하 50개 기관 리스트)
    ]

    all_final_data = []
    seen_titles = set()
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    
    # 🚫 노이즈 필터링 키워드 강화 (한국어 및 주요 외국어 포함)
    exclude_keywords = [
        "게시판 인쇄", "장관 소개", "채용", "공고", "인사", "로그인", "홈페이지", "찾아오시는", 
        "RECRUITMENT", "LOGIN", "SEARCH", "ABOUT US", "CONTACT", "Q&A", "CV ", "PHOTO GALLERY",
        "採用", "募集", "ログイン", "お問い合わせ", "OFFRE D'EMPLOI", "RECRUTEMENT"
    ]
    
    # ✅ 필수 포함 키워드 (이 중 하나라도 없으면 탈락시켜 정확도 향상)
    must_include = ["AI", "인공지능", "디지털", "데이터", "ICT", "통신", "혁신", "규제", "STRATEGY", "POLICY", "DIGITAL", "DATA"]

    print(f"📡 {collected_date} 고순도 글로벌 정책 수집 가동...")

    for agency in gov_agencies:
        config = get_config_by_country(agency['국가'])
        query = get_localized_query(agency)
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl={config['hl']}&gl={config['gl']}&ceid={config['gl']}:{config['hl']}"

        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:5]: # 상위 5개 확인
                raw_title = entry.title.split(' - ')[0].strip()
                
                # 1. 중복 제거
                if raw_title in seen_titles: continue
                
                # 2. 제외 키워드 필터 (노이즈 제거)
                if any(ex in raw_title.upper() for ex in exclude_keywords): continue
                
                # 3. 제목 길이 필터 (너무 짧은 메뉴명 등 제거)
                if len(raw_title) < 12: continue

                # 4. 날짜 필터 (2025년 이후 데이터 우선)
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    if entry.published_parsed[0] < 2024: continue
                    pub_date = datetime(*entry.published_parsed[:3]).strftime('%Y-%m-%d')
                else: continue

                # 5. 한국어 번역
                try:
                    title_ko = raw_title if agency['국가'] == "대한민국" else translator.translate(raw_title, dest='ko').text
                except: title_ko = raw_title

                # 6. 번역본 기반 필수 키워드 검증 (한 번 더 필터링)
                if not any(word in title_ko.upper() for word in must_include): continue

                # 7. 링크 해독
                try:
                    decoded = gnewsdecoder(entry.link)
                    actual_link = decoded.get('decoded_url', entry.link)
                except: actual_link = entry.link

                all_final_data.append({
                    "국가": agency["국가"], "기관": agency["기관"], "발행일": pub_date,
                    "제목": title_ko, "원문": raw_title, "링크": actual_link, "수집일": collected_date
                })
                seen_titles.add(raw_title)
            
            time.sleep(1)
        except Exception as e:
            print(f"❌ {agency['기관']} 오류: {e}")

    # 최종 정렬: 최신순
    all_final_data.sort(key=lambda x: x['발행일'], reverse=True)

    # CSV 저장
    file_name = f'global_ict_clean_{collected_date}.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["국가", "기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        writer.writerows(all_final_data)
        
    print(f"✅ 필터링 완료: 총 {len(all_final_data)}건의 고순도 데이터 저장.")

if __name__ == "__main__":
    main()
