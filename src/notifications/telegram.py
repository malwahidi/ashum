import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import Bot, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, ContextTypes,
)

from config.settings import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, STRONG_THRESHOLD, MODERATE_THRESHOLD,
    STOP_LOSS_PERCENT, TAKE_PROFIT_PERCENT, TRAILING_STOP_ACTIVATION,
)
from src.data.tickers import get_stock_info
from src.notifications.charts import generate_stock_chart
from src.analysis.technical import compute_indicators, get_latest_indicators

logger = logging.getLogger(__name__)

RIYADH_TZ = ZoneInfo("Asia/Riyadh")


def format_signal_message(signal: dict) -> str:
    """تنسيق رسالة الإشارة بالعربي."""
    is_buy = signal["signal_type"] == "BUY"
    grade = signal.get("grade", "WEAK")

    if grade == "STRONG":
        grade_icon = "\U0001f7e2\U0001f7e2\U0001f7e2"
        grade_text = "قوية"
        safety_note = "إشارة بثقة عالية"
    elif grade == "MODERATE":
        grade_icon = "\U0001f7e1\U0001f7e1"
        grade_text = "متوسطة"
        safety_note = "ثقة متوسطة - كن حذراً في حجم الصفقة"
    else:
        grade_icon = "\U0001f7e0"
        grade_text = "ضعيفة"
        safety_note = "ثقة منخفضة - للمراقبة فقط، خطر في التنفيذ"

    action = "شراء" if is_buy else "بيع"
    action_icon = "\U0001f7e2" if is_buy else "\U0001f534"

    reasons_text = ""
    for reason in signal.get("reasons", []):
        reasons_text += f"  \u2022 {reason}\n"

    stop_loss = signal.get("stop_loss", 0)
    take_profit = signal.get("take_profit", 0)
    price = signal.get("price", 0)

    indicators = signal.get("indicators", {})
    rsi_val = indicators.get("RSI_14", "N/A")
    rsi_display = f"{rsi_val:.1f}" if isinstance(rsi_val, (int, float)) else rsi_val

    msg = (
        f"{action_icon} <b>إشارة {action}: {signal['ticker']}</b>\n"
        f"<b>{signal.get('stock_name', signal['ticker'])}</b> | {signal.get('sector', '')}\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"{grade_icon} الدرجة: <b>{grade_text}</b> ({signal['strength']}/100)\n"
        f"\U0001f4b0 السعر: <b>{price:.2f} ريال</b>\n"
        f"\U0001f4c8 RSI: {rsi_display}\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"\U0001f6e1 <b>إدارة المخاطر:</b>\n"
        f"  \U0001f6d1 وقف الخسارة: <b>{stop_loss:.2f} ريال</b> (-{STOP_LOSS_PERCENT}%)\n"
        f"  \U0001f3af الهدف: <b>{take_profit:.2f} ريال</b> (+{TAKE_PROFIT_PERCENT}%)\n"
        f"  \U0001f4ab وقف متحرك: يتفعل عند +{TRAILING_STOP_ACTIVATION}%\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"<b>الأسباب:</b>\n{reasons_text}\n"
    )

    # Add AI sentiment if available
    sentiment = signal.get("sentiment")
    if sentiment:
        msg += f"\U0001f9e0 <b>تحليل الذكاء الاصطناعي:</b>\n  {sentiment.to_arabic()}\n\n"

    msg += (
        f"\U0001f4a1 <i>{safety_note}</i>\n"
        f"\u26a0\ufe0f <i>ليست نصيحة مالية. استخدم وقف الخسارة لحماية رأس مالك.</i>"
    )

    return msg


