import os
import requests
import pandas as pd
from datetime import datetime

# 직접 입력하는 대신 GitHub Secrets 금고에서 몰래 가져옵니다.
client_id = os.environ.get('NAVER_CLIENT_ID')
client_secret = os.environ.get('NAVER_CLIENT_SECRET')

# 뉴스 검색 API 주소 (AI 키워드, 10개, 최신순 정렬)
keyword = "AI"
url = f"https://openapi.naver.com/v1/search/news.json?query={keyword}&display=10&sort=sim"

headers = {
    "X-Naver-Client-Id": client_id,
    "X-Naver-Client-Secret": client_secret
}

try:
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        items = response.json().get('items', [])
        data = []

        for item in items:
            # 글자 사이의 <b> 태그 등을 깨끗하게 청소합니다.
            title = item['title'].replace("<b>", "").replace("</b>", "").replace("&quot;", '"').replace("&amp;", "&")
            
            # 발행일 형식을 읽기 좋게 바꿉니다.
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
            print(f"✅ 수집 성공! 엑셀 파일이 업데이트되었습니다.")
        else:
            print("❌ 검색 결과가 없습니다.")
    else:
        print(f"❌ API 연결 실패 (코드: {response.status_code}) - ID/Secret을 확인하세요.")

except Exception as e:
    print(f"⚠️ 에러 발생: {e}")
