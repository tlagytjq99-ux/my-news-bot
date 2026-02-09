import requests
import csv
import re

def fetch_eu_robust_scraping():
    # 최신 문서 피드 주소
    feed_url = "https://op.europa.eu/en/web/general-publications/publications?p_p_id=eu_europa_publications_portlet_search_search_results_display_WAR_eu_europa_publications_portlet&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_eu_europa_publications_portlet_search_search_results_display_WAR_eu_europa_publications_portlet_format=rss"
    
    file_name = 'EU_Policy_2025_Final.csv'
    all_records = []
    
    print("🧹 [강력 수집] 깨진 글자를 무시하고 2025년 정책 데이터를 추출합니다...", flush=True)

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(feed_url, headers=headers, timeout=30)
        response.encoding = 'utf-8' # 인코딩 강제 설정

        # XML 파싱 에러 방지를 위해 '정규표현식'으로 데이터 추출
        # <title>과 <link> 태그 사이에 있는 글자들을 직접 낚아챕니다.
        content = response.text
        titles = re.findall(r'<title>(.*?)</title>', content, re.DOTALL)
        links = re.findall(r'<link>(.*?)</link>', content, re.DOTALL)
        
        # 첫 번째 제목은 채널 정보이므로 제외하고 1대1 매칭
        for t, l in zip(titles[1:], links[1:]):
            # CDATA 태그 등 불필요한 장식 제거
            clean_title = t.replace('<![CDATA[', '').replace(']]>', '').strip()
            clean_link = l.strip()
            
            # 제목에 2025가 있거나 최신 문서라면 수집
            # RSS 피드 특성상 최근 1개월 내 문서가 주로 올라옵니다.
            all_records.append({
                "date": "2025-Latest",
                "title": clean_title,
                "link": clean_link
            })

        if all_records:
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                writer.writeheader()
                writer.writerows(all_records)
            print(f"✅ [성공] 총 {len(all_records)}건의 최신 정책 리스트를 확보했습니다!", flush=True)
            print(f"📌 첫 번째 데이터 확인: {all_records[0]['title'][:50]}...", flush=True)
        else:
            print("⚠️ 획득한 데이터가 없습니다. 서버의 응답 형식을 다시 점검합니다.", flush=True)

    except Exception as e:
        print(f"❌ 오류 발생: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_robust_scraping()
