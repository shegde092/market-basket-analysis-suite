# 📊 Retail Market Basket Analytics Suite
> **An End-to-End Retail Intelligence Platform for Upselling & Cross-Selling**

[![Streamlit App](https://static.streamlit.io/badge_svg.svg)](https://market-basket-analysis-suite-hkwkdzrgkazqlauyygf5bu.streamlit.app/)
[![GitHub License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/shegde092/market-basket-analysis-suite/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg)](#)

Have you ever wondered why grocery stores place butter next to bread, or why e-commerce giants suggest a screen protector the second you add a smartphone to your cart? This is not intuition—it is the math of **Market Basket Analysis (MBA)**.

This production-grade analytics platform uses **Association Rule Mining** (comparing tree-based **FP-Growth** and classic **Apriori** algorithms) to discover high-strength consumer purchase patterns. It transforms raw transactional lists into dynamic, interactive affinity clusters and compiles strategic, print-ready business proposals to boost **Average Order Value (AOV)**.

---

## 🚀 Live Interactive Dashboard
You can access and interact with the live deployed project directly on the web:

👉 **[Access the Live Analytics Dashboard](https://market-basket-analysis-suite-hkwkdzrgkazqlauyygf5bu.streamlit.app/)**

### 💡 What you can do on the Live Dashboard:
* **Dynamic Parameter Sliders:** Tune **Minimum Support**, **Confidence**, and **Lift** in real-time to watch rules recalculate.
* **Upload Custom Datasets:** Drag and drop your own raw retail transactional CSVs (up to 200MB) to mine patterns instantly.
* **Apriori vs FP-Growth Benchmark:** Inspect the live Plotly comparison bar chart showcasing the massive speed increase of FP-Growth on large catalogs.
* **Interactive Affinity Constellation:** Drag, zoom, and explore a physics-enabled floating product clusters network map.
* **Download Mined Rules:** Export the generated rules as a clean CSV with a single click.

---

## ✨ Core Platform Features

### 🧹 1. Multi-Encoding Preprocessing & Booleans
* **Encoding Safety:** Bypasses common retail currency symbol encoding errors (e.g. Pound `£` signs represented as byte `0xa3`) using robust multi-fallback CP1252, Latin1, and UTF-8 decoders.
* **Rigorous Cleaning:** Filters returns/cancellations (Invoices starting with 'C' or Quantity $\le 0$), trims spacing, and ignores null values.
* **Boolean Pivoting:** Converts sparse 'Long' transactional logs into a memory-efficient boolean matrix, cutting RAM footprint by **87.5%**.

### ⏱️ 2. High-Performance Dual-Algorithm Mining
* **Apriori Safety-Bypass:** Bypasses Apriori's exponential $O(2^N)$ combinatorial search space on huge catalogs to prevent browser freezes or Out-of-Memory crashes.
* **Tree-Based FP-Growth:** Successfully mines **20,136 transactions** in **under 0.2 seconds** by utilizing a RAM-compressed FP-Tree.
* **Safe-Sample Speed Benchmark:** Runs both algorithms on a small, dense representative slice (300 transactions, 15 items) to show a beautiful speed comparison chart live without blocking execution.

### 🕸️ 3. Visual Affinity Constellations
* **Dynamic PyVis Networks:** Nodes represent products (sized by popularity/Support) and edges represent rules (thickness scaled by Lift/Affinity strength).
* **Affinity Clusters:** Physics-enabled gravity-forces automatically cluster associated products into clear segments:
  * 🥞 **The Breakfast Cluster:** Whole Wheat Bread, Unsalted Butter, Strawberry Jam, Organic Milk, Ground Coffee.
  * 🍪 **The Baking Cluster:** All-Purpose Flour, White Sugar, Baking Powder, Chocolate Chips, Eggs.
  * 🍿 **The Weekend Party Cluster:** Tortilla Chips, Mild Tomato Salsa, Cheddar Cheese Block, Potato Chips, Soft Drinks.

### 📝 4. Automated Strategy Proposal Compiler
* Generates a fully compiled, standalone, professional business report.
* Outlines co-merchandising displays, cross-promotional weekend bundles, and digital cart upsells.
* Tailored as a **print-ready document** (open it in your browser and press **Ctrl+P** to save as a flawless PDF).

---

## 📂 Project Architecture

```text
market_basket_analysis/
├── app.py                     # Streamlit Dashboard (Primary Web Frontend)
├── main.py                    # CLI Orchestrator (Headless Mode Pipeline)
├── requirements.txt           # Python Dependencies List
├── README.md                  # Beautiful Project Documentation
│
├── data/                      # Input Data Folder
│   └── online_retail_sample.csv  # Realistic transactional logs (default fallback)
│
├── outputs/                   # Generated Deliverables
│   ├── association_rules.csv  # Mined rules sorted by Lift
│   ├── network_graph.png      # High-resolution static constellation map
│   ├── network_graph.html     # Interactive physics-enabled network graph
│   └── strategy_proposal.html # Deployed standalone business proposal
│
└── src/                       # Modular Backend Packages
    ├── __init__.py            # Package Invalidation
    ├── generate_data.py       # Custom Mock Retail Transaction Writer
    ├── data_transformer.py    # Robust multi-encoding cleaner & boolean pivoted matrix
    ├── rules_engine.py        # Safe-sample benchmark, Apriori & FP-Growth mining
    ├── visualizer.py          # NetworkX topology & PyVis interactive embedding
    ├── business_rules.py      # Rule translating algorithms for retail strategy
    └── report_generator.py    # Jinja2 compiled HTML strategy template
```

---

## 🛠️ Local Development Setup

To run the application locally on your computer, follow these quick steps:

### 1. Clone & Install Dependencies
Ensure you have Python 3.9 or higher installed. Open your terminal in the project directory and run:
```bash
# Install required libraries
pip install -r requirements.txt
```

### 2. Run the Interactive Dashboard
To boot up the Streamlit server locally:
```bash
python -m streamlit run app.py
```
Open your browser at **`http://localhost:8501`**.

### 3. Run the Headless CLI Pipeline
To run the analysis headlessly from your terminal and save deliverables directly to `outputs/`:
```bash
python main.py --run-all --support 0.01 --confidence 0.3 --lift 1.2
```
* **Command Arguments:**
  * `--support`: Minimum Support threshold (default: `0.01`).
  * `--confidence`: Minimum Confidence threshold (default: `0.3`).
  * `--lift`: Minimum Lift threshold (default: `1.2`).
  * `--algorithm`: Select `fpgrowth`, `apriori`, or `both` (default: `fpgrowth`).
  * `--data-path`: Path to raw CSV (default: `data/online_retail_sample.csv`).

---

## 🧮 Mathematical Pillars of MBA

The rules engine filters and ranks associations based on three primary mathematical metrics:

| Metric | Formulation | Description | Business Interpretation |
| :--- | :--- | :--- | :--- |
| **Support** | $$P(A \cap B) = \frac{\text{Freq}(A, B)}{N}$$ | How frequently the items appear together in the catalog. | **Popularity:** High support indicates a massive portion of shoppers buy this bundle. |
| **Confidence** | $$P(B \mid A) = \frac{\text{Freq}(A, B)}{\text{Freq}(A)}$$ | The probability that B is purchased given that A is in the cart. | **Predictability:** Higher confidence represents a stronger directional rule. |
| **Lift** | $$\frac{\text{Confidence}}{P(B)}$$ | The ratio of observed support to expected support if purchases were completely independent. | **Relationship Strength:** Lift > 1 represents a true "hidden" association. |

---

## 🌟 Acknowledgements & Internship Portfolio
* **Developer:** Soujanya K Hegde
* **GitHub Repository:** [shegde092/market-basket-analysis-suite](https://github.com/shegde092/market-basket-analysis-suite)
