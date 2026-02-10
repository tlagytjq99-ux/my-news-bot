import requests
import csv
import re
from datetime import datetime

def fetch_eu_policy_smart_filter():
    # EU의 최신 발행물 전체 리스트 페이지
    target_url = "https://op.europa.eu/en/web/general-publications/publications"
    file_name = 'EU_Policy_Latest_Reports.csv'
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    print("📡 [지능형 수집] 키워드 없이 알짜 정책 보고서만 추출합니다...", flush=True)

    try:
        response = requests.get(target_url, headers=headers, timeout=30)
        # 모든 링크와 제목 추출
        links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', response.text)
        
        final_list = []
        seen_titles = set()
        
        # 1. '진짜' 정책 문서에만 들어가는 핵심 단어들 (포함 조건)
        policy_keywords = ['report', 'study', 'strategy', 'briefing', 'policy', 'analysis', 'guide', 'handbook', 'summary', 'commission']
        
        # 2. 제거할 잡음 데이터 (제외 조건)
        exclude_list = ['privacy policy', 'legal notice', 'cookies', 'contact', 'sitemap', 
                        'search', 'browse by', 'call us', 'meet us', 'options', 'publishing services']

        for l, t in links:
            title = re.sub('<[^<]+?>', '', t).strip()
            title_lower = title.lower()
            
            # 필터링 조건:
            # - 제목이 30자 이상 (충분한 정보가 담긴 제목)
            # - 위 정책 핵심 단어 중 하나라도 포함
            # - 제외 리스트에 있는 단어는 포함하지 않음
            if len(title) > 30 and title not in seen_titles:
                is_policy = any(pk in title_lower for pk in policy_keywords)
                is_noise = any(ex in title_lower for ex in exclude_list)
                
                if is_policy and not is_noise:
                    full_link = l if l.startswith('http') else "https://op.europa.eu" + l
                    final_list.append({
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "title": title,
                        "link": full_link
                    })
                    seen_titles.add(title)

        if final_list:
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                writer.writeheader()
                writer.writerows(final_list)
            
            print("\n" + "🚀"*20)
            print(f"📁 필터링 완료! {len(final_list)}건의 핵심 정책 문서를 선별했습니다.")
            print("🚀"*20)
            for i, item in enumerate(final_list[:15], 1): # 상위 15개 출력
                print(f"{i}. {item['title']}")
                print(f"   🔗 {item['link']}\n")
            print("🚀"*20)
        else:
            print("⚠️ 정책 문서 조건에 맞는 데이터가 없습니다. 필터를 조정 중입니다...", flush=True)

    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_policy_smart_filter()
