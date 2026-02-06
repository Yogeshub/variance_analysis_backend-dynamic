import math


def apply_rules(row, rules):
    messages = []

    for rule in rules:
        metric = rule.get("metric")
        condition = rule.get("condition")
        message = rule.get("message")

        try:
            value = float(row.get(metric, 0))
            if eval(f"{value} {condition}"):
                messages.append(message)
        except:
            continue

    return " ".join(messages) if messages else None
