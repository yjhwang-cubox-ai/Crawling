import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from time import sleep

result_consensus = []

def StockCodeList(path):
    stock_code = pd.read_excel(path, sheet_name = 'Sheet1', converters={'종목코드':str})
    stock_code = stock_code[['한글 종목명','단축코드']]
    stock_code.columns = ['Stock','Code']
    # print(stock_code)

    code_list = stock_code['Code'].values.tolist()
    # print(code_list)

    return stock_code
def do_html_crawl(urll: str, url: str):
    data_array = []

    options = webdriver.ChromeOptions()

    # 창 숨기는 옵션 추가
    options.add_argument("headless")
    browser = webdriver.Chrome(options=options)
    browser.get(urll)

    sleep(1)

    name = browser.find_element(By.CLASS_NAME, 'name')
    data_array.append(name.text)
    data_array.append(url)

    lists = browser.find_elements(By.CLASS_NAME, 'center')

    for list in lists:
        if list.text == "2022(A)":
            parent = list.find_element(By.XPATH, "..")
            element = parent.find_element(By.XPATH, '//*[@id="cTB25"]/tbody/tr[3]/td[6]')
            if element.text == '':
                data_array.append(0)
            else:
                data_array.append(element.text)
        elif list.text == "2023(E)":
            parent = list.find_element(By.XPATH, "..")
            element = parent.find_element(By.XPATH, '//*[@id="cTB25"]/tbody/tr[4]/td[6]')
            if element.text == '':
                data_array.append(0)
            else:
                data_array.append(element.text)
        elif list.text == "2024(E)":
            parent = list.find_element(By.XPATH, "..")
            element = parent.find_element(By.XPATH, '//*[@id="cTB25"]/tbody/tr[5]/td[6]')  
            if element.text == '':
                data_array.append(0)
            else:
                data_array.append(element.text)        
    
    print(data_array)
    result_consensus.append(data_array)

def do_thread_crawl(urls: list):
    count = 0
    thread_list = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        for url in urls:            
            urll = "https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd=" + url
            thread_list.append(executor.submit(do_html_crawl, urll, url))            
        for execution in concurrent.futures.as_completed(thread_list):
            count += 1
            print(count, "번째 진행중.....")
            execution.result()

def do_process_with_thread_crawl(code_list: str):
    do_thread_crawl(code_list)


def search(stock_code):
    
    code_list = stock_code

    with Pool(processes=4) as pool:  
        pool.map(do_process_with_thread_crawl, code_list)

def main():
    stockcodelist = StockCodeList("cosdaq.xlsx")
    code_list = stockcodelist['Code'].values.tolist()

    search(code_list)

    result = pd.DataFrame(data = result_consensus)

    result.to_excel('컨센서스.xlsx')

if __name__ == "__main__":
    main()