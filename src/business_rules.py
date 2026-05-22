import pandas as pd

def translate_rule_to_strategy(row):
    """
    Translates a single association rule row into a structured business strategy.
    Matches products and rules to determine the type of retail recommendation:
    - Bundle Offer (Discounts)
    - Shelf-Placement (Store Layout)
    - Cross-Selling Widget (Digital UI)
    - Checkout Promotion (Impulse Buy)
    """
    antecedent = row['antecedents_str']
    consequent = row['consequents_str']
    lift = row['lift']
    confidence = row['confidence']
    
    # Identify item characteristics to tailor recommendations
    a_lower = antecedent.lower()
    c_lower = consequent.lower()
    
    strategy_type = "Cross-Selling Promotion"
    recommendation = ""
    rationale = f"A strong association exists between '{antecedent}' and '{consequent}' (Lift = {lift:.2f}, Confidence = {confidence*100:.1f}%). Customers buying '{antecedent}' have a extremely high propensity to purchase '{consequent}'."

    # 1. Breakfast affinities
    if any(item in a_lower for item in ['bread', 'butter', 'jam', 'milk', 'coffee', 'creamer']) and \
       any(item in c_lower for item in ['bread', 'butter', 'jam', 'milk', 'coffee', 'creamer']):
        strategy_type = "Store Layout / Shelf-Placement"
        recommendation = f"Place '{consequent}' directly adjacent to '{antecedent}' in the dairy or bakery aisle. Alternatively, create a 'Breakfast Breakfast Combo' sign on shelves."
        
    # 2. Cleaning affinities
    elif any(item in a_lower for item in ['cleaner', 'towels', 'soap', 'detergent', 'sponge']) and \
         any(item in c_lower for item in ['cleaner', 'towels', 'soap', 'detergent', 'sponge']):
        strategy_type = "Promotional Bundling"
        recommendation = f"Create a 'Home Clean Quick Bundle' featuring '{antecedent}' and '{consequent}' at a packaged 10% discount. Display them together in end-cap promotions."

    # 3. Party food affinities
    elif any(item in a_lower for item in ['chips', 'salsa', 'cheese', 'drink']) and \
         any(item in c_lower for item in ['chips', 'salsa', 'cheese', 'drink']):
        strategy_type = "Weekend Bundle Promotion"
        recommendation = f"Introduce a 'Weekend Party Snack Bundle' grouping '{antecedent}' and '{consequent}' on Friday afternoons near checkout. Offer a 'Buy A, Get B at 30% Off' coupon."

    # 4. Tech accessories affinities
    elif any(item in a_lower for item in ['case', 'protector', 'earbuds', 'cable', 'power bank']) and \
         any(item in c_lower for item in ['case', 'protector', 'earbuds', 'cable', 'power bank']):
        strategy_type = "Digital Recommendation Engine"
        recommendation = f"Configure the online store recommendation widget to trigger an upsell pop-up: 'Customers who bought {antecedent} also added {consequent} to their cart!' Offer one-click bundle adding."

    # 5. Baking affinities
    elif any(item in a_lower for item in ['flour', 'sugar', 'baking', 'chocolate', 'eggs']) and \
         any(item in c_lower for item in ['flour', 'sugar', 'baking', 'chocolate', 'eggs']):
        strategy_type = "Co-Marketing Display"
        recommendation = f"Design a joint holiday baking island. When '{antecedent}' is on promotion, place signboards reminding customers to grab '{consequent}' for their recipe."
        
    # Default fallbacks
    else:
        if confidence > 0.5:
            strategy_type = "Checkout Impulse Offer"
            recommendation = f"Position '{consequent}' near checkout displays. Target shoppers who have added '{antecedent}' to their order with point-of-sale printed discount vouchers."
        else:
            strategy_type = "Aisle Cross-Selling"
            recommendation = f"Cross-merchandise '{consequent}' in the aisle of '{antecedent}'. Place shelf-talkers highlighting the complementary nature of these products."

    return {
        "Rule": f"{antecedent} → {consequent}",
        "Strategy Type": strategy_type,
        "Recommendation": recommendation,
        "Rationale": rationale,
        "Confidence (%)": round(confidence * 100, 1),
        "Lift": round(lift, 2)
    }

def get_business_recommendations(rules_df, limit=10):
    """
    Processes the top association rules dataframe and converts them into
    a list of actionable business strategy dicts.
    """
    if rules_df.empty:
        return []
        
    recommendations = []
    # Take the top rules by lift
    top_rules = rules_df.head(limit)
    
    for _, row in top_rules.iterrows():
        rec = translate_rule_to_strategy(row)
        recommendations.append(rec)
        
    return recommendations
