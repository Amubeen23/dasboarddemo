from flask import Flask, render_template, jsonify, request
import yfinance as yf
import pandas as pd

app = Flask(__name__)

def get_stock_details(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        details = {
            'name': info.get('longName', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'employees': info.get('fullTimeEmployees', 'N/A'),
            'website': info.get('website', 'N/A'),
            'ratios': {
                'Forward P/E': info.get('forwardPE', 'N/A'),
                'PEG Ratio': info.get('pegRatio', 'N/A'),
                'Price to Book': info.get('priceToBook', 'N/A'),
                'Profit Margin': info.get('profitMargin', 'N/A'),
                'Operating Margin': info.get('operatingMargin', 'N/A'),
                'ROE': info.get('returnOnEquity', 'N/A'),
                'Beta': info.get('beta', 'N/A'),
                'Dividend Yield': info.get('dividendYield', 'N/A')
            }
        }
        return details
    except Exception as e:
        print(f"Error fetching details for {symbol}: {str(e)}")
        return None


def get_stock_data(symbols):
    data = {}
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1mo", interval="1d")  #1-month data
            info = stock.info
            details = get_stock_details(symbol)
            
            # Debugging Data
            print(f"\n--- Debugging {symbol} ---")
            print("Historical Data:", hist)
            print("Dates:", [d.strftime('%Y-%m-%d') for d in hist.index.tolist()] if not hist.empty else [])
            print("Prices:", hist['Close'].tolist() if not hist.empty else [])
            print("Info:", info)
            print("Details:", details)

            # missing data
            if hist.empty:
                print(f"Data for {symbol} is empty!")
                continue

            # last 30 points
            historical = hist['Close'].tolist()[-30:] if 'Close' in hist else []
            dates = [d.strftime('%Y-%m-%d') for d in hist.index.tolist()][-30:] if not hist.empty else []

            data[symbol] = {
                'current_price': round(hist['Close'].iloc[-1], 2) if not hist.empty else 0,
                'change': round(((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100), 2) if len(hist) >= 2 else 0,
                'volume': int(hist['Volume'].iloc[-1]) if 'Volume' in hist else 0,
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else 'N/A',
                'historical': historical,
                'dates': dates,
                'details': details
            }
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            continue
    return data


@app.route('/')
def dashboard():
    portfolio = ['AAPL', 'MSFT', 'JPM']  
    stock_data = get_stock_data(portfolio)
    print("Stock data:", stock_data)  # Debug
    return render_template('dashboard.html', stocks=stock_data if stock_data else {})


@app.route('/add_stock', methods=['POST'])
def add_stock():
    symbol = request.form['symbol'].upper()
    stock_data = get_stock_data([symbol])
    
    if symbol in stock_data and stock_data[symbol]['historical'] and stock_data[symbol]['dates']:
        return jsonify(stock_data[symbol])  
    return jsonify({'error': 'Invalid or incomplete stock data'}), 400



if __name__ == '__main__':
    app.run(debug=True)