"""
Arabic-formatted backtest reports for Telegram.
"""

import io
import logging

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

logger = logging.getLogger(__name__)


def format_backtest_report(results: dict) -> str:
    """Format backtest results as Arabic Telegram message."""
    metrics = results.get("metrics", {})
    config = results.get("config", {})

    if not metrics or metrics.get("total_trades", 0) == 0:
        return (
            "\U0001f4ca <b>نتائج الاختبار الرجعي</b>\n\n"
            "\u26a0\ufe0f لم يتم العثور على صفقات في هذه الفترة.\n"
            "جرب فترة أطول أو أسهم مختلفة."
        )

    total = metrics["total_trades"]
    wins = metrics["wins"]
    losses = metrics["losses"]
    win_rate = metrics["win_rate"]
    total_pnl = metrics["total_pnl"]
    total_return = metrics["total_return_pct"]
    initial = metrics.get("initial_capital", 100000)
    final = metrics.get("final_capital", initial + total_pnl)

    # Overall verdict
    if total_return > 10:
        verdict = "\U0001f7e2 الاستراتيجية مربحة"
        verdict_icon = "\U0001f3c6"
    elif total_return > 0:
        verdict = "\U0001f7e1 الاستراتيجية إيجابية بشكل طفيف"
        verdict_icon = "\U0001f44d"
    else:
        verdict = "\U0001f534 الاستراتيجية تحتاج تحسين"
        verdict_icon = "\u26a0\ufe0f"

    # Format exit reasons
    exit_reasons = metrics.get("exit_reasons", {})
    tp_count = exit_reasons.get("take_profit", 0)
    sl_count = exit_reasons.get("stop_loss", 0)
    timeout_count = exit_reasons.get("timeout", 0)

    msg = (
        f"\U0001f4ca <b>نتائج الاختبار الرجعي</b>\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
        f"{verdict_icon} <b>{verdict}</b>\n\n"
        f"\U0001f4b0 <b>الأداء المالي:</b>\n"
        f"  رأس المال: {initial:,.0f} ريال\n"
        f"  الرصيد النهائي: <b>{final:,.0f} ريال</b>\n"
        f"  الربح/الخسارة: <b>{total_pnl:+,.0f} ريال</b>\n"
        f"  العائد: <b>{total_return:+.1f}%</b>\n\n"
        f"\U0001f4c8 <b>إحصائيات الصفقات:</b>\n"
        f"  إجمالي الصفقات: {total}\n"
        f"  صفقات رابحة: {wins} \U0001f7e2\n"
        f"  صفقات خاسرة: {losses} \U0001f534\n"
        f"  نسبة الفوز: <b>{win_rate:.1f}%</b>\n\n"
        f"\U0001f4b5 <b>متوسط الصفقة:</b>\n"
        f"  متوسط الربح: {metrics.get('avg_win', 0):+,.0f} ريال ({metrics.get('avg_win_pct', 0):+.1f}%)\n"
        f"  متوسط الخسارة: {metrics.get('avg_loss', 0):+,.0f} ريال ({metrics.get('avg_loss_pct', 0):+.1f}%)\n"
        f"  معامل الربح: {metrics.get('profit_factor', 0):.2f}\n"
        f"  متوسط مدة الصفقة: {metrics.get('avg_holding_days', 0):.0f} يوم\n\n"
        f"\U0001f6e1 <b>إدارة المخاطر:</b>\n"
        f"  أقصى تراجع: {metrics.get('max_drawdown_pct', 0):.1f}%\n"
        f"  نسبة شارب: {metrics.get('sharpe_ratio', 0):.2f}\n\n"
        f"\U0001f3af <b>أسباب الخروج:</b>\n"
        f"  وصل الهدف: {tp_count} \U0001f7e2\n"
        f"  وقف الخسارة: {sl_count} \U0001f534\n"
        f"  انتهاء المدة: {timeout_count} \u23f0\n\n"
    )

    # Grade performance
    grade_stats = metrics.get("grade_stats", {})
    if grade_stats:
        msg += "\U0001f4ca <b>الأداء حسب درجة الإشارة:</b>\n"
        for grade, stats in grade_stats.items():
            grade_ar = {"STRONG": "قوية", "MODERATE": "متوسطة", "WEAK": "ضعيفة"}.get(grade, grade)
            msg += f"  {grade_ar}: {stats['count']} صفقة، فوز {stats['win_rate']:.0f}%\n"
        msg += "\n"

    # Best/worst
    msg += (
        f"\U0001f947 أفضل صفقة: {metrics.get('best_trade_ticker', '')}.SR "
        f"({metrics.get('best_trade_pnl', 0):+,.0f} ريال)\n"
        f"\U0001f4a5 أسوأ صفقة: {metrics.get('worst_trade_ticker', '')}.SR "
        f"({metrics.get('worst_trade_pnl', 0):+,.0f} ريال)\n\n"
    )

    # Config used
    msg += (
        f"<i>الإعدادات: وقف خسارة {config.get('stop_loss_pct', 3)}%، "
        f"هدف {config.get('take_profit_pct', 6)}%، "
        f"حد الإشارة {config.get('signal_threshold', 40)}/100</i>\n"
        f"\u26a0\ufe0f <i>الأداء السابق لا يضمن النتائج المستقبلية.</i>"
    )

    return msg


def generate_equity_curve(equity_curve: list[dict]) -> io.BytesIO | None:
    """Generate equity curve chart."""
    if not equity_curve or len(equity_curve) < 2:
        return None

    try:
        dates = [datetime.strptime(p["date"], "%Y-%m-%d") for p in equity_curve]
        values = [p["equity"] for p in equity_curve]

        # Sample if too many points (keep chart readable)
        if len(dates) > 500:
            step = len(dates) // 500
            dates = dates[::step]
            values = values[::step]

        fig, ax = plt.subplots(figsize=(12, 6))
        fig.patch.set_facecolor("#1a1a2e")
        ax.set_facecolor("#16213e")

        # Color: green if profitable, red if losing
        initial = values[0]
        color = "#00c853" if values[-1] >= initial else "#ff1744"

        ax.plot(dates, values, color=color, linewidth=2)
        ax.fill_between(dates, values, initial, alpha=0.15, color=color)

        # Initial capital line
        ax.axhline(y=initial, color="#ffd700", linestyle="--", alpha=0.5, linewidth=1)

        # Formatting
        ax.set_title("منحنى رأس المال", fontsize=16, color="white", pad=15)
        ax.set_ylabel("ريال سعودي", fontsize=12, color="white")
        ax.tick_params(colors="white")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        fig.autofmt_xdate()

        ax.grid(True, alpha=0.2, color="#0f3460")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#0f3460")
        ax.spines["bottom"].set_color("#0f3460")

        # Add final value annotation
        final_val = values[-1]
        pnl = final_val - initial
        pnl_pct = (pnl / initial) * 100
        ax.annotate(
            f"{final_val:,.0f} SAR ({pnl_pct:+.1f}%)",
            xy=(dates[-1], final_val),
            fontsize=11, color=color, fontweight="bold",
            ha="right",
        )

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        buf.seek(0)
        plt.close(fig)

        return buf

    except Exception as e:
        logger.error(f"Error generating equity curve: {e}")
        return None
