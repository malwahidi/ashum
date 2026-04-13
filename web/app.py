"""
Ashum Web Dashboard
===================
Premium Arabic financial dashboard for monitoring the trading bot.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="أسهم - لوحة التحكم",
    page_icon="\U0001f4b9",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Premium Arabic Financial Theme ──
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&display=swap" rel="stylesheet">
<style>
    /* ═══ Base ═══ */
    html, body, [class*="css"] {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Tajawal', sans-serif !important;
    }
    .main { background: #f0f2f6 !important; }
    .main .block-container {
        direction: rtl !important;
        padding: 1.5rem 2rem 4rem 2rem;
        max-width: 1200px;
    }

    /* ═══ Hide Streamlit chrome ═══ */
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stToolbar"] { display: none; }

    /* ═══ Sidebar ═══ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f2027 0%, #203a43 50%, #2c5364 100%) !important;
        direction: rtl !important;
        text-align: right !important;
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] .stRadio > div {
        direction: rtl !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        padding: 6px 0;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.1) !important;
    }

    /* ═══ Metrics ═══ */
    [data-testid="stMetric"] {
        background: #fff;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 1px 8px rgba(0,0,0,0.06);
        border: 1px solid #e8ecf1;
        direction: rtl !important;
        text-align: center !important;
        transition: transform 0.15s, box-shadow 0.15s;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    [data-testid="stMetric"] label {
        color: #64748b !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #1e293b !important;
        font-weight: 800 !important;
        font-size: 1.6rem !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        direction: ltr !important;
    }

    /* ═══ Typography ═══ */
    h1 {
        font-weight: 900 !important;
        font-size: 2rem !important;
        color: #0f2027 !important;
        text-align: center !important;
        margin-bottom: 0.2rem !important;
    }
    h2 {
        font-weight: 800 !important;
        color: #1e3a5f !important;
        font-size: 1.35rem !important;
        border-bottom: 3px solid #10b981;
        padding-bottom: 8px;
        display: inline-block;
    }
    h3 {
        font-weight: 700 !important;
        color: #334155 !important;
        font-size: 1.15rem !important;
    }
    p, span, div { color: #475569; }

    /* ═══ Section Cards ═══ */
    .section-card {
        background: #fff;
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
        box-shadow: 0 1px 8px rgba(0,0,0,0.05);
        border: 1px solid #e8ecf1;
    }
    .section-header {
        font-family: 'Tajawal', sans-serif;
        font-weight: 800;
        font-size: 1.2rem;
        color: #1e3a5f;
        margin-bottom: 16px;
        padding-bottom: 10px;
        border-bottom: 2px solid #e8ecf1;
        text-align: right;
    }

    /* ═══ Status Badges ═══ */
    .badge-healthy {
        display: inline-block;
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        color: #065f46;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .badge-danger {
        display: inline-block;
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        color: #991b1b;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .badge-caution {
        display: inline-block;
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        color: #92400e;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
    }

    /* ═══ Tables ═══ */
    [data-testid="stDataFrame"] {
        direction: rtl !important;
    }
    [data-testid="stDataFrame"] th {
        text-align: right !important;
        background-color: #f8fafc !important;
        color: #475569 !important;
        font-weight: 700 !important;
    }
    [data-testid="stDataFrame"] td {
        color: #334155 !important;
    }

    /* ═══ Buttons ═══ */
    .stButton > button {
        font-family: 'Tajawal', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 10px;
        padding: 0.6rem 2.5rem;
        font-size: 1rem !important;
        transition: all 0.2s;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #059669, #10b981) !important;
        border: none !important;
        color: #fff !important;
        box-shadow: 0 3px 12px rgba(16,185,129,0.3);
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 5px 20px rgba(16,185,129,0.4);
        transform: translateY(-1px);
    }

    /* ═══ Alerts ═══ */
    .stAlert { direction: rtl !important; text-align: right !important; border-radius: 10px; }

    /* ═══ Inputs ═══ */
    .stTextInput input {
        direction: ltr !important;
        text-align: left !important;
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        font-size: 1.1rem !important;
        padding: 8px 14px;
    }
    .stTextInput input:focus {
        border-color: #10b981 !important;
        box-shadow: 0 0 0 3px rgba(16,185,129,0.15);
    }

    /* ═══ Containers ═══ */
    [data-testid="stExpander"] {
        background: #fff;
        border-radius: 12px;
        border: 1px solid #e8ecf1;
    }

    /* ═══ Dividers ═══ */
    hr { border-color: #e2e8f0 !important; margin: 1.5rem 0 !important; }

    /* ═══ Logo area ═══ */
    .logo-area {
        text-align: center;
        padding: 16px 0 8px 0;
    }
    .logo-area h1 {
        background: linear-gradient(135deg, #0f2027, #2c5364);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem !important;
        margin: 0 !important;
    }
    .logo-subtitle {
        text-align: center;
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──
page = st.sidebar.radio(
    "\U0001f4cb القائمة",
    ["الرئيسية", "المحفظة", "تحليل سهم", "سجل المسح"],
    index=0,
)
st.sidebar.divider()
st.sidebar.markdown("\U0001f4b9 **أسهم** — محلل السوق السعودي")
st.sidebar.caption("\u2705 أسهم نقية فقط (العصيمي)")
st.sidebar.caption(f"v1.0 | {date.today()}")


def page_home():
    # Header
    st.markdown('<div class="logo-area"><h1>\U0001f4b9 أسهم</h1></div>', unsafe_allow_html=True)
    st.markdown(f'<p class="logo-subtitle">لوحة تحكم السوق السعودي | {date.today()}</p>', unsafe_allow_html=True)

    st.markdown("")

    # Market Regime
    st.markdown("## \U0001f3e6 حالة السوق")
    try:
        from src.analysis.market_regime import detect_market_regime
        regime = detect_market_regime()

        status_ar = {"HEALTHY": "صحي", "CAUTION": "حذر", "DANGER": "خطر", "OVERSOLD": "تشبع بيعي"}.get(regime.status, regime.status)
        badge_class = {"HEALTHY": "badge-healthy", "CAUTION": "badge-caution", "DANGER": "badge-danger", "OVERSOLD": "badge-healthy"}.get(regime.status, "badge-caution")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div style="text-align:center;padding:8px 0"><span class="{badge_class}">{status_ar} \u2714</span></div>', unsafe_allow_html=True)
            st.caption("حالة السوق")
        col2.metric("مؤشر TASI", f"{regime.tasi_price:,.0f}")
        col3.metric("تغير 5 أيام", f"{regime.tasi_change_5d:+.1f}%")
    except Exception as e:
        st.warning(f"لا يمكن تحميل حالة السوق")

    st.divider()

    # Portfolio
    st.markdown("## \U0001f4bc المحفظة الافتراضية")
    try:
        from src.trading.paper_trader import get_portfolio, get_performance

        portfolio = get_portfolio()
        perf = get_performance()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("رأس المال", f"{portfolio['capital']:,.0f} ريال")
        col2.metric("قيمة المحفظة", f"{portfolio['portfolio_value']:,.0f} ريال")

        pnl = portfolio['total_unrealized_pnl']
        col3.metric("الربح/الخسارة", f"{pnl:+,.0f} ريال",
                     delta=f"{(pnl/portfolio['capital']*100) if portfolio['capital'] else 0:+.1f}%")
        col4.metric("نسبة الفوز", f"{perf.get('win_rate', 0)}%")

        if portfolio["open_positions"]:
            st.markdown("### الصفقات المفتوحة")
            positions_data = []
            for pos in portfolio["open_positions"]:
                positions_data.append({
                    "السهم": f"{pos['ticker']}.SR",
                    "الاسم": pos["stock_name"],
                    "النوع": "شراء" if pos["signal_type"] == "BUY" else "بيع",
                    "سعر الدخول": f"{pos['entry_price']:.2f}",
                    "السعر الحالي": f"{pos.get('current_price', pos['entry_price']):.2f}",
                    "الربح/الخسارة": f"{pos.get('current_pnl', 0):+,.0f} ريال",
                    "النسبة": f"{pos.get('current_pnl_pct', 0):+.1f}%",
                })
            st.dataframe(pd.DataFrame(positions_data), use_container_width=True, hide_index=True)
        else:
            st.info("\U0001f4a4 لا توجد صفقات مفتوحة — البوت سيفتح صفقات تلقائياً مع مسح الصباح")
    except Exception as e:
        st.warning(f"لا يمكن تحميل المحفظة")

    st.divider()

    # Scan Button
    st.markdown("## \U0001f50d مسح السوق")
    if st.button("\U0001f50d مسح الأسهم النقية الآن", type="primary"):
        with st.spinner("جاري مسح 198 سهم نقي..."):
            try:
                from src.analysis.screener import run_market_scan
                result = run_market_scan(save_to_db=False)

                col1, col2, col3 = st.columns(3)
                col1.metric("الأسهم المفحوصة", result["stats"]["total_scanned"])
                col2.metric("إشارات شراء", result["stats"]["buy_signals"])
                col3.metric("إشارات بيع", result["stats"]["sell_signals"])

                if result["top_buys"]:
                    st.markdown("### \U0001f7e2 أقوى إشارات الشراء")
                    buy_data = []
                    for s in result["top_buys"][:5]:
                        grade_ar = {"STRONG": "قوية \U0001f7e2", "MODERATE": "متوسطة \U0001f7e1", "WEAK": "ضعيفة \U0001f7e0"}.get(s.get("grade", ""), "")
                        buy_data.append({
                            "السهم": f"{s['ticker']}.SR",
                            "الاسم": s.get("stock_name", ""),
                            "السعر": f"{s.get('price', 0):.2f} ريال",
                            "القوة": f"{s['strength']}/100",
                            "الدرجة": grade_ar,
                            "وقف الخسارة": f"{s.get('stop_loss', 0):.2f}",
                            "الهدف": f"{s.get('take_profit', 0):.2f}",
                        })
                    st.dataframe(pd.DataFrame(buy_data), use_container_width=True, hide_index=True)

                if result["top_sells"]:
                    st.markdown("### \U0001f534 أقوى إشارات البيع")
                    sell_data = []
                    for s in result["top_sells"][:5]:
                        grade_ar = {"STRONG": "قوية \U0001f534", "MODERATE": "متوسطة \U0001f7e1", "WEAK": "ضعيفة \U0001f7e0"}.get(s.get("grade", ""), "")
                        sell_data.append({
                            "السهم": f"{s['ticker']}.SR",
                            "الاسم": s.get("stock_name", ""),
                            "السعر": f"{s.get('price', 0):.2f} ريال",
                            "القوة": f"{s['strength']}/100",
                            "الدرجة": grade_ar,
                        })
                    st.dataframe(pd.DataFrame(sell_data), use_container_width=True, hide_index=True)

            except Exception as e:
                st.error(f"حدث خطأ: {e}")


def page_portfolio():
    st.markdown('<div class="logo-area"><h1>\U0001f4bc المحفظة والأداء</h1></div>', unsafe_allow_html=True)
    st.markdown("")

    try:
        from src.trading.paper_trader import get_portfolio, get_performance, _load_data

        perf = get_performance()

        # Performance cards
        st.markdown("## \U0001f4ca الأداء العام")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("إجمالي الصفقات", perf.get("total_trades", 0))
        col2.metric("نسبة الفوز", f"{perf.get('win_rate', 0)}%")
        pnl = perf.get("total_pnl", 0)
        col3.metric("الربح/الخسارة", f"{pnl:+,.0f} ريال",
                     delta=f"{perf.get('total_return_pct', 0):+.1f}%")
        col4.metric("رأس المال", f"{perf.get('capital', 100000):,.0f} ريال")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("صفقات رابحة \U0001f7e2", perf.get("wins", 0))
        col2.metric("صفقات خاسرة \U0001f534", perf.get("losses", 0))
        col3.metric("متوسط الربح", f"{perf.get('avg_win', 0):+,.0f} ريال")
        col4.metric("متوسط الخسارة", f"{perf.get('avg_loss', 0):+,.0f} ريال")

        st.divider()

        # Open positions
        portfolio = get_portfolio()
        st.markdown("## \U0001f4cb الصفقات المفتوحة")
        if portfolio["open_positions"]:
            for pos in portfolio["open_positions"]:
                pnl = pos.get("current_pnl", 0)
                pnl_pct = pos.get("current_pnl_pct", 0)
                emoji = "\U0001f7e2" if pnl >= 0 else "\U0001f534"

                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                    col1.markdown(f"**{emoji} {pos['ticker']}.SR** — {pos['stock_name']}")
                    col2.metric("دخول", f"{pos['entry_price']:.2f}")
                    col3.metric("الحالي", f"{pos.get('current_price', pos['entry_price']):.2f}")
                    col4.metric("P&L", f"{pnl:+,.0f}", delta=f"{pnl_pct:+.1f}%")
        else:
            st.info("\U0001f4a4 لا توجد صفقات مفتوحة")

        st.divider()

        # Closed trades
        data = _load_data()
        closed = data.get("closed_trades", [])
        if closed:
            st.markdown("## \U0001f4dc سجل الصفقات المغلقة")
            closed_data = []
            for t in reversed(closed[-20:]):
                emoji = "\U0001f7e2" if t.get("final_pnl", 0) > 0 else "\U0001f534"
                closed_data.append({
                    "": emoji,
                    "السهم": f"{t['ticker']}.SR",
                    "دخول": f"{t.get('entry_price', 0):.2f}",
                    "خروج": f"{t.get('exit_price', 0):.2f}",
                    "السبب": t.get("exit_reason", ""),
                    "الربح": f"{t.get('final_pnl', 0):+,.0f} ريال",
                    "النسبة": f"{t.get('final_pnl_pct', 0):+.1f}%",
                    "المدة": f"{t.get('days_held', 0)} يوم",
                })
            st.dataframe(pd.DataFrame(closed_data), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"حدث خطأ: {e}")


def page_stock_analysis():
    st.markdown('<div class="logo-area"><h1>\U0001f4ca تحليل سهم</h1></div>', unsafe_allow_html=True)
    st.markdown("")

    col1, col2, _ = st.columns([1, 1, 3])
    with col1:
        ticker = st.text_input("رمز السهم", value="2222", max_chars=4)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze = st.button("\U0001f50d تحليل", type="primary")

    if analyze:
        with st.spinner(f"جاري تحليل {ticker}.SR..."):
            try:
                from src.data.fetcher import fetch_stock_history
                from src.data.tickers import get_stock_info, is_naqi
                from src.analysis.technical import compute_indicators, get_latest_indicators
                from src.analysis.signals import generate_signal

                stock_info = get_stock_info(ticker) or {"name": ticker, "sector": ""}
                naqi_badge = "\u2705 نقي" if is_naqi(ticker) else "\u274c غير نقي"

                st.markdown(f"## {ticker}.SR — {stock_info.get('name', ticker)}")
                st.markdown(f"القطاع: **{stock_info.get('sector', '')}** | {naqi_badge}")

                df = fetch_stock_history(ticker, period="1y")
                if df.empty:
                    st.error("لا توجد بيانات")
                    return

                # Price chart
                st.markdown("### السعر (سنة)")
                st.line_chart(df["Close"], use_container_width=True, color="#10b981")

                # Indicators
                if len(df) >= 200:
                    analyzed = compute_indicators(df)
                    indicators = get_latest_indicators(analyzed)

                    st.markdown("### المؤشرات الفنية")
                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("السعر", f"{indicators.get('close', 0):.2f}")
                    col2.metric("RSI", f"{indicators.get('RSI_14', 0):.1f}")
                    col3.metric("SMA 50", f"{indicators.get('SMA_50', 0):.2f}")
                    col4.metric("SMA 200", f"{indicators.get('SMA_200', 0):.2f}")

                    vol_ratio = indicators.get('Volume_Ratio', 0)
                    col5.metric("حجم التداول", f"{vol_ratio:.1f}x")

                    # Signal
                    signal = generate_signal(ticker, df)
                    if signal:
                        grade_ar = {"STRONG": "قوية", "MODERATE": "متوسطة", "WEAK": "ضعيفة"}.get(signal.get("grade", ""), "")
                        signal_ar = "شراء \U0001f7e2" if signal["signal_type"] == "BUY" else "بيع \U0001f534"

                        st.markdown(f"### إشارة {signal_ar} — {grade_ar} ({signal['strength']}/100)")

                        col1, col2 = st.columns(2)
                        col1.metric("وقف الخسارة", f"{signal.get('stop_loss', 0):.2f} ريال")
                        col2.metric("الهدف", f"{signal.get('take_profit', 0):.2f} ريال")

                        st.markdown("**الأسباب:**")
                        for reason in signal.get("reasons", []):
                            st.markdown(f"- {reason}")
                    else:
                        st.info("\U0001f7e1 لا توجد إشارة قوية حالياً لهذا السهم")
                else:
                    st.warning("بيانات غير كافية (أقل من 200 يوم)")

            except Exception as e:
                st.error(f"حدث خطأ: {e}")


def page_scan_history():
    st.markdown('<div class="logo-area"><h1>\U0001f4cb معلومات النظام</h1></div>', unsafe_allow_html=True)
    st.markdown("")

    from src.data.tickers import get_naqi_tickers, NAQI_LAST_UPDATED

    naqi = get_naqi_tickers()

    st.markdown("## \u2705 الأسهم النقية")

    col1, col2, col3 = st.columns(3)
    col1.metric("عدد الأسهم النقية", f"{len(naqi)} سهم")
    col2.metric("المصدر", "قائمة العصيمي")
    col3.metric("آخر تحديث", NAQI_LAST_UPDATED)

    st.divider()

    st.markdown("## \U0001f916 مكونات النظام")

    components = [
        {"المكون": "التحليل الفني", "الحالة": "\U0001f7e2 يعمل", "الوصف": "RSI, MACD, Bollinger, SMA, EMA, Volume"},
        {"المكون": "حالة السوق", "الحالة": "\U0001f7e2 يعمل", "الوصف": "كشف انهيارات TASI تلقائياً"},
        {"المكون": "قوة القطاعات", "الحالة": "\U0001f7e2 يعمل", "الوصف": "تصنيف القطاعات حسب الأداء"},
        {"المكون": "تحليل الأخبار", "الحالة": "\U0001f7e2 يعمل", "الوصف": "Argaam RSS + Gemini AI"},
        {"المكون": "التداول الافتراضي", "الحالة": "\U0001f7e2 يعمل", "الوصف": "100,000 ريال افتراضي"},
        {"المكون": "بوت تيليجرام", "الحالة": "\U0001f7e2 يعمل", "الوصف": "@ashum_market_bot"},
        {"المكون": "التداول الحقيقي", "الحالة": "\u23f3 قريباً", "الوصف": "المرحلة 4 — بعد نتائج التداول الافتراضي"},
    ]
    st.dataframe(pd.DataFrame(components), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("## \U0001f4c5 جدول المسح التلقائي")
    schedule = [
        {"الوقت": "10:15 ص", "المهمة": "مسح الصباح + فتح صفقات افتراضية"},
        {"الوقت": "كل 30 دقيقة", "المهمة": "فحص الصفقات المفتوحة (وقف خسارة / هدف)"},
        {"الوقت": "3:15 م", "المهمة": "ملخص نهاية اليوم"},
    ]
    st.dataframe(pd.DataFrame(schedule), use_container_width=True, hide_index=True)


# ── Router ──
if page == "الرئيسية":
    page_home()
elif page == "المحفظة":
    page_portfolio()
elif page == "تحليل سهم":
    page_stock_analysis()
elif page == "سجل المسح":
    page_scan_history()
