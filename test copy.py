import requests
from bs4 import BeautifulSoup

def get_financial_data(nRow):
    url = f"https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={nRow}"
    headers = {"User-Agent": "Mozilla/5.0"}  # User-Agent 설정 (웹사이트 차단 방지)

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
#RVArcVR1a2 > table:nth-child(2) > tbody > tr:nth-child(1) > td:nth-child(2) > span
        # 연간 버튼 클릭
        annual_button = soup.find("tbody")
        if annual_button:
            annual_button_link = annual_button.find("RVArcVR1a2")
            if annual_button_link:
                annual_url = annual_button_link.find("td", {"class": "num line "})
                annual_response = requests.get(annual_url, headers=headers)
                if annual_response.status_code == 200:
                    annual_soup = BeautifulSoup(annual_response.content, "html.parser")

                    # EPS 정보
                    eps_element = annual_soup.find("td", text="EPS(원)")
                    if eps_element:
                        eps_data = eps_element.find_next_siblings("td")[1:4]
                        eps_values = [data.get_text() for data in eps_data]
                        return eps_values

                    # 당기순이익 정보
                    net_profit_element = annual_soup.find("td", text="당기순이익")
                    if net_profit_element:
                        net_profit_data = net_profit_element.find_next_siblings("td")[1:4]
                        net_profit_values = [data.get_text() for data in net_profit_data]
                        return net_profit_values

    return None

# nRow 값은 Excel 시트의 C열에 해당하는 값을 넣어주어야 합니다.
nRow_value = "347890"  # 예시 값, 실제로는 원하는 회사의 코드로 대체해야 합니다.
financial_data = get_financial_data(nRow_value)
if financial_data:
    print("EPS(원):", financial_data[0])
    print("EPS 전년동기:", financial_data[1])
    print("EPS 전전년동기:", financial_data[2])
else:
    print("데이터를 찾을 수 없습니다.")