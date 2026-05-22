import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

# Import and dynamically reload backend modules to prevent Streamlit from using stale in-memory modules
import importlib
import src.generate_data
import src.data_transformer
import src.rules_engine
import src.visualizer
import src.business_rules
import src.report_generator

importlib.reload(src.generate_data)
importlib.reload(src.data_transformer)
importlib.reload(src.rules_engine)
importlib.reload(src.visualizer)
importlib.reload(src.business_rules)
importlib.reload(src.report_generator)

from src.generate_data import generate_mock_data
from src.data_transformer import clean_data, transform_to_basket, get_eda_stats, load_csv_robust
from src.rules_engine import run_frequent_itemsets, benchmark_algorithms, generate_association_rules
from src.visualizer import generate_network_graphs
from src.business_rules import get_business_recommendations
from src.report_generator import generate_html_proposal

# --- Page Setup ---
st.set_page_config(
    page_title="Retail Market Basket Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- Default File Path ---
DEFAULT_DATA_PATH = "data/online_retail_sample.csv"
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Generate mock data if default path is missing
if not os.path.exists(DEFAULT_DATA_PATH):
    st.info("Default transactional dataset not found. Generating a realistic dataset...")
    generate_mock_data(DEFAULT_DATA_PATH)

# Initialize Session State variables to keep data across tab switches
if 'raw_data' not in st.session_state:
    st.session_state.raw_data = load_csv_robust(DEFAULT_DATA_PATH)
if 'cleaned_data' not in st.session_state:
    st.session_state.cleaned_data = None
if 'basket' not in st.session_state:
    st.session_state.basket = None
if 'eda_stats' not in st.session_state:
    st.session_state.eda_stats = None
if 'rules' not in st.session_state:
    st.session_state.rules = None
if 'benchmarks' not in st.session_state:
    st.session_state.benchmarks = None

# --- Page Title ---
st.title("📊 Retail Market Basket Analytics Suite")
st.markdown("##### Uncover hidden consumer buying patterns to drive Average Order Value (AOV), shelf layout, and bundles.")
st.write("---")

# --- Sidebar Controls ---
st.sidebar.header("🛠️ Dashboard Controls")

# File Upload Widget
uploaded_file = st.sidebar.file_uploader("Upload Transaction Dataset (CSV)", type=["csv"], help="Upload transactional logs. Must contain columns: InvoiceNo, Description, Quantity, UnitPrice")

# Hyperparameter Sliders
st.sidebar.subheader("🎛️ MBA Threshold Parameters")
min_support = st.sidebar.slider(
    "Minimum Support", 
    min_value=0.005, 
    max_value=0.100, 
    value=0.010, 
    step=0.005, 
    help="How popular the item combination must be. E.g., 0.01 means bought in 1% of transactions."
)
min_confidence = st.sidebar.slider(
    "Minimum Confidence", 
    min_value=0.10, 
    max_value=1.00, 
    value=0.30, 
    step=0.05, 
    help="Likelihood of buying Product B given Product A has been added to basket. E.g., 0.3 means 30% chance."
)
min_lift = st.sidebar.slider(
    "Minimum Lift", 
    min_value=1.0, 
    max_value=5.0, 
    value=1.2, 
    step=0.1, 
    help="Strength of association. Lift > 1.0 means products are bought together more often than expected by chance."
)
max_len = st.sidebar.slider(
    "Max Rule Length", 
    min_value=2, 
    max_value=5, 
    value=3, 
    help="Maximum items combined in a rule (antecedents + consequents)."
)

# Button to Trigger Pipeline
run_button = st.sidebar.button("⚡ Run Market Basket Analysis", type="primary", use_container_width=True)

# Helper function to execute the full pipeline
def execute_pipeline(df):
    with st.spinner("Step 1/5: Cleaning data and removing cancellations..."):
        cleaned = clean_data(df)
        basket = transform_to_basket(cleaned)
        eda = get_eda_stats(cleaned, basket)
        
    with st.spinner("Step 2/5: Mining frequent itemsets & speed benchmarking..."):
        # We benchmark on the fly
        bench = benchmark_algorithms(basket, min_support=min_support, max_len=max_len)
        # Generate itemsets using fpgrowth
        itemsets, _ = run_frequent_itemsets(basket, min_support=min_support, algorithm='fpgrowth', max_len=max_len)
        
    with st.spinner("Step 3/5: Deriving association rules..."):
        rules = generate_association_rules(
            itemsets, 
            total_transactions=eda['total_transactions'],
            min_confidence=min_confidence,
            min_lift=min_lift,
            max_len=max_len
        )
        
    with st.spinner("Step 4/5: Building static and interactive product cluster graphs..."):
        static_png = os.path.join(OUTPUT_DIR, "network_graph.png")
        interactive_html = os.path.join(OUTPUT_DIR, "network_graph.html")
        generate_network_graphs(
            rules, 
            static_png_path=static_png, 
            interactive_html_path=interactive_html,
            min_confidence=0.6, # standard filter for hairball reduction
            min_lift=1.2
        )
        
    with st.spinner("Step 5/5: Compiling business strategy proposal..."):
        recs = get_business_recommendations(rules, limit=10)
        report_path = os.path.join(OUTPUT_DIR, "strategy_proposal.html")
        generate_html_proposal(eda, rules, recs, report_path)
        
    return cleaned, basket, eda, rules, bench

# Check if we should initialize or re-run
is_old_bench = False
if 'benchmarks' in st.session_state and st.session_state.benchmarks is not None:
    # Force a re-run if it lacks sample metadata, or has the old legacy skipped message
    is_old_bench = ('is_sampled' not in st.session_state.benchmarks) or \
                   ('apriori' in st.session_state.benchmarks and 
                    'Dataset too large' in str(st.session_state.benchmarks['apriori'].get('status', '')))

# Track file upload changes to force a reload of the pipeline when a new file is uploaded
if 'last_uploaded_file' not in st.session_state:
    st.session_state.last_uploaded_file = None

uploaded_file_name = uploaded_file.name if uploaded_file is not None else None
is_new_file = uploaded_file_name != st.session_state.last_uploaded_file
if is_new_file:
    st.session_state.last_uploaded_file = uploaded_file_name

if run_button or st.session_state.cleaned_data is None or is_old_bench or is_new_file:
    # Set active data
    if uploaded_file is not None:
        try:
            df_to_use = load_csv_robust(uploaded_file)
            st.session_state.raw_data = df_to_use
            st.success("Uploaded dataset loaded successfully!")
        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")
            df_to_use = st.session_state.raw_data
    else:
        df_to_use = st.session_state.raw_data

    # Run analysis
    cleaned_df, basket_df, eda, rules, bench = execute_pipeline(df_to_use)
    
    # Store in session state
    st.session_state.cleaned_data = cleaned_df
    st.session_state.basket = basket_df
    st.session_state.eda_stats = eda
    st.session_state.rules = rules
    st.session_state.benchmarks = bench

# Load variables from session state
cleaned_df = st.session_state.cleaned_data
basket_df = st.session_state.basket
eda = st.session_state.eda_stats
rules = st.session_state.rules
bench = st.session_state.benchmarks

# --- TOP-LEVEL KPI ROW ---
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

with kpi_col1:
    st.metric(
        label="Total Transactions", 
        value=f"{eda['total_transactions']:,}",
        help="Total unique orders analyzed (after cleaning cancelled transactions)."
    )
with kpi_col2:
    st.metric(
        label="Unique Products", 
        value=f"{eda['unique_products']:,}",
        help="Total number of distinct inventory products detected in orders."
    )
with kpi_col3:
    st.metric(
        label="Avg Basket Size", 
        value=f"{eda['avg_basket_size']}",
        help="Average number of products purchased per transaction."
    )
with kpi_col4:
    st.metric(
        label="Strong Rules Found", 
        value=f"{len(rules)}",
        help="Number of association rules satisfying the Support, Confidence, and Lift thresholds."
    )
with kpi_col5:
    highest_lift = float(rules['lift'].max()) if not rules.empty else 0.0
    st.metric(
        label="Highest Lift", 
        value=f"{highest_lift:.2f}",
        help="Maximum lift score computed. Indicates the strongest relationship found."
    )

st.write("---")

# --- MAIN DASHBOARD TABS ---
tab_eda, tab_rules, tab_network, tab_strategy = st.tabs([
    "📊 Data Exploration (EDA)",
    "⚡ MBA Rules & Performance",
    "🕸️ Product Cluster Network",
    "📝 Business Strategy Proposal"
])

# ==========================================
# TAB 1: DATA EXPLORATION (EDA)
# ==========================================
with tab_eda:
    st.header("📊 Exploratory Data Analysis (EDA)")
    st.write("Understand your sales trends and item distributions prior to running association mining.")
    
    col_chart, col_details = st.columns([2, 1])
    
    with col_chart:
        # Chart 1: Top Selling Products
        st.subheader("🏆 Top 10 Best-Selling Products")
        top_support_data = pd.DataFrame([
            {"Product": item, "Support %": round(val * 100, 2)} 
            for item, val in eda['top_support'].items()
        ])
        
        fig_bar = px.bar(
            top_support_data, 
            x="Support %", 
            y="Product", 
            orientation="h",
            color="Support %",
            color_continuous_scale="Viridis",
            labels={"Support %": "Invoice Share (%)"},
            category_orders={"Product": top_support_data["Product"].tolist()}
        )
        fig_bar.update_layout(height=450, margin=dict(l=20, r=20, t=10, b=10))
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_details:
        st.subheader("📦 Order Distribution Statistics")
        # Basket size calculations
        basket_sizes = basket_df.sum(axis=1)
        size_counts = basket_sizes.value_counts().sort_index().reset_index()
        size_counts.columns = ["Basket Size", "Transaction Count"]
        
        # Display small stats table
        st.dataframe(
            size_counts, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "Basket Size": st.column_config.NumberColumn("Items in Order", format="%d"),
                "Transaction Count": st.column_config.NumberColumn("Orders", format="%d")
            }
        )
        
        st.info(
            f"**Data Clean Logs:**\n"
            f"- Raw records ingested: **{len(st.session_state.raw_data):,}**\n"
            f"- Total transactions remaining: **{eda['total_transactions']:,}**\n"
            f"- Removed returns/cancellation rows.\n"
            f"- Max items in single transaction: **{eda['max_basket_size']}**"
        )

