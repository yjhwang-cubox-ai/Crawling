import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import os

options = webdriver.ChromeOptions()
browser = webdriver.Chrome()

#1. 페이지 이동
url = "https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd=005930"
browser.get(url)

# 재무재표 연간 탭 클릭
checkbox = browser.find_element(By.ID, 'cns_Tab21')
checkbox.click()

array1 = []

row1 = browser.find_elements(By.CLASS_NAME, 'center')

for row in row1:
    if row.text == "2020(A)":
        print("있음")
        parent = row.find_element(By.XPATH, "..")
        eles = parent.find_element(By.XPATH, '//*[@id="cTB25"]/tbody/tr[1]/td[6]')
        print(eles.text)