def format_stock_info(ticker: str, indicators: dict, stock_info: dict) -> str:
    """تنسيق معلومات السهم بالعربي."""
    close = indicators.get("close", 0)
    rsi = indicators.get("RSI_14", 0)
    sma50 = indicators.get("SMA_50", 0)
    sma200 = indicators.get("SMA_200", 0)
    ema9 = indicators.get("EMA_9", 0)
    ema21 = indicators.get("EMA_21", 0)
    vol_ratio = indicators.get("Volume_Ratio", 0)

    trend = "\U0001f7e2 صاعد" if close > sma200 else "\U0001f534 هابط"
    momentum = "\U0001f7e2 إيجابي" if ema9 > ema21 else "\U0001f534 سلبي"

    if rsi < 30:
        rsi_status = "\U0001f7e2 تشبع بيعي (احتمال ارتداد)"
    elif rsi > 70:
        rsi_status = "\U0001f534 تشبع شرائي (احتمال تصحيح)"
    elif rsi > 55:
        rsi_status = "\U0001f7e2 صحي"
    elif rsi > 45:
        rsi_status = "\U0001f7e1 محايد"
    else:
        rsi_status = "\U0001f7e0 ضعيف"

    name = stock_info.get("name", ticker)
    sector = stock_info.get("sector", "")

    msg = (
        f"\U0001f4ca <b>{ticker} - {name}</b>\n"
        f"القطاع: {sector}\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"\U0001f4b0 السعر: <b>{close:.2f} ريال</b>\n"
        f"\U0001f4c8 الاتجاه العام: {trend}\n"
        f"\u26a1 الزخم قصير المدى: {momentum}\n"
        f"\U0001f4ca RSI(14): {rsi:.1f} - {rsi_status}\n"
        f"\U0001f4ca حجم التداول: {vol_ratio:.1f}x من المتوسط\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"<b>مستويات مهمة:</b>\n"
        f"  متوسط 50 يوم: {sma50:.2f}\n"
        f"  متوسط 200 يوم: {sma200:.2f}\n"
        f"  EMA 9: {ema9:.2f}\n"
        f"  EMA 21: {ema21:.2f}\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"\U0001f4a1 <b>لا توجد إشارة قوية حالياً.</b>\n"
        f"<i>البوت سينبهك عندما تتغير الظروف.</i>"
    )

    return msg


def format_scan_summary(scan_result: dict) -> str:
    """تنسيق ملخص المسح بالعربي."""
    stats = scan_result.get("stats", {})
    top_buys = scan_result.get("top_buys", [])
    top_sells = scan_result.get("top_sells", [])

    now = datetime.now(RIYADH_TZ).strftime("%Y-%m-%d %H:%M")

    # Market regime info
    market_regime = scan_result.get("market_regime")
    regime_text = market_regime.to_arabic() if market_regime else ""

    msg = (
        f"\U0001f50d <b>مسح الأسهم النقية - تداول</b>\n"
        f"\u2705 أسهم نقية فقط (العصيمي)\n"
        f"\U0001f4c5 {now} (الرياض)\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
    )

    if regime_text:
        msg += f"\U0001f3e6 <b>حالة السوق:</b>\n{regime_text}\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"

    msg += (
        f"\U0001f4ca الأسهم المفحوصة: {stats.get('total_scanned', 0)}\n"
        f"\U0001f7e2 إشارات شراء: {stats.get('buy_signals', 0)}\n"
        f"\U0001f534 إشارات بيع: {stats.get('sell_signals', 0)}\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
    )

    if top_buys:
        msg += "\U0001f7e2 <b>أقوى إشارات الشراء:</b>\n"
        for i, s in enumerate(top_buys[:5], 1):
            grade = s.get("grade", "WEAK")
            grade_icon = "\U0001f7e2" if grade == "STRONG" else "\U0001f7e1" if grade == "MODERATE" else "\U0001f7e0"
            grade_ar = "قوية" if grade == "STRONG" else "متوسطة" if grade == "MODERATE" else "ضعيفة"
            msg += (
                f"  {i}. {grade_icon} <b>{s['ticker']}</b> ({s.get('stock_name', '')})\n"
                f"     {s.get('price', 0):.2f} ريال | {grade_ar} [{s['strength']}/100]\n"
                f"     وقف: {s.get('stop_loss', 0):.2f} | هدف: {s.get('take_profit', 0):.2f}\n\n"
            )

    if top_sells:
        msg += "\U0001f534 <b>أقوى إشارات البيع:</b>\n"
        for i, s in enumerate(top_sells[:5], 1):
            grade = s.get("grade", "WEAK")
            grade_icon = "\U0001f534" if grade == "STRONG" else "\U0001f7e1" if grade == "MODERATE" else "\U0001f7e0"
            grade_ar = "قوية" if grade == "STRONG" else "متوسطة" if grade == "MODERATE" else "ضعيفة"
            msg += (
                f"  {i}. {grade_icon} <b>{s['ticker']}</b> ({s.get('stock_name', '')})\n"
                f"     {s.get('price', 0):.2f} ريال | {grade_ar} [{s['strength']}/100]\n\n"
            )

    if not top_buys and not top_sells:
        msg += (
            "\U0001f7e1 <b>لا توجد إشارات حالياً.</b>\n"
            "السوق في منطقة محايدة. البوت سينبهك\n"
            "عندما تظهر فرص قوية.\n\n"
            "\U0001f4a1 <i>هذا شيء جيد - يعني أن البوت\n"
            "يتحلى بالحذر ولا يعطيك إشارات محفوفة بالمخاطر.</i>\n\n"
        )

    msg += "\u26a0\ufe0f <i>ليست نصيحة مالية. استخدم وقف الخسارة دائماً.</i>"

    return msg


