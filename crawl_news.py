import os
import requests
import pandas as pd
from datetime import datetime

# 1. 인증 정보 가져오기 (GitHub Secrets)
client_id = os.environ.get('NAVER_CLIENT_ID')
client_secret = os.environ.get('NAVER_CLIENT_SECRET')

# 2. 뉴스 검색 API 설정
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
        new_data_list = []

        for item in items:
            title = item['title'].replace("<b>", "").replace("</b>", "").replace("&quot;", '"').replace("&amp;", "&")
            try:
                pub_date = datetime.strptime(item['pubDate'], '%a, %d %b %Y %H:%M:%S +0900')
                formatted_date = pub_date.strftime('%Y-%m-%d %H:%M')
            except:
                formatted_date = item['pubDate']

            new_data_list.append({
                "수집일": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "발행일": formatted_date,
                "기사제목": title,
                "링크": item['link']
            })

        if new_data_list:
            new_df = pd.DataFrame(new_data_list)
            file_name = "news_list.xlsx"

            # [핵심] 기존 파일이 있으면 합치고, 없으면 새로 만듭니다.
            if os.path.exists(file_name):
                # 기존 엑셀 파일을 읽어옵니다.
                old_df = pd.read_excel(file_name)
                # 기존 데이터 아래에 새 데이터를 붙입니다.
                combined_df = pd.concat([old_df, new_df], ignore_index=True)
                # 중복된 기사 제목이 있다면 제거합니다 (똑같은 기사가 또 들어오는 것 방지)
                combined_df = combined_df.drop_duplicates(subset=['기사제목'], keep='first')
            else:
                combined_df = new_df

            # 최종적으로 엑셀 파일 저장
            combined_df.to_excel(file_name, index=False)
            print(f"✅ 누적 업데이트 완료! 현재 총 {len(combined_df)}개의 데이터가 쌓여있습니다.")
        else:
            print("❌ 검색 결과가 없습니다.")
    else:
        print(f"❌ API 오류: {response.status_code}")

except Exception as e:
    print(f"⚠️ 에러 발생: {e}")
