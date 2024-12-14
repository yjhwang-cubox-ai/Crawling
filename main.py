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

    # pandas로 DataFrame 변환
    import pandas as pd
    df = pd.read_html(html_content)[0]

    # DataFrame을 CSV 파일로 저장
    csv_file_name = f"{stock_code}_financial_data.csv"
    df.to_csv(csv_file_name, index=False, encoding='utf-8-sig')
    print(f"{csv_file_name}로 저장 완료")

    print(df)


def main():
    # stock_list = ['068270', '000660', '035420', '365330', '033320']
    stock_list = ['068270']
    url = "https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd="

    start = time.time()
    for stock_code in stock_list:
        result = do_html_crawl(url, stock_code)
        print(result)

    end = time.time()
    print(f"작업 실행 시간: {end - start:.2f}초")

if __name__ == "__main__":
    main()