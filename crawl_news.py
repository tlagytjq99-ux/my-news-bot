import requests
import pandas as pd
from datetime import datetime

# 1. 네이버에서 받은 인증 정보 입력
client_id = "qeHrlFepLCF0iYMg2zEP" # 여기에 입력
client_secret = "EtNc__GQWw" # 여기에 입력

# 2. 뉴스 검색 API 주소 (AI 키워드, 10개, 최신순)
keyword = "AI"
url = f"https://openapi.naver.com/v1/search/news.json?query={keyword}&display=10&sort=sim"

headers = {
    "X-Naver-Client-Id": client_id,
    "X-Naver-Client-Secret": client_secret
}

try:
    response = requests.get(url, headers=headers)
    rescode = response.status_code

    if rescode == 200:
        items = response.json().get('items', [])
        data = []

        for item in items:
            # HTML 태그 제거 (<b> 등)
            title = item['title'].replace("<b>", "").replace("</b>", "").replace("&quot;", '"')
            
            # 날짜 형식 변환
            try:
                pub_date = datetime.strptime(item['pubDate'], '%a, %d %b %Y %H:%M:%S +0900')
                formatted_date = pub_date.strftime('%Y-%m-%d %H:%M')
            except:
                formatted_date = item['pubDate']

            data.append({
                "수집일": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "발행일": formatted_date,
                "기사제목": title,
                "링크": item['link']
            })

        if data:
            df = pd.DataFrame(data)
            df.to_excel("news_list.xlsx", index=False)
            print(f"✅ API 방식으로 {len(data)}개 수집 성공!")
        else:
            print("❌ 검색 결과가 없습니다.")
    else:
        print(f"❌ API 오류 발생: {rescode}")

except Exception as e:
    print(f"⚠️ 에러 발생: {e}")
