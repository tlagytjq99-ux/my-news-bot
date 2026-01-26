import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# 1. 네이버 뉴스 검색 주소 (AI 키워드, 최신순)
url = "https://search.naver.com/search.naver?where=news&query=AI&sm=tab_opt&sort=1"

# 2. 사람처럼 보이게 하는 최소한의 설정 (헤더)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 3. 뉴스 아이템 찾기
    news_items = soup.select('.news_wrap')
    data = []

    for item in news_items:
        # 기사 제목과 링크
        title_el = item.select_one('.news_tit')
        if not title_el: continue
        
        title = title_el.get_text(strip=True)
        link = title_el['href']
        
        # 발행일 (info 클래스 중 날짜 형식을 가진 것 추출)
        info_els = item.select('.info_group .info')
        # 보통 언론사 이름 다음에 날짜가 나오므로 마지막 요소를 가져옵/니다.
        date_text = info_els[-1].get_text(strip=True) if info_els else "날짜미상"

        # 광고성 링크 제외
        if "static/channelPromotion" in link:
            continue

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
        print(f"✅ 성공! {len(data)}개의 뉴스를 수집했습니다.")
    else:
        print("❌ 여전히 데이터를 찾지 못했습니다. 네이버가 접근을 일시 차단했을 수 있습니다.")

except Exception as e:
    print(f"⚠️ 에러 발생: {e}")
