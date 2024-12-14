import pandas as pd
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import List, Optional, Literal

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    ElementClickInterceptedException, 
    NoSuchElementException
)

from pykrx import stock

class StockDataCrawler:
    def __init__(self, base_url="https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd="):
        """
        주식 데이터 크롤러 초기화
        
        Args:
            base_url (str): 크롤링할 기본 URL
        """
        self.base_url = base_url
        self.logger = self._setup_logger()
        self.webdriver_options = self._configure_webdriver_options()

    @staticmethod
    def _setup_logger():
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s'
        )
        return logging.getLogger(__name__)

    def _configure_webdriver_options(self):
        """
        Selenium WebDriver 옵션 설정
        
        Returns:
            webdriver.ChromeOptions: 구성된 WebDriver 옵션
        """
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        return options

    def _get_market_price(self, stock_code):
        """
        특정 주식의 현재 시장 가격 조회
        
        Args:
            stock_code (str): 주식 코드
        
        Returns:
            float: 현재 주식 가격
        """
        try:
            today = datetime.now()
            if today.weekday() in [5, 6]:  # 주말 처리
                target_date = today - timedelta(days=1 if today.weekday() == 5 else 2)
            else:
                target_date = today

            formatted_date = target_date.strftime("%Y%m%d")
            market_price = stock.get_market_ohlcv_by_date(formatted_date, formatted_date, stock_code).iloc[-1]['종가']
            
            return market_price
        except Exception as e:
            self.logger.error(f"시장 가격 조회 중 오류: {e}")
            return None

    def _crawl_stock_data(self, stock_code):
        """
        개별 주식의 재무 데이터 크롤링
        
        Args:
            stock_code (str): 주식 코드
        
        Returns:
            dict or None: 크롤링된 주식 데이터
        """
        url = self.base_url + stock_code
        
        try:
            with webdriver.Chrome(options=self.webdriver_options) as browser:
                browser.get(url)
                time.sleep(1)

                # 연간 탭 클릭
                annual_tab = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div/form/div[1]/div/div[2]/div[3]/div/div/table[2]/tbody/tr/td[3]"))
                )
                annual_tab.click()
                time.sleep(1)

                # 재무 테이블 선택
                table = browser.find_element(By.XPATH, '//table[@class="gHead01 all-width" and @summary="주요재무정보를 제공합니다."]')
                html_content = table.get_attribute('outerHTML')
                
                df = pd.read_html(html_content)[0]

                # 재무 지표 추출
                columns_map = {
                    "operating_profit": 1,  
                    "eps": 25,             
                    "per": 26              
                }

                result = {
                    metric: {year: df[df.columns[-(3 - i)]][index] for i, year in enumerate([2024, 2025, 2026])}
                    for metric, index in columns_map.items()
                }

                # 컨센서스 데이터 확인
                if any(pd.isna(result["operating_profit"][year]) for year in [2024, 2025, 2026]):
                    return None

                # 현재가 및 종목명 추출
                stock_name = stock.get_market_ticker_name(stock_code)
                market_price = self._get_market_price(stock_code)

                return self._format_stock_data(
                    stock_code, stock_name, market_price, result
                )

        except Exception as e:
            self.logger.error(f"주식 코드 {stock_code} 크롤링 중 오류: {e}")
            return None

    @staticmethod
    def _format_stock_data(stock_code, stock_name, market_price, result):
        """
        크롤링된 데이터 포맷팅
        
        Args:
            stock_code (str): 주식 코드
            stock_name (str): 주식 이름
            market_price (float): 현재 시장 가격
            result (dict): 크롤링된 재무 지표
        
        Returns:
            dict: 포맷팅된 주식 데이터
        """
        per_2024 = result["per"][2024]
        
        data = {
            "종목코드": str(stock_code),
            "종목명": stock_name,
            "현재가": str(int(market_price)),
            "영업이익(2024)": str(int(result["operating_profit"][2024])),
            "영업이익(2025)": str(int(result["operating_profit"][2025])),
            "영업이익(2026)": str(int(result["operating_profit"][2026])),
            "EPS(2024)": str(int(result["eps"][2024])),
            "EPS(2025)": str(int(result["eps"][2025])),
            "EPS(2026)": str(int(result["eps"][2026])),
            "PER(2024)": str(int(per_2024)),
            "목표가(2024)": str(int(result["eps"][2024] * per_2024)),
            "목표가(2025)": str(int(result["eps"][2025] * per_2024)),
            "목표가(2026)": str(int(result["eps"][2026] * per_2024))
        }
        
        return data

    def crawl_stocks(
        self, 
        market: Optional[Literal['KOSPI', 'KOSDAQ', 'ALL']] = 'ALL', 
        stock_list: Optional[List[str]] = None, 
        custom_stocks: Optional[List[str]] = None,  # 추가된 파라미터
        max_workers: int = 10
    ):
        """
        주식 목록 크롤링
        
        Args:
            market (str): 크롤링할 시장 ('KOSPI', 'KOSDAQ', 'ALL')
            stock_list (list, optional): 크롤링할 주식 코드 목록
            custom_stocks (list, optional): 사용자 지정 종목코드 리스트
            max_workers (int, optional): 동시 크롤링 스레드 수
        
        Returns:
            pandas.DataFrame: 크롤링된 주식 데이터
        """
        start_time = time.time()

        # 주식 리스트 설정 우선순위
        # 1. custom_stocks (사용자 지정 종목)
        # 2. stock_list (기존 파라미터)
        # 3. market 기반 자동 선택
        if custom_stocks is not None:
            stock_list = custom_stocks
        elif stock_list is None:
            if market == 'KOSPI':
                stock_list = stock.get_market_ticker_list(market="KOSPI")
            elif market == 'KOSDAQ':
                stock_list = stock.get_market_ticker_list(market="KOSDAQ")
            else:  # ALL
                stock_list = (
                    stock.get_market_ticker_list(market="KOSPI") + 
                    stock.get_market_ticker_list(market="KOSDAQ")
                )

        # 병렬 크롤링 (이하 기존 코드와 동일)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            stock_data = list(filter(None, executor.map(self._crawl_stock_data, stock_list)))

        # DataFrame 생성
        df = pd.DataFrame(stock_data)
        
        # 열 순서 지정
        column_order = [
            "종목코드", "종목명", "현재가", 
            "영업이익(2024)", "영업이익(2025)", "영업이익(2026)", 
            "EPS(2024)", "EPS(2025)", "EPS(2026)", 
            "PER(2024)", "목표가(2024)", "목표가(2025)", "목표가(2026)"
        ]
        df = df[column_order]

        # CSV 저장
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 파일명 생성 로직 개선
        if custom_stocks:
            market_suffix = "CUSTOM"
        else:
            market_suffix = market if market != 'ALL' else 'TOTAL'
        
        csv_file_name = f"financial_data_{market_suffix}_{current_time}.csv"
        
        df.to_csv(csv_file_name, index=False, encoding='utf-8-sig')

        end_time = time.time()
        self.logger.info(f"크롤링 완료. 총 소요 시간: {end_time - start_time:.2f}초")
        
        return df

def main():
    crawler = StockDataCrawler()
    
    # 사용자 지정 종목코드로 크롤링
    custom_stocks = ['005930', '000660', '035420']  # 예시 종목코드
    
    start = time.time()
    custom_df = crawler.crawl_stocks(custom_stocks=custom_stocks)
    end = time.time()
    print(f"작업 실행 시간: {end - start:.2f}초")
    
    # 기존 시장별 크롤링 방식도 유지
    kospi_df = crawler.crawl_stocks(market='KOSPI')
    kosdaq_df = crawler.crawl_stocks(market='KOSDAQ')

if __name__ == "__main__":
    main()