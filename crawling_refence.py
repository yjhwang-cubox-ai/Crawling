import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

browser = webdriver.Chrome()
browser.maximize_window()

#1. 페이지 이동
url = "https://finance.naver.com/sise/sise_market_sum.naver"
# url = "https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd=005930"
browser.get(url)

#2. 조회 항목 초기화
checkboxes = browser.find_elements(By.NAME, 'fieldIds')
for checkbox in checkboxes:
    if checkbox.is_selected():
        checkbox.click()

item_to_select = ['영업이익', '자산총계', '매출액']
for checkbox in checkboxes:
    parent = checkbox.find_element(By.XPATH, "..")
    label = parent.find_element(By.TAG_NAME, "label")
    print(label.text)

    if label.text in item_to_select:
        checkbox.click()

btn_apply = browser.find_element(By.XPATH, "//a[@href='javascript:fieldSubmit()']")
btn_apply.click()


# 성공코드
# checkbox = browser.find_element(By.ID, 'cns_Tab21')
# checkbox.click()

while(True):
    pass