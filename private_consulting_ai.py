import feedparser
import csv
import urllib.parse
from datetime import datetime
from googletrans import Translator
from googlenewsdecoder import gnewsdecoder

def main():
    # 🎯 민간 컨설팅사 타겟팅
    # 각 사의 도메인에서 AI 리포트 위주로 수집하며, 채용(career) 정보는 제외합니다.
    target_firms = {
        "McKinsey": 'site:mckinsey.com (intitle:"Artificial Intelligence" OR intitle:AI) -intitle:career',
        "BCG": 'site:bcg.com (intitle:"Artificial Intelligence" OR intitle:AI) -intitle:career',
        "Bain": 'site:bain.com (intitle:"Artificial Intelligence" OR intitle:AI)',
        "GoldmanSachs": 'site:goldmansachs.com (intitle:"Artificial Intelligence" OR intitle:AI)'
    }

    file_name = 'private_consulting_ai_monitor.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")
    all_data = []

    print(f"💼 민간 컨설팅사 AI 리포트 수집 및 해독 시작...")

    for firm, query in target_firms.items():
        print(f"📡 {firm} 분석 중...")
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            feed = feedparser.parse(rss_url)
            # 사별로 최신 3~4건씩 검토
            entries = sorted(feed.entries, key=lambda x: x.get('published_parsed'), reverse=True)[:5]
            
            for entry in entries:
                title_en = entry.title.split(' - ')[0]
                if len(title_en.split()) <= 2: continue

                # 💡 구글 뉴스 암호 해독
                try:
                    decoded = gnewsdecoder(entry.link)
                    link = decoded.get('decoded_url', entry.link)
                except:
                    link = entry.link

                # 💡 PDF 여부 판별
                is_pdf = "YES" if link.lower().endswith('.pdf') or ".pdf?" in link.lower() else "NO"

                # 날짜 및 번역
                pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d') if hasattr(entry, 'published_parsed') else collected_date
                try:
                    title_ko = translator.translate(title_en, dest='ko').text
                except:
                    title_ko = title_en

                all_data.append({
                    "기관": firm,
                    "발행일": pub_date,
                    "제목": f"{'[PDF] ' if is_pdf == 'YES' else ''}{title_ko}",
                    "원문": title_en,
                    "PDF여부": is_pdf,
                    "링크": link,
                    "수집일": collected_date
                })
        except Exception as e:
            print(f"⚠️ {firm} 처리 중 오류: {e}")

    # 최신순 정렬
    all_data.sort(key=lambda x: x['발행일'], reverse=True)

    # 💾 결과 저장
    fieldnames = ["기관", "발행일", "제목", "원문", "PDF여부", "링크", "수집일"]
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_data)
        print(f"✅ 완료! 총 {len(all_data)}건의 민간 인사이트 저장.")

if __name__ == "__main__":
    main()
