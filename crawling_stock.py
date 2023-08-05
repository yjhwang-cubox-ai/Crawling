import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import os

browser = webdriver.Chrome()
# browser.maximize_window()

#1. 페이지 이동
url = "https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd=005930"
browser.get(url)

# 재무재표 연간 탭 클릭
checkbox = browser.find_element(By.ID, 'cns_Tab21')
checkbox.click()

# sales = browser.find_elements(By.TAG_NAME, 'span')
sales = browser.find_element(By.XPATH, '//*[@id="aFVlanREZS"]/table[2]/tbody/tr[1]')
label = sales.find_elements(By.TAG_NAME, 'span')

for i in label:
    print(i.text)