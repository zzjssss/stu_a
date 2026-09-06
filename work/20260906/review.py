sales = [
    {"name": "A", "amount": 320},
    {"name": "B", "amount": 150},
    {"name": "C", "amount": 400},
    {"name": "D", "amount": 210},
    {"name": "E", "amount": 99},
]

print(max(sales , key = lambda s:s.get("amount")))
print(sorted(sales,key = lambda s:s.get("amount"),reverse=True)[:3:])