def final_deposit_amount(*interest, amount=1000):
    result = amount
    for i in interest:
        result = result * (100 + i) / 100
    return round(result, 2)
