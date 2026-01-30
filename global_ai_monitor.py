import feedparser
import csv
import urllib.parse
from datetime import datetime
from googletrans import Translator
from googlenewsdecoder import gnewsdecoder

def main():
    # 🎯 검색어 보강: 인물 프로필, 팀 소개, 단순 이벤트 페이지 제외 (-)
    target_orgs = {
        "OECD": 'site:oecd.org (intitle:"Artificial Intelligence" OR intitle:AI) -intitle:PISA -intitle:team',
        "IMF": 'site:imf.org (intitle:"Artificial Intelligence" OR intitle:AI) -intitle:biography',
        "UN": 'site:un.org (intitle:"Artificial Intelligence" OR intitle:AI) -intitle:photo',
        "WorldBank": 'site:worldbank.org (intitle:"Artificial Intelligence" OR intitle:AI) -intitle:team -intitle:expert -intitle:profile',
        "EU": 'site:europa.eu (intitle:"Artificial Intelligence" OR intitle:AI) -intitle:directory'
    }

    file_name = 'global_ai_policy_monitor.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    all_data = []

    print(f"🌍 글로벌 AI 정책 모니터링 고도화 시작: {collected_date}")

    for org, query in target_orgs.items():
        print(f"📡 {org} 분석 중...")
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            feed = feedparser.parse(rss_url)
            entries = sorted(feed.entries, key=lambda x: x.get('published_parsed'), reverse=True)
            
            count = 0
            for entry in entries:
                if count >= 3: break
                
                title_en = entry.title.split(' - ')[0]

                # 💡 [필터 추가] 너무 짧은 제목이나 인물 이름만 있는 경우 건너뛰기
                if len(title_en.split()) <= 2: 
                    continue
                
                # 링크 해독
                try:
                    decoded = gnewsdecoder(entry.link)
                    link = decoded.get('decoded_url', entry.link)
                except:
                    link = entry.link

                # 번역
                try:
                    title_ko = translator.translate(title_en, dest='ko').text
                except:
                    title_ko = title_en

                pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d') if hasattr(entry, 'published_parsed') else collected_date

                all_data.append({
                    "기관": org, "발행일": pub_date, "제목": title_ko,
                    "원문": title_en, "링크": link, "수집일": collected_date
                })
                count += 1
        except Exception as e:
            print(f"⚠️ {org} 처리 중 오류: {e}")

    all_data.sort(key=lambda x: x['발행일'], reverse=True)

    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        writer.writerows(all_data)
        print(f"✅ 필터링 완료! 총 {len(all_data)}건의 핵심 리포트 저장.")

if __name__ == "__main__":
    main()
