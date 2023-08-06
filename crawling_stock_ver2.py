import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import os

options = webdriver.ChromeOptions()
browser = webdriver.Chrome()

code = ['098120', '009520', '005930']

for i in code:
    #1. 페이지 이동
    url = "https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd=" + i
    browser.get(url)

    # 재무재표 연간 탭 클릭
    checkbox = browser.find_element(By.ID, 'cns_Tab21')
    checkbox.click()

    data_array = []

    row1 = browser.find_elements(By.CLASS_NAME, 'center')

    for row in row1:
        if row.text == "2022(A)":
            parent = row.find_element(By.XPATH, "..")
            eles = parent.find_element(By.XPATH, '//*[@id="cTB25"]/tbody/tr[3]/td[6]')
            data_array.append(eles.text)
        elif row.text == "2023(E)":
            parent = row.find_element(By.XPATH, "..")
            eles = parent.find_element(By.XPATH, '//*[@id="cTB25"]/tbody/tr[4]/td[6]')
            if eles.text == '':
                data_array.append(0)
            else:
                data_array.append(eles.text)
        elif row.text == "2024(E)":
            parent = row.find_element(By.XPATH, "..")
            eles = parent.find_element(By.XPATH, '//*[@id="cTB25"]/tbody/tr[5]/td[6]')  
            if eles.text == '':
                data_array.append(0)
            else:
                data_array.append(eles.text)
    
    print(data_array)