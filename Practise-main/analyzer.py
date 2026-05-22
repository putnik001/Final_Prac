import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt
import io

import db_handler as db

def stats_for_period(entries):
    if not entries:
        return None
    mood_sum = 0
    work_sum = 0
    sleep_sum = 0
    count = 0
    for e in entries:
        mood_sum += e["mood"]
        work_sum += e["study_hours"]
        sleep_sum += e["sleep_hours"]
        count += 1
    return {
        "records": count,
        "avg_mood": round(mood_sum / count, 2),
        "avg_work": round(work_sum / count, 2),
        "avg_sleep": round(sleep_sum / count, 2),
    }

def get_insights(entries):
    if not entries:
        return "Недостаточно данных для инсайтов."

    
    sorted_entries = sorted(entries, key=lambda e: e["mood"], reverse=True)
    top_days = sorted_entries[:3]
    top_str = ""
    for e in top_days:
        top_str += f"📅 {e['entry_date']} – настроение {e['mood']}/5\n"

    high_sleep = [e for e in entries if e["sleep_hours"] >= 8]
    low_sleep = [e for e in entries if e["sleep_hours"] < 8]
    sleep_analysis = ""
    if high_sleep and low_sleep:
        avg_high = sum(e["mood"] for e in high_sleep) / len(high_sleep)
        avg_low = sum(e["mood"] for e in low_sleep) / len(low_sleep)
        sleep_analysis = (
            f"💤 Сон ≥ 8 ч: среднее настроение {avg_high:.2f}\n"
            f"💤 Сон < 8 ч: среднее настроение {avg_low:.2f}\n"
        )
    else:
        sleep_analysis = "💤 Недостаточно данных для сравнения по сну.\n"

    high_work = [e for e in entries if e["study_hours"] >= 6]
    low_work = [e for e in entries if e["study_hours"] < 6]
    work_analysis = ""
    if high_work and low_work:
        avg_high = sum(e["mood"] for e in high_work) / len(high_work)
        avg_low = sum(e["mood"] for e in low_work) / len(low_work)
        work_analysis = (
            f"📚 Работа/учёба ≥ 6 ч: среднее настроение {avg_high:.2f}\n"
            f"📚 Работа/учёба < 6 ч: среднее настроение {avg_low:.2f}"
        )
    else:
        work_analysis = "📚 Недостаточно данных для сравнения по нагрузке."

    return (
        "🔍 Мои инсайты:\n\n"
        f"✨ Топ-3 лучших дня:\n{top_str}\n"
        f"{sleep_analysis}\n"
        f"{work_analysis}"
    )

def plot_trend(entries, period_name):
    if not entries:
        return None
    entries_sorted = sorted(entries, key=lambda e: e["id"])
    dates = [e["entry_date"] for e in entries_sorted]
    mood = [e["mood"] for e in entries_sorted]
    work = [e["study_hours"] for e in entries_sorted]
    sleep = [e["sleep_hours"] for e in entries_sorted]

   
    x = list(range(1, len(entries_sorted) + 1))

    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    ax1.plot(x, mood, marker="o", color="blue", label="Настроение")
    ax1.set_ylabel("Настроение", color="blue")
    ax1.set_ylim(0, 5.5)

    ax2 = ax1.twinx()
    ax2.plot(x, work, marker="s", color="green", label="Работа/учёба")
    ax2.plot(x, sleep, marker="^", color="red", label="Сон")
    ax2.set_ylabel("Часы")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.title(f"Динамика показателей ({period_name})")
    ax1.set_xticks(x)
    ax1.set_xticklabels(dates, rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)
    return buf


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


def insights(user_id: int) -> str:
    entries = db.get_entries_for_period(user_id, 30)
    return get_insights(entries)


def mood_chart(user_id: int):
    entries = db.get_entries_for_period(user_id, 30)
    return plot_trend(entries, "последние 30 дней")