# ==========================================
# TAB 2: MBA RULES & PERFORMANCE
# ==========================================
with tab_rules:
    st.header("⚡ Association Rule Mining & Metrics")
    
    # 1. Performance benchmarks
    st.subheader("⏱️ Apriori vs FP-Growth Execution Speed Comparison")
    
    is_sampled = bench.get('is_sampled', False)
    
    if is_sampled:
        # Side-by-side benchmark was run on a sample
        benchmark_data = pd.DataFrame([
            {
                "Algorithm": "Apriori (Sample)", 
                "Status": bench['apriori']['status'],
                "Execution Time (s)": bench['apriori']['time'], 
                "Frequent Itemsets": "N/A (Sample)"
            },
            {
                "Algorithm": "FP-Growth (Sample)", 
                "Status": bench.get('fpgrowth_bench', {}).get('status', 'Success'),
                "Execution Time (s)": bench.get('fpgrowth_bench', {}).get('time', 0.0), 
                "Frequent Itemsets": "N/A (Sample)"
            },
            {
                "Algorithm": "FP-Growth (Full Dataset)",
                "Status": bench['fpgrowth']['status'],
                "Execution Time (s)": bench['fpgrowth']['time'],
                "Frequent Itemsets": bench['fpgrowth']['count']
            }
        ])
    else:
        # Full run
        benchmark_data = pd.DataFrame([
            {
                "Algorithm": "Apriori", 
                "Status": bench['apriori']['status'],
                "Execution Time (s)": bench['apriori']['time'] if bench['apriori']['status'] == 'Success' else None, 
                "Frequent Itemsets": bench['apriori']['count']
            },
            {
                "Algorithm": "FP-Growth", 
                "Status": bench['fpgrowth']['status'],
                "Execution Time (s)": bench['fpgrowth']['time'], 
                "Frequent Itemsets": bench['fpgrowth']['count']
            }
        ])
    
    bench_col1, bench_col2 = st.columns([1, 2])
    with bench_col1:
        st.write("Execution speed benchmark results:")
        st.dataframe(
            benchmark_data, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "Execution Time (s)": st.column_config.NumberColumn("Time (s)", format="%.4fs")
            }
        )
        st.markdown(
            "💡 **FP-Growth** uses a compressed FP-Tree structure in RAM, making it **exponentially faster** than the classic "
            "Apriori algorithm, which generates candidates iteratively. This makes FP-Growth crucial for big catalogs!"
        )
        if is_sampled:
            st.info("ℹ️ **Full Apriori Safe-Bypass:** Running Apriori on the full 20,000+ transactions would crash or hang. To show you the comparison, the dashboard safely benchmarked both algorithms on a small, dense representative slice (1,500 transactions, 40 items) of your data.")
        elif bench['apriori']['status'] != 'Success':
            st.warning(f"⚠️ **Note on Apriori:** {bench['apriori']['status']}")
        
    with bench_col2:
        if is_sampled or bench['apriori']['status'] == 'Success':
            chart_df = benchmark_data[benchmark_data['Algorithm'].str.contains('Sample')] if is_sampled else benchmark_data
            fig_speed = px.bar(
                chart_df,
                x="Algorithm",
                y="Execution Time (s)",
                color="Algorithm",
                color_discrete_map={
                    "Apriori": "#ef4444", "FP-Growth": "#3b82f6",
                    "Apriori (Sample)": "#ef4444", "FP-Growth (Sample)": "#3b82f6"
                },
                labels={"Execution Time (s)": "Seconds (Lower is Better)"}
            )
            fig_speed.update_layout(height=240, showlegend=False, margin=dict(l=20, r=20, t=10, b=10))
            st.plotly_chart(fig_speed, use_container_width=True)
        else:
            st.info("📊 **Plotly Chart Skipped:** Since Apriori was skipped to prevent crash/hang, execution speed comparison cannot be plotted. FP-Growth processed the entire dataset successfully.")
        
    st.write("---")
    
    # 2. Support vs Confidence Scatter Plot
    st.subheader("📈 Rule Quality: Support vs Confidence Scatter")
    
    if not rules.empty:
        fig_scatter = px.scatter(
            rules,
            x="support",
            y="confidence",
            color="lift",
            size="lift",
            color_continuous_scale="Plasma",
            hover_data=["antecedents_str", "consequents_str"],
            labels={"support": "Support (Popularity)", "confidence": "Confidence (Strength)", "lift": "Lift Ratio"}
        )
        fig_scatter.update_layout(height=400, margin=dict(l=20, r=20, t=10, b=10))
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.warning("No strong rules available to draw scatter plot.")
        
    st.write("---")
    
    # 3. Association Rules DataFrame
    st.subheader("📋 Mined Association Rules Table")
    
    if not rules.empty:
        # Search input to filter rules in table
        search_query = st.text_input("🔍 Search Rules (e.g. Bread, Case, Soap)", "")
        
        filtered_rules = rules.copy()
        if search_query:
            filtered_rules = filtered_rules[
                filtered_rules['antecedents_str'].str.contains(search_query, case=False) |
                filtered_rules['consequents_str'].str.contains(search_query, case=False)
            ]
            
        st.write(f"Showing **{len(filtered_rules)}** rules.")
        st.dataframe(
            filtered_rules[[
                'antecedents_str', 'consequents_str', 'support', 'confidence', 'lift', 'rule_len'
            ]], 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "antecedents_str": st.column_config.TextColumn("Antecedent (If bought...)"),
                "consequents_str": st.column_config.TextColumn("Consequent (Then also...)"),
                "support": st.column_config.NumberColumn("Support", format="%.4f"),
                "confidence": st.column_config.NumberColumn("Confidence", format="%.2%"),
                "lift": st.column_config.NumberColumn("Lift", format="%.2f"),
                "rule_len": st.column_config.NumberColumn("Rule Size", format="%d")
            }
        )
        
        # Download rules button
        rules_csv = rules.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Association Rules CSV",
            data=rules_csv,
            file_name="association_rules.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.error("No rules met your threshold metrics. Relax Minimum Support/Confidence in the sidebar to generate rules.")

