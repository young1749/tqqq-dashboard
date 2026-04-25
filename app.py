from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__, static_folder='static')
CORS(app, resources={r"/*": {"origins": "*"}})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    return response

@app.route('/')
def index():
	return send_from_directory('static', 'index.html')
@app.route('/profit')
def profit():
	return send_from_directory('static', 'profit.html')
@app.route('/api/tqqq')
def tqqq_data():
    try:
        tk = yf.Ticker("TQQQ")
        df = tk.history(period="2y", interval="1d")
        if df.empty:
            return jsonify({"error": "데이터 없음"}), 500
        closes = df['Close'].round(2).tolist()
        dates = [d.strftime('%Y-%m-%d') for d in df.index]
        ma200 = pd.Series(closes).rolling(200, min_periods=200).mean().round(2).tolist()
        ma200 = [None if pd.isna(v) else v for v in ma200]
        last = closes[-1]
        prev = closes[-2] if len(closes) > 1 else last
        last_ma = next((v for v in reversed(ma200) if v is not None), None)
        return jsonify({
            "currentPrice": round(last, 2),
            "previousClose": round(prev, 2),
            "change": round(last - prev, 2),
            "changePct": round((last - prev) / prev * 100, 2),
            "ma200": round(last_ma, 2) if last_ma else None,
            "isAbove200": bool(last > last_ma) if last_ma else None,
            "dates": dates,
            "closes": closes,
            "ma200Series": ma200,
            "updatedAt": datetime.now().strftime('%H:%M:%S'),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    print("\n==================================================")
    print("  TQQQ 대시보드 서버 시작!")
    print("  브라우저에서 열기: http://127.0.0.1:5000")
    print("==================================================\n")
    app.run(debug=False, port=8080, host='0.0.0.0')
