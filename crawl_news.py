import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# 1. 네이버 뉴스 검색 결과 가져오기 (AI 검색, 최신순)
url = "https://search.naver.com/search.naver?where=news&query=AI&sm=tab_opt&sort=1"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# 2. 뉴스 데이터 추출
news_items = soup.select('.news_area')[:10] # 상위 10개
data = []

for item in news_items:
    title = item.select_one('.news_tit').text
    link = item.select_one('.news_tit')['href']
    # 발행일 (네이버 검색 결과의 시간을 가져옴)
    date_text = item.select_one('.info_group').text.strip()
    
    data.append({
        "수집일": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "발행일": date_text,
        "기사제목": title,
        "링크": link
    })

# 3. 엑셀 파일로 저장
df = pd.DataFrame(data)
df.to_excel("news_list.xlsx", index=False)
print("엑셀 저장 완료!")
