import feedparser
import csv
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 구글 뉴스 대신 OECD 공식 뉴스 피드를 직접 타겟팅
    # OECD는 주제별 피드를 제공하므로 훨씬 정확합니다.
    oecd_rss_url = "https://www.oecd.org/en/news/news-rss.xml"
    
    file_name = 'oecd_ai_intelligence.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"📡 OECD 공식 뉴스룸에서 AI 리포트 직접 수집 시작...")
    raw_data = []

    try:
        feed = feedparser.parse(oecd_rss_url)
        print(f"🔍 총 {len(feed.entries)}개의 최신 뉴스 분석 중...")

        for entry in feed.entries:
            title_en = entry.title
            link = entry.link
            
            # AI 관련 키워드 필터링 (제목 또는 요약문 기준)
            description = entry.get('summary', '').upper()
            keywords = ['AI', 'ARTIFICIAL INTELLIGENCE', 'GENERATIVE AI', 'ALGORITHM']
            
            if any(kw in title_en.upper() for kw in keywords) or any(kw in description for kw in keywords):
                # 날짜 처리
                if hasattr(entry, 'published_parsed'):
                    pub_dt = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed'):
                    pub_dt = datetime(*entry.updated_parsed[:6])
                else:
                    pub_dt = datetime.now()

                raw_data.append({
                    "기관": "OECD",
                    "발행일": pub_dt.strftime('%Y-%m-%d'),
                    "dt_obj": pub_dt,
                    "제목_en": title_en,
                    "링크": link
                })

        # 1️⃣ 최신순 정렬
        raw_data.sort(key=lambda x: x['dt_obj'], reverse=True)

        # 2️⃣ 최상위 5개 선택 및 번역
        final_data = []
        for item in raw_data[:5]:
            try:
                title_ko = translator.translate(item['제목_en'].strip(), dest='ko').text
            except:
                title_ko = item['제목_en']
            
            final_data.append({
                "기관": "OECD",
                "발행일": item['발행일'],
                "제목": title_ko,
                "원문": item['제목_en'],
                "링크": item['링크'],
                "수집일": collected_date
            })

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    # 💾 결과 저장
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        if final_data:
            writer.writerows(final_data)
            print(f"✅ 성공! OECD 공식 원본 링크 {len(final_data)}건 저장 완료.")
        else:
            print("⚠️ 현재 OECD 뉴스피드에 AI 관련 최신 소식이 없습니다.")

if __name__ == "__main__":
    main()
