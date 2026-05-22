import os
import argparse
import pandas as pd
from src.generate_data import generate_mock_data
from src.data_transformer import load_csv_robust, clean_data, transform_to_basket, get_eda_stats
from src.rules_engine import run_frequent_itemsets, benchmark_algorithms, generate_association_rules
from src.visualizer import generate_network_graphs
from src.business_rules import get_business_recommendations
from src.report_generator import generate_html_proposal

def main():
    parser = argparse.ArgumentParser(description="Market Basket Analysis (MBA) CLI Orchestrator")
    
    parser.add_argument("--run-all", action="store_true", help="Runs the entire pipeline (generate data -> clean -> mine -> visualize -> report)")
    parser.add_argument("--generate", action="store_true", help="Forces generating a new mock transaction dataset")
    parser.add_argument("--num-tx", type=int, default=2000, help="Number of transactions to mock generate (default: 2000)")
    parser.add_argument("--data-path", type=str, default="data/online_retail_sample.csv", help="Path to input transactional CSV (default: data/online_retail_sample.csv)")
    parser.add_argument("--support", type=float, default=0.01, help="Minimum support threshold (default: 0.01)")
    parser.add_argument("--confidence", type=float, default=0.3, help="Minimum confidence threshold (default: 0.3)")
    parser.add_argument("--lift", type=float, default=1.2, help="Minimum lift threshold (default: 1.2)")
    parser.add_argument("--max-len", type=int, default=None, help="Maximum number of items in a rule (default: None/No limit)")
    parser.add_argument("--algorithm", type=str, choices=['apriori', 'fpgrowth', 'both'], default='fpgrowth', help="Mining algorithm choice (default: fpgrowth)")
    
    args = parser.parse_args()
    
    # Check if we should generate data
    if args.generate or not os.path.exists(args.data_path) or args.run_all:
        if not os.path.exists(args.data_path) or args.generate:
            print(f"Dataset not found or forced generate. Generating data in {args.data_path}...")
            generate_mock_data(args.data_path, num_transactions=args.num_tx)
            
    # Load dataset
    print(f"\nLoading raw transaction dataset from {args.data_path}...")
    try:
        raw_df = load_csv_robust(args.data_path)
        print(f"Loaded successfully: {len(raw_df)} transactional records.")
    except Exception as e:
        print(f"Error loading file {args.data_path}: {e}")
        return

    # 1. PREPROCESSING
    print("\n--- [Step 1] Preprocessing & Transforming Data ---")
    cleaned_df = clean_data(raw_df)
    print(f"Data cleaned. Excluded returns. Cleaned count: {len(cleaned_df)} rows.")
    
    print("Pivoting data to basket format and casting columns to boolean (RAM optimized)...")
    basket_df = transform_to_basket(cleaned_df)
    print(f"Basket matrix ready. Shape: {basket_df.shape} (Transactions x Products)")
    
    # 2. EDA STATS
    print("\n--- [EDA Stats] ---")
    eda_stats = get_eda_stats(cleaned_df, basket_df)
    print(f"Total Cleaned Transactions: {eda_stats['total_transactions']:,}")
    print(f"Unique Products Catalog: {eda_stats['unique_products']:,}")
    print(f"Average Basket Size: {eda_stats['avg_basket_size']} items")
    print("Top 5 Selling Items:")
    for item, qty in list(eda_stats['top_selling'].items())[:5]:
        print(f"  - {item}: {qty} units sold")
        
    # 3. BENCHMARK / MINING
    print("\n--- [Step 2] Running Association Rule Mining ---")
    print(f"Using Algorithm: {args.algorithm} (Support Threshold: {args.support})")
    
    if args.algorithm == 'both':
        print("Running side-by-side execution benchmarks...")
        bench_results = benchmark_algorithms(basket_df, min_support=args.support, max_len=args.max_len)
        for alg, data in bench_results.items():
            print(f"  - {alg.upper()}: Time = {data['time']:.4f}s | Itemsets found = {data['count']} | Status = {data['status']}")
        
        # Mine rules using fpgrowth as default
        frequent_itemsets, _ = run_frequent_itemsets(basket_df, min_support=args.support, algorithm='fpgrowth', max_len=args.max_len)
    else:
        frequent_itemsets, elapsed = run_frequent_itemsets(basket_df, min_support=args.support, algorithm=args.algorithm, max_len=args.max_len)
        print(f"Frequent itemsets mined successfully via {args.algorithm.upper()} in {elapsed:.4f} seconds.")
        print(f"Found {len(frequent_itemsets)} frequent itemsets.")

    # 4. RULES GENERATION
    print("\n--- [Step 3] Deriving Association Rules & Metric Analysis ---")
    rules_df = generate_association_rules(
        frequent_itemsets, 
        total_transactions=eda_stats['total_transactions'], 
        min_confidence=args.confidence, 
        min_lift=args.lift, 
        max_len=args.max_len
    )
    
    strong_rules_count = len(rules_df)
    print(f"Filtered rules: {strong_rules_count} strong rules met thresholds (Confidence >= {args.confidence}, Lift >= {args.lift})")
    
    # Save rules
    rules_csv_path = "outputs/association_rules.csv"
    os.makedirs(os.path.dirname(rules_csv_path), exist_ok=True)
    
    if not rules_df.empty:
        rules_df.to_csv(rules_csv_path, index=False)
        print(f"Rules table saved successfully to {rules_csv_path}")
        print("\nTop 5 Discovered Rules by Lift:")
        for idx, row in rules_df.head(5).iterrows():
            print(f"  Rule: {row['antecedents_str']} -> {row['consequents_str']} | Support: {row['support']:.4f} | Confidence: {row['confidence']:.2%} | Lift: {row['lift']:.2f}")
    else:
        print("No association rules found meeting thresholds. Try decreasing support or confidence.")

    # 5. GRAPH VISUALIZATION
    print("\n--- [Step 4] Network Graph Visualization ---")
    static_png = "outputs/network_graph.png"
    interactive_html = "outputs/network_graph.html"
    
    # Generate graphs (using higher thresholds to avoid a hairball, or default filters)
    success = generate_network_graphs(
        rules_df, 
        static_png_path=static_png, 
        interactive_html_path=interactive_html,
        min_confidence=0.6,
        min_lift=1.2
    )
    if success:
        print(f"High-resolution static network saved: {static_png}")
        print(f"Physics-enabled interactive network saved: {interactive_html}")
    else:
        print("Network graphs could not be generated due to empty filtered rules.")

    # 6. BUSINESS REPORT GENERATION
    print("\n--- [Step 5] Business Strategy Proposal & Report ---")
    strategy_report_path = "outputs/strategy_proposal.html"
    
    recs = get_business_recommendations(rules_df, limit=10)
    print(f"Translated {len(recs)} rules into strategic recommendations.")
    
    generate_html_proposal(
        eda_stats=eda_stats,
        rules_df=rules_df,
        recommendations=recs,
        output_path=strategy_report_path
    )
    print(f"Business Proposal compiled: {strategy_report_path}")
    print("\n================ MBA Pipeline Completed Successfully ================")

if __name__ == "__main__":
    main()