async def send_message(text: str, chat_id: str | None = None):
    """إرسال رسالة عبر تيليجرام."""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    target = chat_id or TELEGRAM_CHAT_ID
    try:
        await bot.send_message(
            chat_id=target,
            text=text,
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")


async def send_signal_with_chart(
    signal: dict,
    chart_df=None,
    chat_id: str | None = None,
):
    """إرسال إشارة مع رسم بياني."""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    target = chat_id or TELEGRAM_CHAT_ID

    msg = format_signal_message(signal)

    try:
        await bot.send_message(
            chat_id=target,
            text=msg,
            parse_mode=ParseMode.HTML,
        )

        if chart_df is not None and not chart_df.empty:
            analyzed_df = compute_indicators(chart_df)
            chart_buf = generate_stock_chart(
                analyzed_df,
                ticker=signal["ticker"],
                stock_name=signal.get("stock_name", signal["ticker"]),
                signal_type=signal["signal_type"],
                signal_strength=signal["strength"],
            )
            if chart_buf:
                await bot.send_photo(
                    chat_id=target,
                    photo=chart_buf,
                    caption=f"{signal['ticker']} - {signal.get('stock_name', '')}",
                )

    except Exception as e:
        logger.error(f"Failed to send signal with chart: {e}")


async def send_scan_results(scan_result: dict, stock_data: dict | None = None):
    """إرسال نتائج المسح الكامل."""
    summary = format_scan_summary(scan_result)
    await send_message(summary)

    top_buys = scan_result.get("top_buys", [])
    for signal in top_buys[:3]:
        chart_df = stock_data.get(signal["ticker"]) if stock_data else None
        await send_signal_with_chart(signal, chart_df)


# --- أوامر بوت تيليجرام ---

async def cmd_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مسح كامل للسوق."""
    await update.message.reply_text("\U0001f50d جاري مسح السوق... انتظر من فضلك (1-2 دقيقة).")

    from src.analysis.screener import run_market_scan
    from src.analysis.sentiment import analyze_stock_sentiment
    result = run_market_scan(save_to_db=False)

    # Add sentiment to top signals
    top_buys = result.get("top_buys", [])
    top_sells = result.get("top_sells", [])
    for signal in (top_buys[:5] + top_sells[:3]):
        try:
            sentiment = await analyze_stock_sentiment(signal["ticker"], signal.get("stock_name", ""))
            if sentiment:
                signal["sentiment"] = sentiment
                signal["strength"] = max(0, min(100, signal["strength"] + sentiment.score))
                from src.analysis.signals import get_signal_grade
                signal["grade"] = get_signal_grade(signal["strength"])
                if sentiment.score != 0:
                    signal["reasons"].append(f"تحليل ذكاء اصطناعي: {sentiment.summary}")
        except Exception as e:
            logger.error(f"Sentiment failed for {signal['ticker']}: {e}")

    # Re-sort after sentiment
    top_buys.sort(key=lambda s: s["strength"], reverse=True)

    summary = format_scan_summary(result)
    await update.message.reply_html(summary)

    for signal in top_buys[:3]:
        try:
            from src.data.fetcher import fetch_stock_history
            df = fetch_stock_history(signal["ticker"], period="6mo")
            await send_signal_with_chart(signal, df, chat_id=str(update.effective_chat.id))
        except Exception as e:
            logger.error(f"Error sending chart for {signal['ticker']}: {e}")


async def cmd_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تحليل سهم محدد."""
    if not context.args:
        await update.message.reply_text(
            "الاستخدام: /stock 2222\n\n"
            "أمثلة:\n"
            "/stock 2222 (أرامكو)\n"
            "/stock 1120 (الراجحي)\n"
            "/stock 7010 (STC)"
        )
        return

    ticker = context.args[0].replace(".SR", "")
    await update.message.reply_text(f"\U0001f4ca جاري تحليل {ticker}...")

    from src.data.fetcher import fetch_stock_history
    from src.analysis.signals import generate_signal

    df = fetch_stock_history(ticker, period="1y")
    if df.empty or len(df) < 200:
        await update.message.reply_text(f"لا توجد بيانات كافية لـ {ticker}. نحتاج 200 يوم تداول على الأقل.")
        return

    stock_info = get_stock_info(ticker) or {"name": ticker, "sector": "غير محدد"}
    signal = generate_signal(ticker, df)

    # Get AI sentiment
    from src.analysis.sentiment import analyze_stock_sentiment
    sentiment = await analyze_stock_sentiment(ticker, stock_info.get("name", ticker))

    if signal:
        if sentiment:
            signal["sentiment"] = sentiment
            signal["strength"] = max(0, min(100, signal["strength"] + sentiment.score))
            from src.analysis.signals import get_signal_grade
            signal["grade"] = get_signal_grade(signal["strength"])
            if sentiment.score != 0:
                signal["reasons"].append(f"تحليل ذكاء اصطناعي: {sentiment.summary}")
        msg = format_signal_message(signal)
        await update.message.reply_html(msg)
    else:
        analyzed = compute_indicators(df)
        indicators = get_latest_indicators(analyzed)
        msg = format_stock_info(ticker, indicators, stock_info)
        if sentiment:
            msg += f"\n\n\U0001f9e0 <b>تحليل الذكاء الاصطناعي:</b>\n  {sentiment.to_arabic()}"
        await update.message.reply_html(msg)

    # إرسال الرسم البياني دائماً
    try:
        analyzed = compute_indicators(df)
        chart_buf = generate_stock_chart(
            analyzed,
            ticker=ticker,
            stock_name=stock_info.get("name", ticker),
            signal_type=signal["signal_type"] if signal else None,
            signal_strength=signal["strength"] if signal else None,
        )
        if chart_buf:
            await update.message.reply_photo(
                photo=chart_buf,
                caption=f"{ticker} - {stock_info.get('name', ticker)}",
            )
    except Exception as e:
        logger.error(f"Error generating chart for {ticker}: {e}")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة المساعدة."""
    help_text = (
        "\U0001f4b9 <b>بوت أسهم - محلل السوق السعودي</b>\n\n"
        "<b>الأوامر:</b>\n"
        "/scan - مسح جميع أسهم تداول\n"
        "/stock 2222 - تحليل سهم محدد (مع رسم بياني)\n"
        "/portfolio - المحفظة الافتراضية (الصفقات المفتوحة)\n"
        "/performance - أداء التداول الافتراضي\n"
        "/backtest 2222 - اختبار سهم على بيانات تاريخية\n"
        "/stocks - قائمة الأسهم الشائعة\n"
        "/help - عرض المساعدة\n\n"
        "<b>درجات الإشارة:</b>\n"
        "\U0001f7e2\U0001f7e2\U0001f7e2 قوية (70+) - ثقة عالية\n"
        "\U0001f7e1\U0001f7e1 متوسطة (55-69) - كن حذراً\n"
        "\U0001f7e0 ضعيفة (40-54) - للمراقبة فقط\n\n"
        "<b>ميزات الأمان:</b>\n"
        "\U0001f6e1 كل إشارة تتضمن وقف خسارة وهدف ووقف متحرك\n"
        "\u2696\ufe0f وقف خسارة 5%، هدف 8%، وقف متحرك عند +3%\n\n"
        "<b>المسح التلقائي:</b>\n"
        "البوت يعمل تلقائياً أحد-خميس خلال ساعات التداول\n"
        "(10:00-15:00 بتوقيت الرياض)\n\n"
        "\u26a0\ufe0f <i>ليست نصيحة مالية. قم بأبحاثك الخاصة دائماً.</i>"
    )
    await update.message.reply_html(help_text)


async def cmd_stocks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قائمة الأسهم الشائعة."""
    await update.message.reply_html(
        "<b>الأسهم الأكثر تداولاً:</b>\n\n"
        "/stock 2222 - أرامكو السعودية\n"
        "/stock 1120 - مصرف الراجحي\n"
        "/stock 2010 - سابك\n"
        "/stock 7010 - الاتصالات STC\n"
        "/stock 2280 - المراعي\n"
        "/stock 2082 - أكوا باور\n"
        "/stock 1180 - البنك الأهلي SNB\n"
        "/stock 1150 - مصرف الإنماء\n"
        "/stock 4190 - جرير\n"
        "/stock 4013 - د. سليمان الحبيب\n"
        "/stock 1211 - معادن\n"
        "/stock 2050 - صافولا\n"
    )


async def cmd_backtest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اختبار الاستراتيجية على بيانات تاريخية."""
    from src.backtest.engine import run_backtest
    from src.backtest.report import format_backtest_report, generate_equity_curve

    # Single stock or full backtest
    if context.args:
        ticker = context.args[0].replace(".SR", "")
        info = get_stock_info(ticker)
        name = info["name"] if info else ticker
        await update.message.reply_text(
            f"\U0001f52c جاري اختبار الاستراتيجية على {ticker} ({name})...\n"
            f"هذا قد يستغرق 1-3 دقائق."
        )
        tickers = [ticker]
    else:
        await update.message.reply_text(
            "\U0001f52c جاري اختبار الاستراتيجية على أكبر 20 سهم...\n"
            "هذا قد يستغرق 3-5 دقائق."
        )
        tickers = None  # defaults to top 20

    try:
        results = run_backtest(tickers=tickers, period="2y")

        # Send report
        report = format_backtest_report(results)
        await update.message.reply_html(report)

        # Send equity curve
        equity_curve = results.get("equity_curve", [])
        chart = generate_equity_curve(equity_curve)
        if chart:
            await update.message.reply_photo(
                photo=chart,
                caption="منحنى رأس المال - الاختبار الرجعي",
            )

    except Exception as e:
        logger.error(f"Backtest failed: {e}", exc_info=True)
        await update.message.reply_text(
            f"\u274c حدث خطأ أثناء الاختبار. حاول مرة أخرى."
        )


async def cmd_portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض المحفظة الافتراضية."""
    from src.trading.paper_trader import format_portfolio_arabic, check_positions

    # Update positions with current prices first
    check_positions()

    msg = format_portfolio_arabic()
    await update.message.reply_html(msg)


async def cmd_performance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض أداء التداول الافتراضي."""
    from src.trading.paper_trader import format_performance_arabic

    msg = format_performance_arabic()
    await update.message.reply_html(msg)


def create_telegram_app() -> Application:
    """إنشاء تطبيق بوت تيليجرام."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("scan", cmd_scan))
    app.add_handler(CommandHandler("stock", cmd_stock))
    app.add_handler(CommandHandler("backtest", cmd_backtest))
    app.add_handler(CommandHandler("portfolio", cmd_portfolio))
    app.add_handler(CommandHandler("performance", cmd_performance))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("start", cmd_help))
    app.add_handler(CommandHandler("stocks", cmd_stocks))

    return app
