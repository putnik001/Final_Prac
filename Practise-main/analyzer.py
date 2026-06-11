import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io

import db_handler as db




def stats_for_period(entries):
    if not entries:
        return None
    count = len(entries)
    return {
        "records":   count,
        "avg_mood":  round(sum(e["mood"]         for e in entries) / count, 2),
        "avg_work":  round(sum(e["study_hours"]  for e in entries) / count, 2),
        "avg_sleep": round(sum(e["sleep_hours"]  for e in entries) / count, 2),
    }


def weekly_summary(user_id: int) -> str:
    entries = db.get_entries_for_period(user_id, 7)
    stats = stats_for_period(entries)
    if not stats:
        return "⚠️ Недостаточно данных за неделю."
    return (
        f"📅 <b>Статистика за неделю</b>\n\n"
        f"📝 Записей: {stats['records']}\n"
        f"🌤 Среднее настроение: {stats['avg_mood']}/5\n"
        f"📚 Средняя работа/учёба: {stats['avg_work']} ч\n"
        f"😴 Средний сон: {stats['avg_sleep']} ч"
    )


def monthly_summary(user_id: int) -> str:
    entries = db.get_entries_for_period(user_id, 30)
    stats = stats_for_period(entries)
    if not stats:
        return "⚠️ Недостаточно данных за месяц."
    return (
        f"📅 <b>Статистика за месяц</b>\n\n"
        f"📝 Записей: {stats['records']}\n"
        f"🌤 Среднее настроение: {stats['avg_mood']}/5\n"
        f"📚 Средняя работа/учёба: {stats['avg_work']} ч\n"
        f"😴 Средний сон: {stats['avg_sleep']} ч"
    )




def _compare_by(entries, field, threshold, label, emoji):
    high = [e for e in entries if e[field] >= threshold]
    low  = [e for e in entries if e[field] <  threshold]
    if not high or not low:
        return f"{emoji} Недостаточно данных для сравнения по {label}.\n"
    avg_high = sum(e["mood"] for e in high) / len(high)
    avg_low  = sum(e["mood"] for e in low)  / len(low)
    return (
        f"{emoji} {label} ≥ {threshold}: среднее настроение {avg_high:.2f}\n"
        f"{emoji} {label} < {threshold}: среднее настроение {avg_low:.2f}\n"
    )


def get_insights(entries):
    if not entries:
        return "Недостаточно данных для инсайтов."

    top_days = sorted(entries, key=lambda e: e["mood"], reverse=True)[:3]
    top_str = "".join(f"📅 {e['entry_date']} – настроение {e['mood']}/5\n" for e in top_days)

    sleep_analysis = _compare_by(entries, "sleep_hours",  8, "Сон",          "💤")
    work_analysis  = _compare_by(entries, "study_hours",  6, "Работа/учёба", "📚")

    return (
        "🔍 Мои инсайты:\n\n"
        f"✨ Топ-3 лучших дня:\n{top_str}\n"
        f"{sleep_analysis}\n"
        f"{work_analysis}"
    )


def insights(user_id: int) -> str:
    return get_insights(db.get_entries_for_period(user_id, 30))




def plot_trend(entries, period_name):
    if not entries:
        return None

    entries = sorted(entries, key=lambda e: e["id"])
    x      = list(range(1, len(entries) + 1))
    dates  = [e["entry_date"]   for e in entries]
    mood   = [e["mood"]         for e in entries]
    work   = [e["study_hours"]  for e in entries]
    sleep  = [e["sleep_hours"]  for e in entries]

    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    ax1.plot(x, mood, marker="o", color="blue",  label="Настроение")
    ax1.set_ylabel("Настроение", color="blue")
    ax1.set_ylim(0, 5.5)
    ax1.set_xticks(x)
    ax1.set_xticklabels(dates, rotation=45)

    ax2 = ax1.twinx()
    ax2.plot(x, work,  marker="s", color="green", label="Работа/учёба")
    ax2.plot(x, sleep, marker="^", color="red",   label="Сон")
    ax2.set_ylabel("Часы")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    plt.title(f"Динамика показателей ({period_name})")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)
    return buf


def mood_chart(user_id: int):
    return plot_trend(db.get_entries_for_period(user_id, 30), "последние 30 дней")
