import os
import random
import pandas as pd
from datetime import datetime, timedelta

def generate_mock_data(output_path, num_transactions=2000, cancellation_rate=0.05):
    """
    Generates a realistic transactional retail dataset containing 5 distinct affinity clusters:
    1. Breakfast Cluster
    2. Cleaning Supplies Cluster
    3. Weekend Party Cluster
    4. Tech Accessories Cluster
    5. Baking Cluster
    Also includes random cancelled orders to test preprocessing modules.
    """
    print(f"Generating {num_transactions} mock transactions...")

    # Define products within specific affinity clusters
    clusters = {
        "Breakfast": [
            ("84029E", "Whole Wheat Bread", 2.50),
            ("22752", "Unsalted Butter", 3.20),
            ("22727", "Strawberry Jam", 2.80),
            ("85123A", "Organic Milk", 1.89),
            ("21754", "Ground Coffee", 5.99),
            ("21755", "Sweet Creamer", 2.49)
        ],
        "Cleaning": [
            ("22383", "All-Purpose Cleaner", 3.49),
            ("20725", "Paper Towels", 1.99),
            ("23084", "Dish Soap Eco", 2.29),
            ("84879", "Laundry Detergent Liquid", 8.99),
            ("22384", "Sponge 4-Pack", 1.49)
        ],
        "Weekend_Party": [
            ("22960", "Tortilla Chips", 2.99),
            ("22961", "Mild Tomato Salsa", 3.49),
            ("22386", "Cheddar Cheese Block", 4.29),
            ("21731", "Classic Soft Drink", 1.25),
            ("22197", "Salted Potato Chips", 1.79)
        ],
        "Tech_Accessories": [
            ("21080", "Smartphone Case Clear", 12.99),
            ("21086", "Tempered Screen Protector", 9.99),
            ("22423", "Wireless Earbuds Blue", 29.99),
            ("22086", "USB-C Braided Cable 2m", 5.49),
            ("22666", "10000mAh Power Bank", 19.99)
        ],
        "Baking": [
            ("21213", "All-Purpose Flour 2kg", 1.89),
            ("21212", "Fine White Sugar 1kg", 1.39),
            ("22064", "Baking Powder 100g", 0.99),
            ("22114", "Semi-Sweet Chocolate Chips", 2.79),
            ("22138", "Fresh Brown Eggs 12-Pack", 3.29)
        ]
    }

    # Flat list of all items for filler random purchases
    all_products = []
    for c_name, items in clusters.items():
        all_products.extend(items)

    # Countries
    countries = ["United Kingdom", "Germany", "France", "Spain", "Netherlands", "Australia"]

    data = []
    base_date = datetime(2026, 1, 1)

    for i in range(1, num_transactions + 1):
        invoice_num = f"{10000 + i}"
        customer_id = str(random.randint(12345, 18999))
        country = random.choices(countries, weights=[0.75, 0.08, 0.06, 0.05, 0.04, 0.02])[0]
        tx_time = base_date + timedelta(days=random.randint(0, 120), hours=random.randint(8, 20), minutes=random.randint(0, 59))
        
        # Decide if this transaction is cancelled later (represented as negative or separate record)
        is_cancelled = random.random() < cancellation_rate

        # Decide which clusters are purchased in this transaction
        selected_clusters = []
        # Normal purchases have a 45% chance of adopting a specific cluster, and a 55% chance of completely random baskets
        r_val = random.random()
        if r_val < 0.20:
            selected_clusters.append("Breakfast")
        elif r_val < 0.35:
            selected_clusters.append("Cleaning")
        elif r_val < 0.50:
            selected_clusters.append("Weekend_Party")
        elif r_val < 0.65:
            selected_clusters.append("Tech_Accessories")
        elif r_val < 0.80:
            selected_clusters.append("Baking")
        
        basket_items = []
        
        # Add clustered items with high affinity
        for c in selected_clusters:
            items_in_cluster = clusters[c]
            # Pick a subset of items in this cluster (2 to 5 items)
            num_cluster_items = random.randint(2, min(5, len(items_in_cluster)))
            picked = random.sample(items_in_cluster, num_cluster_items)
            basket_items.extend(picked)

        # Add some random items to basket to simulate noise (0 to 3 items)
        num_noise_items = random.randint(0, 3)
        if num_noise_items > 0:
            noise_items = random.sample(all_products, num_noise_items)
            basket_items.extend(noise_items)

        # Remove duplicate product codes from the basket in a single invoice
        seen_codes = set()
        unique_basket = []
        for item in basket_items:
            if item[0] not in seen_codes:
                seen_codes.add(item[0])
                unique_basket.append(item)
        
        # Baskets must contain at least 1 item
        if not unique_basket:
            unique_basket = [random.choice(all_products)]

        # Append items to the data list
        for stock_code, desc, price in unique_basket:
            qty = random.choices([1, 2, 3, 4, 5, 10], weights=[0.6, 0.2, 0.1, 0.05, 0.03, 0.02])[0]
            data.append({
                "InvoiceNo": invoice_num,
                "StockCode": stock_code,
                "Description": desc,
                "Quantity": qty,
                "UnitPrice": price,
                "CustomerID": customer_id,
                "Country": country,
                "InvoiceDate": tx_time.strftime("%Y-%m-%d %H:%M")
            })

            # If cancelled, insert a matching return invoice with negative quantity and "C" prefix
            if is_cancelled:
                # Cancelled invoices have same customer and country
                data.append({
                    "InvoiceNo": f"C{invoice_num}",
                    "StockCode": stock_code,
                    "Description": desc,
                    "Quantity": -qty,
                    "UnitPrice": price,
                    "CustomerID": customer_id,
                    "Country": country,
                    "InvoiceDate": (tx_time + timedelta(hours=random.randint(1, 24))).strftime("%Y-%m-%d %H:%M")
                })

    df = pd.DataFrame(data)
    
    # Ensure parent output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Data saved successfully to {output_path} ({len(df)} rows).")
    return df

if __name__ == "__main__":
    # Create default file
    generate_mock_data("data/online_retail_sample.csv")
