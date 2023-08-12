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

result_consensus = []

def ErrorLog(error: str):
    current_time = time.strftime("%Y.%m.%d/%H:%M:%S", time.localtime(time.time()))
    with open("Log.txt", "a") as f:
        f.write(f"[{current_time}] - {error}\n")

def StockCodeList(path):
    stock_code = pd.read_excel(path, sheet_name = 'Sheet1', converters={'종목코드':str})
    stock_code = stock_code[['종목명','종목코드']]
    stock_code.columns = ['Stock','Code']
    # print(stock_code)

    code_list = stock_code['Code'].values.tolist()
    # print(code_list)

    return stock_code
def do_html_crawl(urll: str, url: str):
    data_array = []
    data_array_per = []
    data_array_price = []

    options = webdriver.ChromeOptions()

    # 창 숨기는 옵션 추가
    options.add_argument("headless")
    browser = webdriver.Chrome(options=options)
    browser.get(urll)

    sleep(3)

    name = browser.find_element(By.CLASS_NAME, 'name')
    price = browser.find_element(By.XPATH, '//*[@id="cTB11"]/tbody/tr[1]/td/strong')
    data_array.append(name.text)
    data_array.append(url)
    data_array_price.append(price.text)

    lists = browser.find_elements(By.CLASS_NAME, 'center')
    
    try:
        for list in lists:
            if list.text == "2022(A)":
                parent = list.find_element(By.XPATH, "..")
                element = parent.find_element(By.XPATH, '//*[@id="cTB25"]/tbody/tr[3]/td[6]')
                if element.text == '':
                    data_array.append(0)
                else:
                    data_array.append(element.text)
                element_per = parent.find_element(By.XPATH, '//*[@id="cTB25"]/tbody/tr[3]/td[7]')
                data_array_per.append(element_per.text)
                
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
        
        # 일부 종목에서 컨센서스가 4개 크롤링 되는 문제 발생 -> 따로 표시
        if len(data_array) > 5:
            data_array = [name.text, url, '', '', '']
        elif len(data_array) == 4:
            data_array.append('')
        
        # 현재 PER 와 주가 추가
        data_array.append(data_array_per[0])
        data_array.append(data_array_price[0])
        print(data_array)

        if (data_array[3] == 0 or data_array[4] == 0 or data_array[5] == 'N/A'):
            price_23 = ''
            price_24 = ''
            data_array.append(price_23)
            data_array.append(price_24)
        else:
            price_23 = float(data_array[3].replace(',', '')) * float(data_array[5])
            price_24 = float(data_array[4].replace(',', '')) * float(data_array[5])
            data_array.append(int(price_23))
            data_array.append(int(price_24)) 

    except Exception as error:
        ErrorLog(str(name.text))       
        ErrorLog(str(urll))     
    

    result_consensus.append(data_array)

    browser.quit()

    return result_consensus

def do_thread_crawl(urls: list):
    count = 0
    thread_list = []
    with ThreadPoolExecutor(max_workers=16) as executor:
        for url in urls:            
            urll = "https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd=" + url
            thread_list.append(executor.submit(do_html_crawl, urll, url))            
        for execution in concurrent.futures.as_completed(thread_list):
            count += 1
            print(count, "번째 진행중.....")
            execution.result()

def search(stock_code):
    
    code = stock_code
    # code = ['265520', '456440', '442770', '426550', '439730', '456490']
    do_thread_crawl(code)

def main():
    stockcodelist = StockCodeList("cosdaq.xlsx")
    
    code_list = stockcodelist['Code'].values.tolist()

    search(code_list)

    columns = ['종목명', '종목코드', '2022(A)', '2023(E)', '2024(E)', 'PER(2022)', '현재가', '2023 예상가', '2024 예상가']
    result = pd.DataFrame(data = result_consensus, columns=columns)
    result = result.sort_values(by=['종목명'] ,ascending=True)
    print(result)
    result.to_excel('컨센서스_.xlsx', index=False)

if __name__ == "__main__":
    main()