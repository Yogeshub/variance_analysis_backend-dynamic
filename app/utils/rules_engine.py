import math


def generate_rule_based_explanation(row, rules):
    explanations = []
    for rule in rules:
        metric = rule.get("metric")
        condition = rule.get("condition")
        message = rule.get("message")
        try:
            value = row.get(metric, 0)
            if value is None or (isinstance(value, float) and math.isnan(value)):
                value = 0
            value = float(value)
            expr = f"{value} {condition}"
            if eval(expr):
                explanations.append(message)
        except Exception as e:
            explanations.append(f"(⚠️ Error evaluating rule for {metric}: {e})")

    return " ".join(explanations) if explanations else "No major variance detected."
