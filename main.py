import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from time import sleep
import time
import traceback
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, WebDriverException, NoSuchElementException
import logging
import pandas as pd
import time
from datetime import datetime, timedelta
from pykrx import stock

### 용어
# 종목명: ticker_name
# 종목코드: ticker symbol    
# 현재가: market_price

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def click_element_by_xpath(driver, xpath, element_name, wait_time=10):
    try:
        element = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        # 요소가 뷰포트에 보일 때까지 스크롤
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        # 요소가 클릭 가능할 때까지 대기
        element = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        element.click()
        logger.info(f"{element_name} 클릭 완료")
        time.sleep(2)  # 클릭 후 잠시 대기
    except TimeoutException:
        logger.error(f"{element_name} 요소를 찾는 데 시간이 초과되었습니다.")
    except ElementClickInterceptedException:
        logger.error(f"{element_name} 요소를 클릭할 수 없습니다. 다른 요소에 가려져 있을 수 있습니다.")
    except NoSuchElementException:
        logger.error(f"{element_name} 요소를 찾을 수 없습니다.")
    except Exception as e:
        logger.error(f"{element_name} 클릭 중 오류 발생: {e}")

def get_market_price(stock_code):
    today = datetime.now()
    if today.weekday() == 5:  # 토요일
        target_date = today - timedelta(days=1)
    elif today.weekday() == 6:  # 일요일
        target_date = today - timedelta(days=2)
    else:
        target_date = today

    formatted_date = target_date.strftime("%Y%m%d")
  
    market_price = stock.get_market_ohlcv_by_date(formatted_date, formatted_date, stock_code).iloc[-1]['종가']

    return market_price

def do_html_crawl(url: str, stock_code: str):
    url = url + stock_code
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    browser = webdriver.Chrome(options=options)
    browser.get(url)

    sleep(1)
    
    click_element_by_xpath(
        browser,
        "/html/body/div/form/div[1]/div/div[2]/div[3]/div/div/table[2]/tbody/tr/td[3]",
        "연간"
    )

    # 'class'와 'summary' 속성을 조합하여 특정 테이블 선택
    table = browser.find_element(By.XPATH, '//table[@class="gHead01 all-width" and @summary="주요재무정보를 제공합니다."]')
    html_content = table.get_attribute('outerHTML')
    
    # HTML에서 DataFrame 읽기
    df = pd.read_html(html_content)[0]

    # 열 이름 매핑
    columns_map = {
        "operating_profit": 1,  # 영업이익
        "eps": 25,             # 주당순이익 (EPS)
        "per": 26              # PER
    }

    # 필요한 데이터 추출
    result = {
        metric: {year: df[df.columns[-(3 - i)]][index] for i, year in enumerate([2024, 2025, 2026])}
        for metric, index in columns_map.items()
    }

    # 결과 변수 예시
    operating_profit_2024 = result["operating_profit"][2024]
    operating_profit_2025 = result["operating_profit"][2025]
    operating_profit_2026 = result["operating_profit"][2026]

    eps_2024 = result["eps"][2024]
    eps_2025 = result["eps"][2025]
    eps_2026 = result["eps"][2026]

    per_2024 = result["per"][2024]
    
    #컨센서스가 없는 종목 패스
    if pd.isna(operating_profit_2024) or pd.isna(operating_profit_2025) or pd.isna(operating_profit_2026):
        return  # 함수 종료
    
    stock_name = stock.get_market_ticker_name(stock_code)
    market_price = get_market_price(stock_code)
    
    data = {
        "종목코드": str(stock_code),  # 종목코드
        "종목명": stock_name,  # 종목명
        "현재가": str(int(market_price)),  # 현재가
        "영업이익(2024)": str(int(operating_profit_2024)), # 영업이익(2024)
        "영업이익(2025)": str(int(operating_profit_2025)), # 영업이익(2025)
        "영업이익(2026)": str(int(operating_profit_2026)), # 영업이익(2026)
        "EPS(2024)": str(int(eps_2024)),  # EPS(2024)
        "EPS(2025)": str(int(eps_2024)),  # EPS(2025)
        "EPS(2026)": str(int(eps_2024)),  # EPS(2026)
        "PER(2024)": str(int(eps_2024)),  # PER(2024)
        "PER(2025)": str(int(eps_2025)),  # PER(2025)
        "PER(2026)": str(int(eps_2026)),  # PER(2026)
        "목표가(2024)": str(int(eps_2024*per_2024)),  # 목표가(2024)
        "목표가(2025)": str(int(eps_2025*per_2024)),  # 목표가(2025) -> per 는 현재 수치를 기준으로 한다
        "목표가(2026)": str(int(eps_2026*per_2024))   # 목표가(2026) -> per 는 현재 수치를 기준으로 한다
    }
    
    return data


def main():
    # 테스트용 종목코드
    stock_list = ['068270', '000660', '035420', '365330', '033320']
    # stock_list = ['365330']
    
    # 전종목 코드
    # KOSPI 시장의 종목 리스트 가져오기
    kospi_list = stock.get_market_ticker_list(market="KOSPI")
    kosdaq_list = stock.get_market_ticker_list(market="KOSDAQ")
    
    url = "https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd="

    start = time.time()
    total_data = []
    for stock_code in stock_list:
        data = do_html_crawl(url, stock_code)
        if data is not None:
            total_data.append(data)

    end = time.time()
    print(f"작업 실행 시간: {end - start:.2f}초")
    
    # 데이터를 csv 파일로 저장
    # DataFrame 생성
    df = pd.DataFrame(total_data)

    # 열 순서 지정
    column_order = [
        "종목코드", "종목명", "현재가", 
        "영업이익(2024)", "영업이익(2025)", "영업이익(2026)", 
        "EPS(2024)", "EPS(2025)", "EPS(2026)", 
        "PER(2024)", "PER(2025)", "PER(2026)", 
        "목표가(2024)", "목표가(2025)", "목표가(2026)"
    ]

    # DataFrame을 지정된 열 순서로 정렬
    df = df[column_order]

    # CSV 파일로 저장
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file_name = f"financial_data_{current_time}.csv"
    df.to_csv(csv_file_name, index=False, encoding='utf-8-sig')
    print(f"{csv_file_name}로 저장 완료")
    

if __name__ == "__main__":
    main()