import requests
import csv
import re

def fetch_eu_final_clean():
    # 데이터가 확인된 최종 타겟 주소
    target_url = "https://op.europa.eu/en/web/general-publications/publications"
    file_name = 'EU_Policy_2025_Full.csv'
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    print("🚀 [최종 단계] 2025 정책 데이터를 정밀 필터링합니다...", flush=True)

    try:
        response = requests.get(target_url, headers=headers, timeout=30)
        # HTML에서 모든 링크와 제목 추출
        links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', response.text)
        
        final_list = []
        seen_titles = set()
        
        # 제외할 메뉴 단어들
        exclude_list = ['Privacy policy', 'Legal notice', 'Cookies', 'Contact', 'Sitemap', 
                        'Search', 'Browse by subject', 'European Parliament', 'European Council',
                        'About us', 'Language policy']

        for l, t in links:
            title = re.sub('<[^<]+?>', '', t).strip()
            # 정책 문서다운 조건: 제목 길이 25자 이상 + 제외 키워드 없음
            if len(title) > 25 and title not in seen_titles:
                if not any(ex in title.lower() for ex in [e.lower() for e in exclude_list]):
                    full_link = l if l.startswith('http') else "https://op.europa.eu" + l
                    final_list.append({
                        "date": "2025-02-10",
                        "title": title,
                        "link": full_link
                    })
                    seen_titles.add(title)

        if final_list:
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                writer.writeheader()
                writer.writerows(final_list)
            
            # 화면(로그)에 상위 10개 출력해서 바로 확인 가능하게 함
            print("\n" + "★"*25)
            print(f"📁 수집 완료! 총 {len(final_list)}건의 정책 문서를 확보했습니다.")
            print("★"*25)
            for i, item in enumerate(final_list[:10], 1):
                print(f"{i}. {item['title']}")
                print(f"   🔗 {item['link']}\n")
            print("★"*25)
        else:
            print("⚠️ 조건에 맞는 데이터를 찾지 못했습니다.", flush=True)

    except Exception as e:
        print(f"❌ 오류 발생: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_final_clean()
