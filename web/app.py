"""
Ashum Web Dashboard
===================
Personal dashboard to monitor the trading bot visually.
Run: streamlit run web/app.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from datetime import date

# Page config
st.set_page_config(
    page_title="أسهم - لوحة التحكم",
    page_icon="\U0001f4b9",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Professional RTL Arabic theme
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
    /* RTL + Arabic Font */
    html, body, [class*="css"] {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Tajawal', sans-serif !important;
    }

    /* Main area */
    .main .block-container {
        direction: rtl !important;
        padding-top: 2rem;
    }

    /* Sidebar RTL */
    [data-testid="stSidebar"] {
        direction: rtl !important;
        text-align: right !important;
    }
    [data-testid="stSidebar"] .stRadio > div {
        direction: rtl !important;
    }

    /* Metric cards styling */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        direction: rtl !important;
        text-align: center !important;
    }
    [data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        direction: ltr !important;
    }

    /* Headers */
    h1, h2, h3, h4 {
        font-family: 'Tajawal', sans-serif !important;
        font-weight: 800 !important;
    }
    h2 { color: #38bdf8 !important; }
    h3 { color: #e2e8f0 !important; }

    /* Tables */
    .stDataFrame {
        direction: rtl !important;
    }
    [data-testid="stDataFrame"] th {
        text-align: right !important;
        background-color: #1e293b !important;
        color: #94a3b8 !important;
    }

    /* Buttons */
    .stButton > button {
        font-family: 'Tajawal', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 8px;
        padding: 0.5rem 2rem;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #059669, #10b981) !important;
        border: none !important;
    }

    /* Info/Warning boxes */
    .stAlert {
        direction: rtl !important;
        text-align: right !important;
        border-radius: 8px;
    }

    /* Container borders */
    [data-testid="stVerticalBlock"] > div:has(> [data-testid="stContainer"]) {
        border-radius: 12px;
    }

    /* Input fields RTL */
    .stTextInput input {
        direction: ltr !important;
        text-align: left !important;
    }

    /* Positive/Negative colors */
    .profit { color: #10b981 !important; font-weight: 700; }
    .loss { color: #ef4444 !important; font-weight: 700; }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Custom divider */
    hr {
        border-color: #334155 !important;
        margin: 1.5rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
page = st.sidebar.radio(
    "\U0001f4cb القائمة",
    ["الرئيسية", "المحفظة", "تحليل سهم", "سجل المسح"],
    index=0,
)


def page_home():
    """Main dashboard page."""
    st.markdown("## \U0001f4b9 أسهم - لوحة التحكم")
    st.caption(f"التاريخ: {date.today()}")

    # Market Regime
    st.markdown("### \U0001f3e6 حالة السوق")
    try:
        from src.analysis.market_regime import detect_market_regime
        regime = detect_market_regime()

        col1, col2, col3 = st.columns(3)
        status_color = "green" if regime.status == "HEALTHY" else "orange" if regime.status == "CAUTION" else "red"
        status_ar = {"HEALTHY": "صحي", "CAUTION": "حذر", "DANGER": "خطر", "OVERSOLD": "تشبع بيعي"}.get(regime.status, regime.status)

        col1.metric("حالة السوق", status_ar)
        col2.metric("مؤشر TASI", f"{regime.tasi_price:,.0f}")
        col3.metric("تغير 5 أيام", f"{regime.tasi_change_5d:+.1f}%")
    except Exception as e:
        st.warning(f"لا يمكن تحميل حالة السوق: {e}")

    st.divider()

    # Portfolio Summary
    st.markdown("### \U0001f4bc المحفظة الافتراضية")
    try:
        from src.trading.paper_trader import get_portfolio, get_performance

        portfolio = get_portfolio()
        perf = get_performance()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("رأس المال", f"{portfolio['capital']:,.0f} ريال")
        col2.metric("قيمة المحفظة", f"{portfolio['portfolio_value']:,.0f} ريال")
        col3.metric("الربح/الخسارة", f"{portfolio['total_unrealized_pnl']:+,.0f} ريال")
        col4.metric("نسبة الفوز", f"{perf.get('win_rate', 0)}%")

        # Open positions
        if portfolio["open_positions"]:
            st.markdown("#### الصفقات المفتوحة")
            positions_data = []
            for pos in portfolio["open_positions"]:
                positions_data.append({
                    "السهم": f"{pos['ticker']}.SR",
                    "الاسم": pos["stock_name"],
                    "النوع": pos["signal_type"],
                    "سعر الدخول": pos["entry_price"],
                    "السعر الحالي": pos.get("current_price", pos["entry_price"]),
                    "الربح/الخسارة": f"{pos.get('current_pnl', 0):+,.0f}",
                    "النسبة": f"{pos.get('current_pnl_pct', 0):+.1f}%",
                    "وقف الخسارة": pos["stop_loss"],
                    "الهدف": pos["take_profit"],
                })
            st.dataframe(pd.DataFrame(positions_data), use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد صفقات مفتوحة")

    except Exception as e:
        st.warning(f"لا يمكن تحميل المحفظة: {e}")

    st.divider()

    # Quick Scan
    st.markdown("### \U0001f50d آخر إشارات")
    if st.button("مسح السوق الآن", type="primary"):
        with st.spinner("جاري المسح..."):
            try:
                from src.analysis.screener import run_market_scan
                result = run_market_scan(save_to_db=False)

                col1, col2, col3 = st.columns(3)
                col1.metric("الأسهم المفحوصة", result["stats"]["total_scanned"])
                col2.metric("إشارات شراء", result["stats"]["buy_signals"])
                col3.metric("إشارات بيع", result["stats"]["sell_signals"])

                # Top buys
                if result["top_buys"]:
                    st.markdown("#### \U0001f7e2 أقوى إشارات الشراء")
                    buy_data = []
                    for s in result["top_buys"][:5]:
                        grade_ar = {"STRONG": "قوية", "MODERATE": "متوسطة", "WEAK": "ضعيفة"}.get(s.get("grade", ""), "")
                        buy_data.append({
                            "السهم": f"{s['ticker']}.SR",
                            "الاسم": s.get("stock_name", ""),
                            "السعر": f"{s.get('price', 0):.2f}",
                            "القوة": f"{s['strength']}/100",
                            "الدرجة": grade_ar,
                            "وقف": f"{s.get('stop_loss', 0):.2f}",
                            "هدف": f"{s.get('take_profit', 0):.2f}",
                        })
                    st.dataframe(pd.DataFrame(buy_data), use_container_width=True, hide_index=True)

                # Top sells
                if result["top_sells"]:
                    st.markdown("#### \U0001f534 أقوى إشارات البيع")
                    sell_data = []
                    for s in result["top_sells"][:5]:
                        grade_ar = {"STRONG": "قوية", "MODERATE": "متوسطة", "WEAK": "ضعيفة"}.get(s.get("grade", ""), "")
                        sell_data.append({
                            "السهم": f"{s['ticker']}.SR",
                            "الاسم": s.get("stock_name", ""),
                            "السعر": f"{s.get('price', 0):.2f}",
                            "القوة": f"{s['strength']}/100",
                            "الدرجة": grade_ar,
                        })
                    st.dataframe(pd.DataFrame(sell_data), use_container_width=True, hide_index=True)

            except Exception as e:
                st.error(f"حدث خطأ: {e}")


def page_portfolio():
    """Portfolio and performance page."""
    st.markdown("## \U0001f4bc المحفظة والأداء")

    try:
        from src.trading.paper_trader import get_portfolio, get_performance, _load_data

        # Performance stats
        perf = get_performance()

        st.markdown("### \U0001f4ca أداء التداول")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("إجمالي الصفقات", perf.get("total_trades", 0))
        col2.metric("نسبة الفوز", f"{perf.get('win_rate', 0)}%")
        pnl = perf.get("total_pnl", 0)
        col3.metric("الربح/الخسارة", f"{pnl:+,.0f} ريال", delta=f"{perf.get('total_return_pct', 0):+.1f}%")
        col4.metric("رأس المال", f"{perf.get('capital', 100000):,.0f} ريال")

        col1, col2 = st.columns(2)
        col1.metric("صفقات رابحة", perf.get("wins", 0))
        col2.metric("صفقات خاسرة", perf.get("losses", 0))

        st.divider()

        # Open positions
        portfolio = get_portfolio()
        st.markdown("### الصفقات المفتوحة")
        if portfolio["open_positions"]:
            for pos in portfolio["open_positions"]:
                pnl = pos.get("current_pnl", 0)
                color = "green" if pnl >= 0 else "red"
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns(4)
                    col1.markdown(f"**{pos['ticker']}.SR** ({pos['stock_name']})")
                    col2.write(f"دخول: {pos['entry_price']:.2f}")
                    col3.write(f"الحالي: {pos.get('current_price', pos['entry_price']):.2f}")
                    col4.markdown(f":{color}[{pnl:+,.0f} ريال ({pos.get('current_pnl_pct', 0):+.1f}%)]")
        else:
            st.info("لا توجد صفقات مفتوحة")

        st.divider()

        # Closed trades history
        data = _load_data()
        closed = data.get("closed_trades", [])
        if closed:
            st.markdown("### سجل الصفقات المغلقة")
            closed_data = []
            for t in reversed(closed[-20:]):  # Last 20
                closed_data.append({
                    "السهم": f"{t['ticker']}.SR",
                    "النوع": t.get("signal_type", ""),
                    "دخول": t.get("entry_price", 0),
                    "خروج": t.get("exit_price", 0),
                    "السبب": t.get("exit_reason", ""),
                    "الربح": f"{t.get('final_pnl', 0):+,.0f}",
                    "النسبة": f"{t.get('final_pnl_pct', 0):+.1f}%",
                    "المدة": f"{t.get('days_held', 0)} يوم",
                })
            st.dataframe(pd.DataFrame(closed_data), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"حدث خطأ: {e}")


def page_stock_analysis():
    """Single stock analysis page."""
    st.markdown("## \U0001f4ca تحليل سهم")

    ticker = st.text_input("أدخل رمز السهم", value="2222", max_chars=4)

    if st.button("تحليل", type="primary"):
        with st.spinner(f"جاري تحليل {ticker}.SR..."):
            try:
                from src.data.fetcher import fetch_stock_history
                from src.data.tickers import get_stock_info
                from src.analysis.technical import compute_indicators, get_latest_indicators
                from src.analysis.signals import generate_signal

                stock_info = get_stock_info(ticker) or {"name": ticker, "sector": ""}
                st.markdown(f"### {ticker}.SR — {stock_info.get('name', ticker)}")
                st.caption(f"القطاع: {stock_info.get('sector', '')}")

                df = fetch_stock_history(ticker, period="1y")
                if df.empty:
                    st.error("لا توجد بيانات")
                    return

                # Price chart
                st.markdown("#### الرسم البياني")
                st.line_chart(df["Close"], use_container_width=True)

                # Volume chart
                st.bar_chart(df["Volume"].tail(60), use_container_width=True)

                # Indicators
                if len(df) >= 200:
                    analyzed = compute_indicators(df)
                    indicators = get_latest_indicators(analyzed)

                    st.markdown("#### المؤشرات الفنية")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("السعر", f"{indicators.get('close', 0):.2f} ريال")
                    col2.metric("RSI", f"{indicators.get('RSI_14', 0):.1f}")
                    col3.metric("SMA 50", f"{indicators.get('SMA_50', 0):.2f}")
                    col4.metric("SMA 200", f"{indicators.get('SMA_200', 0):.2f}")

                    # Signal
                    signal = generate_signal(ticker, df)
                    if signal:
                        grade_ar = {"STRONG": "قوية", "MODERATE": "متوسطة", "WEAK": "ضعيفة"}.get(signal.get("grade", ""), "")
                        signal_type = "شراء" if signal["signal_type"] == "BUY" else "بيع"
                        color = "green" if signal["signal_type"] == "BUY" else "red"

                        st.markdown(f"#### :{color}[إشارة {signal_type} — {grade_ar} ({signal['strength']}/100)]")

                        st.write("**الأسباب:**")
                        for reason in signal.get("reasons", []):
                            st.write(f"• {reason}")

                        col1, col2 = st.columns(2)
                        col1.metric("وقف الخسارة", f"{signal.get('stop_loss', 0):.2f}")
                        col2.metric("الهدف", f"{signal.get('take_profit', 0):.2f}")
                    else:
                        st.info("لا توجد إشارة قوية حالياً")

            except Exception as e:
                st.error(f"حدث خطأ: {e}")


def page_scan_history():
    """Scan history page."""
    st.markdown("## \U0001f4cb سجل المسح")
    st.info("سيتم تفعيل هذه الصفحة بعد تجميع بيانات المسح خلال الأيام القادمة.")

    # Show naqi info
    from src.data.tickers import get_naqi_tickers, NAQI_LAST_UPDATED
    naqi = get_naqi_tickers()
    st.markdown("### معلومات الأسهم النقية")
    st.write(f"عدد الأسهم النقية: **{len(naqi)}** سهم")
    st.write(f"آخر تحديث للقائمة: **{NAQI_LAST_UPDATED}**")
    st.write(f"المصدر: قائمة العصيمي (Argaam.com)")


# Route pages
if page == "الرئيسية":
    page_home()
elif page == "المحفظة":
    page_portfolio()
elif page == "تحليل سهم":
    page_stock_analysis()
elif page == "سجل المسح":
    page_scan_history()

# Footer
st.sidebar.divider()
st.sidebar.caption("أسهم — محلل السوق السعودي")
st.sidebar.caption("أسهم نقية فقط (العصيمي)")
st.sidebar.caption(f"v1.0 | {date.today()}")
