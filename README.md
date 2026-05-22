# Market Basket Analysis (MBA) Suite

A comprehensive Retail Analytics dashboard and command-line engine to detect hidden patterns in transactional lists using Association Rule Mining (Apriori and FP-Growth).

## 📂 Project Structure

```text
market_basket_analysis/
├── app.py                     # Streamlit Dashboard (Primary Interactive Frontend)
├── main.py                    # CLI Orchestrator (Headless Mode Pipeline)
├── requirements.txt           # Python Dependencies
├── README.md                  # Documentation File
│
├── data/                      # Transaction Data Input Folder
│   └── online_retail_sample.csv  # Realistic Transaction Logs (Generated Mock Data)
│
├── outputs/                   # Analysis Output Deliverables
│   ├── association_rules.csv  # Mined Association Rules CSV
│   ├── network_graph.png      # High-Resolution Static Network Map
│   ├── network_graph.html     # Physics-Enabled Interactive Network Constellation
│   └── strategy_proposal.html # Print-Ready HTML Strategy Proposal Report
│
└── src/                       # Backend Source Code Module
    ├── __init__.py            # Package Init
    ├── generate_data.py       # Mock Retail Transaction Generator
    ├── data_transformer.py    # Cleaning & Memory-Efficient One-Hot pivot (Bool casting)
    ├── rules_engine.py        # Apriori / FP-Growth Engine and Benchmark Speed comparison
    ├── visualizer.py          # NetworkX & PyVis Map Generation (Anti-Hairball filtering)
    ├── business_rules.py      # Rule-to-Strategy qualitative mapper
    └── report_generator.py    # Report template builder
```

## 🚀 Setup & Execution

### 1. Install Dependencies
Make sure you have Python 3 installed. Navigate to the project root directory and run:
```powershell
pip install -r requirements.txt
```

### 2. Run the Interactive Dashboard
To launch the Streamlit frontend dashboard (equipped with metrics cards, dynamic sliders, top product sales charts, interactive physics floating constellations, and strategies cards):
```powershell
python -m streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### 3. Run via Headless Command Line (CLI)
To run the analysis pipeline completely headlessly and write results directly to `outputs/`:
```powershell
python main.py --run-all --support 0.01 --confidence 0.3 --lift 1.2
```
Options:
* `--support`: Minimum support threshold (default: `0.01`).
* `--confidence`: Minimum confidence threshold (default: `0.3`).
* `--lift`: Minimum lift threshold (default: `1.2`).
* `--algorithm`: Choice of `fpgrowth`, `apriori`, or `both` (default: `fpgrowth`).
* `--generate`: Forces writing a fresh set of mock transaction data.
* `--num-tx`: Number of mock invoices to generate (default: `2000`).