# ==========================================
# TAB 3: PRODUCT CLUSTER NETWORK
# ==========================================
with tab_network:
    st.header("🕸️ Physics-Enabled Product Clusters Network Graph")
    st.write("Drag nodes to inspect items, scroll to zoom, hover on nodes or edges to read probability statistics.")
    
    html_graph_path = os.path.join(OUTPUT_DIR, "network_graph.html")
    
    if os.path.exists(html_graph_path):
        try:
            with open(html_graph_path, 'r', encoding='utf-8') as f:
                html_data = f.read()
                
            # Render interactive PyVis graph inside Streamlit component
            components.html(html_data, height=700, scrolling=True)
            
            st.info(
                "💡 **How to interpret:**\n"
                "- **Node Size:** Represents product support (popularity).\n"
                "- **Edge Thickness:** Represents association Lift (relationship strength).\n"
                "- **Physics:** Nodes auto-arrange into dynamic affinity clusters (e.g. Breakfast, Cleaning, Party)!"
            )
        except Exception as e:
            st.error(f"Error rendering interactive network: {e}")
    else:
        st.warning("Network graph HTML not found. Verify rules are correctly generated.")

# ==========================================
# TAB 4: BUSINESS STRATEGY PROPOSAL
# ==========================================
with tab_strategy:
    st.header("📝 Translating Math Into English: Strategic Business Proposal")
    st.write("Concrete retail recommendations built algorithmically from high-lift product affinities.")
    
    recs = get_business_recommendations(rules, limit=10)
    
    if recs:
        # Load compiled HTML proposal for download button
        proposal_path = os.path.join(OUTPUT_DIR, "strategy_proposal.html")
        if os.path.exists(proposal_path):
            with open(proposal_path, 'r', encoding='utf-8') as f:
                html_report = f.read()
                
            st.download_button(
                label="📥 Download Standalone Print-Ready Strategy Proposal HTML",
                data=html_report,
                file_name="strategy_proposal.html",
                mime="text/html",
                use_container_width=True
            )
        
        st.write("---")
        
        # Display recommendations in nice cards
        for idx, rec in enumerate(recs):
            with st.container():
                st.subheader(f"💡 Recommendation {idx + 1}: {rec['Rule']}")
                
                col_b1, col_b2 = st.columns([1, 3])
                
                with col_b1:
                    # Strategy Badge type
                    st.info(f"**Strategy Type:**\n{rec['Strategy Type']}")
                    st.write(f"- Confidence: **{rec['Confidence (%)']}%**")
                    st.write(f"- Lift Score: **{rec['Lift']}**")
                    
                with col_b2:
                    st.markdown(f"📊 **Rationale:**\n*{rec['Rationale']}*")
                    st.success(f"🎯 **Action Plan:**\n{rec['Recommendation']}")
                    
                st.write("---")
    else:
        st.error("No rules met your threshold metrics. Reduce support/confidence to generate recommendations.")
