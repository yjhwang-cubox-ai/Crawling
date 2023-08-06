import pandas as pd


def StockCodeList(path):
    stock_code = pd.read_excel(path, sheet_name = 'Sheet1', converters={'종목코드':str})
    stock_code = stock_code[['한글 종목명','단축코드']]
    stock_code.columns = ['Stock','Code']
    # print(stock_code)

    code_list = stock_code['Code'].values.tolist()
    # print(code_list)

    return stock_code