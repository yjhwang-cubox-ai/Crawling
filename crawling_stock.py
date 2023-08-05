import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import os

options = webdriver.ChromeOptions()
# 창 숨기는 옵션 추가
options.add_argument("headless")

browser = webdriver.Chrome(options=options)
# browser.maximize_window()

#1. 페이지 이동
url = "https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd=005930"
browser.get(url)

# 재무재표 연간 탭 클릭
checkbox = browser.find_element(By.ID, 'cns_Tab21')
checkbox.click()

#매출액: //*[@id="aFVlanREZS"]/table[2]/tbody/tr[1]
#당기순이익: //*[@id="aFVlanREZS"]/table[2]/tbody/tr[5]
#eps: //*[@id="aFVlanREZS"]/table[2]/tbody/tr[26]

array1 = []
array2 = []
array3 = []

row1 = browser.find_element(By.XPATH, '//*[@id="aFVlanREZS"]/table[2]/tbody/tr[1]')
values = row1.find_elements(By.TAG_NAME, 'span')
for i in values:
    array1.append(i.text)

row2 = browser.find_element(By.XPATH, '//*[@id="aFVlanREZS"]/table[2]/tbody/tr[5]')
values = row2.find_elements(By.TAG_NAME, 'span')
for i in values:
    array2.append(i.text)

row3 = browser.find_element(By.XPATH, '//*[@id="aFVlanREZS"]/table[2]/tbody/tr[26]')
values = row3.find_elements(By.TAG_NAME, 'span')
for i in values:
    array3.append(i.text)

array1 = [array1[-3], array1[-2], array1[-1]]
array2 = [array2[-3], array2[-2], array2[-1]]
array3 = [array3[-3], array3[-2], array3[-1]]

'''
items = ['매출액', '당기순이익', 'EPS(원)']

table = browser.find_element(By.XPATH, '//*[@id="aFVlanREZS"]/table[2]/tbody')
labels = table.find_elements(By.TAG_NAME, 'th')

array1 = []
array2 = []
array3 = []

for label in labels:
    if label.text in items[0]:
        parent = label.find_element(By.XPATH, '..')        
        values = parent.find_elements(By.TAG_NAME, 'span')
        for i in values:
            array1.append(i.text)
    elif label.text in items[1]:
        parent = label.find_element(By.XPATH, '..')        
        values = parent.find_elements(By.TAG_NAME, 'span')
        for i in values:
            array2.append(i.text)
    elif label.text in items[2]:
        parent = label.find_element(By.XPATH, '..')        
        values = parent.find_elements(By.TAG_NAME, 'span')
        for i in values:
            array3.append(i.text)
    else:
        continue

browser.quit()
'''

print("매출액", "   ", array1)
print("당기순이익", "   ", array2)
print("EPS(원)", "   ", array3)