import FinanceDataReader as fdr
import pandas as pd
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


class StockDataHandler:
    def __init__(self, db_name="stock_data.db"):
        self.db_name = db_name
        self.create_saving_stock_data_table()

    def create_saving_stock_data_table(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS stock_prices
                        (date TEXT, code TEXT, name TEXT, open REAL, high REAL, low REAL, close REAL, volume INTEGER)"""
        )
        conn.commit()
        conn.close()

    def truncate_stock_data_table(self):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("""DELETE FROM stock_prices""")
            conn.commit()
            conn.close()
            print("Table truncated successfully")
        except Exception as e:
            print(f"Error truncating table: {e}")

    def read_stock_data(self, symbol, start_date, end_date):
        data = fdr.DataReader(symbol, start_date, end_date)
        return data

    def get_korean_stock_symbols(self):
        krx = fdr.StockListing("KRX")
        symbols_dict = dict(zip(krx["Name"], krx["Code"]))
        return symbols_dict

    def save_stock_data_for_period(self, start_date, end_date):
        symbols = self.get_korean_stock_symbols()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(
                    self.save_stock_data_for_symbol, name, code, start_date, end_date
                )
                for name, code in symbols.items()
            ]

            for future in tqdm(futures, desc="Saving stock data", unit="symbol"):
                future.result()

    def save_stock_data_for_symbol(self, name, code, start_date, end_date):
        try:
            print(f"Processing {name} ({code}) from {start_date} to {end_date}")
            data = self.read_stock_data(code, start_date, end_date)
            if not data.empty:
                conn = sqlite3.connect(self.db_name)
                c = conn.cursor()
                for index, row in data.iterrows():
                    c.execute(
                        """INSERT INTO stock_prices (date, code, name, open, high, low, close, volume)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            index.strftime("%Y-%m-%d"),
                            code,
                            name,
                            row["Open"],
                            row["High"],
                            row["Low"],
                            row["Close"],
                            row["Volume"],
                        ),
                    )
                conn.commit()
                conn.close()
                print(f"Saved data for {name} from {start_date} to {end_date}")
            else:
                print(f"No data for {name} from {start_date} to {end_date}")
        except Exception as e:
            print(f"Error processing {name} from {start_date} to {end_date}: {e}")

    def fetch_stock_data_from_db(self, code, start_date, end_date):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute(
            """SELECT * FROM stock_prices WHERE code = ? AND date BETWEEN ? AND ?""",
            (code, start_date, end_date),
        )
        results = c.fetchall()
        conn.close()
        if results:
            return [
                {
                    "date": result[0],
                    "code": result[1],
                    "name": result[2],
                    "open": result[3],
                    "high": result[4],
                    "low": result[5],
                    "close": result[6],
                    "volume": result[7],
                }
                for result in results
            ]
        else:
            return []


if __name__ == "__main__":
    handler = StockDataHandler()
    handler.save_stock_data_for_period("2023-01-01", "2023-12-31")
