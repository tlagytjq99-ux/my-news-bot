import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# 1. 네이버 뉴스 검색 RSS 주소 (AI 키워드)
# RSS 방식은 네이버가 공식적으로 데이터를 제공하는 통로라 차단이 거의 없습니다.
url = "https://search.naver.com/search.naver?where=news&query=AI&sm=tab_pge&sort=1&format=rss"

try:
    response = requests.get(url)
    # RSS는 XML 형식이므로 lxml이나 html.parser로 읽습니다.
    soup = BeautifulSoup(response.content, 'xml')

    # 2. 기사 아이템 찾기
    items = soup.find_all('item')
    data = []

    for item in items:
        title = item.find('title').get_text(strip=True)
        link = item.find('link').get_text(strip=True)
        # RSS에서 제공하는 발행일 (예: Mon, 26 Jan 2026 14:00:00 +0900)
        pub_date = item.find('pubDate').get_text(strip=True)
        
        # 날짜 형식을 보기 좋게 변환 (선택 사항)
        try:
            date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
        except:
            formatted_date = pub_date

        data.append({
            "수집일": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "발행일": formatted_date,
            "기사제목": title,
            "링크": link
        })

        if len(data) >= 10:
            break

    # 3. 엑셀 저장
    if data:
        df = pd.DataFrame(data)
        df.to_excel("news_list.xlsx", index=False)
        print(f"✅ RSS 방식으로 {len(data)}개 수집 성공!")
    else:
        print("❌ RSS에서도 데이터를 찾지 못했습니다. 키워드를 확인해주세요.")

except Exception as e:
    print(f"⚠️ 에러 발생: {e}")
