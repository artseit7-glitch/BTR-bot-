from calculators.concrete import WORK_LABELS as CONCRETE_LABELS
from calculators.wooden import WORK_LABELS as WOODEN_LABELS


def fmt(n: float) -> str:
    return f"{int(round(n)):,}".replace(",", " ")


def format_concrete(area: float, items: dict) -> str:
    lines = [f"📐 Площадь: <b>{area} м²</b>\n", "🧱 <b>Бетонные полы — расчёт работ:</b>\n"]
    total = 0.0
    for key, val in items.items():
        label = CONCRETE_LABELS.get(key, key)
        lines.append(f"• {label}: <b>{fmt(val)} ₸</b>")
        total += val
    lines.append(f"\n💰 <b>Итого: {fmt(total)} ₸</b>")
    lines.append("<i>Цена за работу, без материалов</i>")
    return "\n".join(lines)


def format_wooden(area: float, items: dict) -> str:
    lines = [f"📐 Площадь: <b>{area} м²</b>\n", "🪵 <b>Деревянные полы — расчёт работ:</b>\n"]
    total_min, total_max = 0.0, 0.0
    for key, (mn, mx) in items.items():
        label = WOODEN_LABELS.get(key, key)
        lines.append(f"• {label}: <b>{fmt(mn)} – {fmt(mx)} ₸</b>")
        total_min += mn
        total_max += mx
    lines.append(f"\n💰 <b>Итого: {fmt(total_min)} – {fmt(total_max)} ₸</b>")
    lines.append("<i>Цена за работу, без материалов</i>")
    return "\n".join(lines)


def format_self_leveling(area: float, total: float) -> str:
    lines = [
        f"📐 Площадь: <b>{area} м²</b>\n",
        "💧 <b>Наливные полы — расчёт работ:</b>\n",
        f"• Наливной пол: <b>от {fmt(total)} ₸</b>\n",
        f"💰 <b>Итого: от {fmt(total)} ₸</b>",
        "<i>Цена за работу, без материалов</i>",
    ]
    return "\n".join(lines)
