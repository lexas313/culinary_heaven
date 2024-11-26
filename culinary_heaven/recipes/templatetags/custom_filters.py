from django import template
from decimal import Decimal, InvalidOperation
from datetime import timedelta

register = template.Library()


@register.filter
def format_decimal(value):
    try:
        decimal_value = Decimal(value)
        # Преобразуем значение в строку, убирая лишние нули
        formatted_value = str(decimal_value).rstrip('0').rstrip('.')
        return formatted_value
    except (ValueError, InvalidOperation):
        return value


@register.filter
def format_time_for_minutes(value):
    if isinstance(value, int):
        delta = timedelta(minutes=value)

        # Извлечение дней, часов и минут
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes = remainder // 60

        # Форматирование на русский язык
        formatted_time = []

        if days > 0:
            formatted_time.append(f"{days} дн.")
        if hours > 0:
            formatted_time.append(f"{hours} ч.")
        if minutes > 0:
            formatted_time.append(f"{minutes} мин.")

        # Объединение в строку
        formatted_time = " ".join(formatted_time)

        return formatted_time

    return value

