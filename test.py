import requests
from bs4 import BeautifulSoup

# 크롤링할 URL
url = 'https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd=347890'

# User-Agent 설정 (일부 사이트에서는 User-Agent를 설정해야 정상적인 응답을 받을 수 있음)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

# URL에 GET 요청 보내기
response = requests.get(url, headers=headers)

# 응답의 상태 코드 확인 (200이면 정상 응답)
if response.status_code == 200:
    # BeautifulSoup을 사용하여 HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # 원하는 데이터를 추출하는 코드 작성
    # 예를 들어, 클래스명이 'financial_summary'인 테이블을 찾는다고 가정하면:
    financial_summary_table = soup.find('div', {'id': 'ZlEwemUxRm'})

    # 데이터 추출 후 처리하는 로직을 추가로 작성해야 합니다.
    if financial_summary_table:
        rows = financial_summary_table.find_all('tbody')
        for row in rows:
            columns = row.find_all('td')
            for column in columns:
                print(column.get_text(), end='\t')
            print()

    else:
        print('테이블을 찾을 수 없습니다.')


    print(financial_summary_table)

else:
    print('서버 응답에 실패했습니다. 상태 코드:', response.status_code)