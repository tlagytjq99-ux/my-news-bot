import os
import requests
import pandas as pd
from datetime import datetime

# 1. 인증 정보 가져오기 (GitHub Secrets)
client_id = os.environ.get('NAVER_CLIENT_ID')
client_secret = os.environ.get('NAVER_CLIENT_SECRET')

# 2. 카테고리 분류 함수 (보고서 목차 기준)
def classify_category(title):
    # 각 카테고리별 핵심 키워드 설정
    categories = {
        "기업": ["투자", "유치", "인수", "합병", "M&A", "실적", "상장", "IPO", "파트너십", "협력", "삼성", "네이버", "구글", "오픈AI"],
        "기술": ["모델", "LLM", "성능", "출시", "특허", "논문", "칩", "반도체", "HBM", "Sora", "GPT", "알고리즘"],
        "정책": ["정부", "법안", "규제", "가이드라인", "예산", "지원", "국회", "과기부", "EU", "조약", "윤리"],
        "산업": ["시장", "전망", "도입", "사례", "금융", "의료", "제조", "일자리", "확산", "트렌드", "인력"]
    }
    
    for category, keywords in categories.items():
        if any(keyword in title for keyword in keywords):
            return category
    return "기타" # 키워드가 매칭되지 않을 경우

# 3. 뉴스 검색 API 설정
search_keyword = "AI"
url = f"https://openapi.naver.com/v1/search/news.json?query={search_keyword}&display=20&sort=sim"

headers = {
    "X-Naver-Client-Id": client_id,
    "X-Naver-Client-Secret": client_secret
}

try:
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        items = response.json().get('items', [])
        new_data_list = []

        for item in items:
            title = item['title'].replace("<b>", "").replace("</b>", "").replace("&quot;", '"').replace("&amp;", "&")
            
            # 카테고리 자동 분류 실행
            category = classify_category(title)
            
            try:
                pub_date = datetime.strptime(item['pubDate'], '%a, %d %b %Y %H:%M:%S +0900')
                formatted_date = pub_date.strftime('%Y-%m-%d %H:%M')
            except:
                formatted_date = item['pubDate']

            new_data_list.append({
                "수집일": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "카테고리": category,
                "발행일": formatted_date,
                "기사제목": title,
                "링크": item['link']
            })

        if new_data_list:
            new_df = pd.DataFrame(new_data_list)
            file_name = "news_list.xlsx"

            if os.path.exists(file_name):
                old_df = pd.read_excel(file_name)
                combined_df = pd.concat([old_df, new_df], ignore_index=True)
                # 제목 중복 제거
                combined_df = combined_df.drop_duplicates(subset=['기사제목'], keep='first')
            else:
                combined_df = new_df

            combined_df.to_excel(file_name, index=False)
            print(f"✅ 분류 완료! 현재 DB에 총 {len(combined_df)}개의 뉴스가 분류되어 저장되었습니다.")
        else:
            print("❌ 검색 결과가 없습니다.")
    else:
        print(f"❌ API 오류: {response.status_code}")

except Exception as e:
    print(f"⚠️ 에러 발생: {e}")
