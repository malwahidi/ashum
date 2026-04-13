"""
Ashum Dashboard API Server
==========================
Flask server: serves the dashboard HTML + JSON API endpoints.
Run: python web/server.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, jsonify
from datetime import date

app = Flask(__name__, template_folder="templates")

# Refresh Arabic names on startup
from src.data.tickers import refresh_arabic_names
refresh_arabic_names()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/market")
def api_market():
    try:
        from src.analysis.market_regime import detect_market_regime
        regime = detect_market_regime()
        return jsonify({
            "status": regime.status,
            "tasi_price": regime.tasi_price,
            "tasi_change_5d": regime.tasi_change_5d,
            "tasi_rsi": regime.tasi_rsi,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/portfolio")
def api_portfolio():
    try:
        from src.trading.paper_trader import get_portfolio, get_performance
        portfolio = get_portfolio()
        perf = get_performance()
        return jsonify({"portfolio": portfolio, "performance": perf})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/scan")
def api_scan():
    try:
        from src.analysis.screener import run_market_scan
        result = run_market_scan(save_to_db=False)
        return jsonify({
            "stats": result["stats"],
            "top_buys": result["top_buys"][:5],
            "top_sells": result["top_sells"][:5],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stock/<ticker>")
def api_stock(ticker):
    try:
        from src.data.fetcher import fetch_stock_history
        from src.data.tickers import get_stock_info, is_naqi
        from src.analysis.technical import compute_indicators, get_latest_indicators
        from src.analysis.signals import generate_signal

        info = get_stock_info(ticker) or {"name": ticker, "sector": ""}
        df = fetch_stock_history(ticker, period="6mo")

        if df.empty:
            return jsonify({"error": "no data"}), 404

        prices = [{"date": str(d.date()), "close": float(r["Close"])} for d, r in df.tail(60).iterrows()]

        result = {"info": info, "naqi": is_naqi(ticker), "prices": prices}

        if len(df) >= 200:
            analyzed = compute_indicators(df)
            indicators = get_latest_indicators(analyzed)
            signal = generate_signal(ticker, df)
            result["indicators"] = indicators
            result["signal"] = signal

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8501, debug=False)
