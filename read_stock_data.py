import FinanceDataReader as fdr
import pandas as pd 

def read_stock_data(ticker, start_date, end_date):
    data = fdr.DataReader(ticker, start_date, end_date)
    return data

def get_korean_stock_symbols():
    krx = fdr.StockListing('KRX')
    symbols_dict = dict(zip(krx['Name'], krx['Code']))
    return symbols_dict

def get_top_10_most_changed_stocks(start_date, end_date):
    symbols = get_korean_stock_symbols()
    changes = {}
    total_symbols = len(symbols)
    processed_symbols = 0
    for name, code in symbols.items():
        try:
            print(f"Processing {name} ({code})")
            data = read_stock_data(code, start_date, end_date)
            if not data.empty:
                change = (data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]
                changes[name] = change
                print(f"{name}: {change:.2%}")
            else:
                print(f"No data for {name}")
        except Exception as e:
            print(f"Error processing {name}: {e}")
        processed_symbols += 1
        print(f"Progress: {processed_symbols}/{total_symbols} ({(processed_symbols/total_symbols)*100:.2f}%)")
    sorted_changes = sorted(changes.items(), key=lambda x: x[1], reverse=True)
    return sorted_changes[:10]

if __name__ == "__main__":
    print(get_top_10_most_changed_stocks('2025-02-13', '2025-02-14'))
