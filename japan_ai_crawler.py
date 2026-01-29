import feedparser
import csv
import os
from datetime import datetime

def main():
    # 🎯 일본 내각부 보도발표 RSS 피드 주소 (가장 정확한 데이터 소스)
    rss_url = "https://www.cao.go.jp/houdou/houdou.rdf"
    file_name = 'japan_ai_report.csv'
    
    print(f"📡 [일본 내각부] RSS 피드 데이터 수집 시작...")

    try:
        # RSS 피드 읽기
        feed = feedparser.parse(rss_url)
        
        new_data = []
        existing_titles = set()
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader: existing_titles.add(row['제목'])

        # AI 관련 키워드 (제한 없이 다 가져오려면 ['']로 설정)
        ai_keywords = ['AI', '人工知能', 'デジタル', '戦略', '技術', '']

        count = 0
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            # 발행일 추출 (피드마다 형식이 다르므로 안전하게 처리)
            published = entry.get('published', datetime.now().strftime("%Y-%m-%d"))

            # 💡 필터링: 제목에 키워드가 있고 중복이 아닐 때
            if any(kw in title.upper() for kw in ai_keywords):
                if title not in existing_titles:
                    print(f"   🆕 뉴스 발견: {title[:40]}...")
                    new_data.append({
                        "기관": "일본 내각부(CAO)",
                        "발행일": published,
                        "제목": title,
                        "링크": link,
                        "수집일": datetime.now().strftime("%Y-%m-%d")
                    })
                    count += 1
                    if count >= 5: break

        # 💾 결과 저장
        if new_data:
            file_exists = os.path.exists(file_name)
            with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "링크", "수집일"])
                if not file_exists: writer.writeheader()
                writer.writerows(new_data)
            print(f"✅ 성공! RSS를 통해 {len(new_data)}건의 진짜 뉴스를 수집했습니다.")
        else:
            print("💡 새로운 소식이 없습니다.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    main()
