import requests
import csv
import re

def fetch_eu_policy_and_show():
    target_url = "https://op.europa.eu/en/web/general-publications/publications"
    file_name = 'EU_Policy_2025_Final.csv'
    headers = {"User-Agent": "Mozilla/5.0"}

    print("💰 [데이터 확인 중] 수집된 내용을 화면에 출력합니다...", flush=True)

    try:
        response = requests.get(target_url, headers=headers, timeout=30)
        links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', response.text)
        
        final_list = []
        seen_titles = set()
        exclude_keywords = ['Privacy policy', 'Legal notice', 'Cookies', 'Contact', 'Sitemap', 'Search', 'Browse by subject']

        for l, t in links:
            title = re.sub('<[^<]+?>', '', t).strip()
            if len(title) > 20 and title not in seen_titles: # 'Browse by subject' 등을 거르기 위해 길이 상향
                if not any(key in title for key in exclude_keywords):
                    full_link = l if l.startswith('http') else "https://op.europa.eu" + l
                    final_list.append({"date": "2025-Latest", "title": title, "link": full_link})
                    seen_titles.add(title)

        if final_list:
            # 1. 파일 저장
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                writer.writeheader()
                writer.writerows(final_list)
            
            # 2. [추가] 화면에 상위 5개 미리보기 출력
            print("\n" + "="*50)
            print(f"📋 수집된 정책 리스트 (총 {len(final_list)}건)")
            print("-"*50)
            for i, item in enumerate(final_list[:5], 1):
                print(f"{i}. 제목: {item['title']}")
                print(f"   링크: {item['link']}")
            print("="*50 + "\n")
            
            print(f"🎯 [최종 성공] {file_name} 파일 생성이 완료되었습니다.", flush=True)
        else:
            print("⚠️ 조건에 맞는 정책 문서를 찾지 못했습니다.", flush=True)

    except Exception as e:
        print(f"❌ 오류 발생: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_policy_and_show()
