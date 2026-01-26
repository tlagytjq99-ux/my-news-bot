import os
import requests
import pandas as pd
from datetime import datetime

# 1. 인증 정보 가져오기 (GitHub Secrets)
client_id = os.environ.get('NAVER_CLIENT_ID')
client_secret = os.environ.get('NAVER_CLIENT_SECRET')

# 2. 카테고리 분류 함수
def classify_category(title):
    categories = {
        "기업": ["투자", "유치", "인수", "합병", "M&A", "실적", "상장", "IPO", "파트너십", "협력", "삼성", "네이버", "구글", "오픈AI"],
        "기술": ["모델", "LLM", "성능", "출시", "특허", "논문", "칩", "반도체", "HBM", "Sora", "GPT", "알고리즘"],
        "정책": ["정부", "법안", "규제", "가이드라인", "예산", "지원", "국회", "과기부", "EU", "조약", "윤리"],
        "산업": ["시장", "전망", "도입", "사례", "금융", "의료", "제조", "일자리", "확산", "트렌드", "인력"]
    }
    for category, keywords in categories.items():
        if any(keyword in title for keyword in keywords):
            return category
    return "기타"

# 3. 뉴스 검색 API 설정 (100개를 가져와서 2개씩 골라냅니다)
search_keyword = "AI"
url = f"https://openapi.naver.com/v1/search/news.json?query={search_keyword}&display=100&sort=sim"

headers = {
    "X-Naver-Client-Id": client_id,
    "X-Naver-Client-Secret": client_secret
}

try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        items = response.json().get('items', [])
        
        # 각 분야별로 2개씩만 담을 바구니
        category_counts = {"기업": 0, "기술": 0, "정책": 0, "산업": 0, "기타": 0}
        final_data_list = []

        for item in items:
            title = item['title'].replace("<b>", "").replace("</b>", "").replace("&quot;", '"').replace("&amp;", "&")
            category = classify_category(title)
            
            # 해당 카테고리가 아직 2개 미만일 때만 추가
            if category_counts[category] < 2:
                try:
                    pub_date = datetime.strptime(item['pubDate'], '%a, %d %b %Y %H:%M:%S +0900')
                    formatted_date = pub_date.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted_date = item['pubDate']

                final_data_list.append({
                    "카테고리": category,
                    "기사제목": title,
                    "발행일": formatted_date,
                    "링크": item['link']
                })
                category_counts[category] += 1

        # [변경점] 누적 로직 없이 무조건 새로 저장합니다.
        if final_data_list:
            df = pd.DataFrame(final_data_list)
            # 카테고리 순서대로 정렬해서 보기 좋게 만듭니다.
            df = df.sort_values(by="카테고리")
            
            file_name = "news_list.xlsx"
            df.to_excel(file_name, index=False)
            
            print("--- 수집 결과 요약 ---")
            for cat, count in category_counts.items():
                print(f"[{cat}]: {count}개 수집됨")
            print("----------------------")
            print(f"✅ 테스트 완료! '{file_name}'에 새 데이터만 저장되었습니다.")
        else:
            print("❌ 조건에 맞는 검색 결과가 없습니다.")
    else:
        print(f"❌ API 오류: {response.status_code}")

except Exception as e:
    print(f"⚠️ 에러 발생: {e}")
