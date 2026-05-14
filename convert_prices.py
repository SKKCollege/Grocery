import json

with open("rimi_prices.json", "r", encoding="utf-8") as f:
    rimi_data = json.load(f)

products = {}
for item in rimi_data:
    key = f"{item['name']}_{item['category']}"
    if key not in products:
        products[key] = {
            "name": item["name"],
            "unit": item["unit"],
            "category": item["category"],
            "prices": []
        }
    products[key]["prices"].append({
        "store": "rimi",
        "price": item["price"]
    })

output = list(products.values())

with open("prices.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Done! Converted {len(output)} products to prices.json")
for p in output[:3]:
    print(f"  {p['name']} - €{p['prices'][0]['price']}")
