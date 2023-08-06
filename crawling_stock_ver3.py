import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
from time import sleep


def search(stock_code):

    options = webdriver.ChromeOptions()

    # 창 숨기는 옵션 추가
    options.add_argument("headless")

    browser = webdriver.Chrome(options=options)

    code = stock_code

    eps_array = []
    num = 0
    for i in code:
        num += 1
        #1. 페이지 이동
        url = "https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd=" + i
        browser.get(url)

        sleep(1)

        data_array = []

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
            
        print(i)
        print(data_array)        
        eps_array.append(data_array)
        print(num, " 진행중", " / ", len(code))
    
    return eps_array

    # print(eps_array)

    # col = ["2022(A)", "2023(E)", "2024(E)"]
    # df = pd.DataFrame(data=eps_array,columns=col)

    # print(df)