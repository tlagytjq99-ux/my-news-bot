import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# 1. 모바일용 검색 주소 (m.search.naver.com 사용)
url = "https://m.search.naver.com/search.naver?where=m_news&query=AI&sm=mtb_opt&sort=1"

# 2. 모바일 브라우저인 척 하는 신분증
headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
}

try:
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 3. 모바일 뉴스 아이템 찾기 (구조가 다름)
    news_items = soup.select('.news_wrap')
    data = []

    for item in news_items:
        # 제목과 링크
        title_el = item.select_one('.news_tit')
        if not title_el: continue
        
        title = title_el.get_text(strip=True)
        link = title_el['href']
        
        # 발행일 (모바일은 .info_group 안에 .info가 있음)
        try:
            date_text = item.select('.info_group .info')[-1].get_text(strip=True)
        except:
            date_text = "날짜미상"

        data.append({
            "수집일": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "발행일": date_text,
            "기사제목": title,
            "링크": link
        })

        if len(data) >= 10:
            break

    # 4. 엑셀 저장
    if data:
        df = pd.DataFrame(data)
        df.to_excel("news_list.xlsx", index=False)
        print(f"✅ 모바일 수집 성공! {len(data)}개의 뉴스를 가져왔습니다.")
    else:
        # 만약 이것도 안된다면 네이버가 IP 자체를 차단한 것일 수 있음
        print("❌ 모바일 버전에서도 데이터를 찾지 못했습니다.")

except Exception as e:
    print(f"⚠️ 에러 발생: {e}")
