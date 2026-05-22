import os

def generate_html_proposal(eda_stats, rules_df, recommendations, output_path):
    """
    Compiles data metrics and translated strategic rules into a premium, responsive
    HTML business proposal. The report includes print-specific CSS so it compiles
    to a flawless PDF when printed in a web browser.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Renders the KPI Values
    total_tx = eda_stats.get('total_transactions', 0)
    unique_prod = eda_stats.get('unique_products', 0)
    avg_basket = eda_stats.get('avg_basket_size', 0.0)
    strong_rules_count = len(rules_df)
    highest_lift = float(rules_df['lift'].max()) if not rules_df.empty else 0.0
    
    # Construct rules table rows
    rules_rows_html = ""
    if rules_df.empty:
        rules_rows_html = "<tr><td colspan='5' style='text-align:center;'>No significant association rules found at current thresholds.</td></tr>"
    else:
        for idx, row in rules_df.head(15).iterrows():
            rules_rows_html += f"""
            <tr>
                <td><strong>{row['antecedents_str']}</strong></td>
                <td>&rarr; <strong>{row['consequents_str']}</strong></td>
                <td>{row['support']*100:.2f}%</td>
                <td>{row['confidence']*100:.1f}%</td>
                <td class="badge-lift">{row['lift']:.2f}</td>
            </tr>
            """

    # Construct recommendation cards HTML
    recommendations_html = ""
    if not recommendations:
        recommendations_html = "<p>No tailored recommendations available.</p>"
    else:
        for rec in recommendations:
            # Color-code strategy badges based on type
            s_type = rec['Strategy Type']
            badge_class = "badge-default"
            if "Layout" in s_type:
                badge_class = "badge-layout"
            elif "Bundle" in s_type:
                badge_class = "badge-bundle"
            elif "Digital" in s_type:
                badge_class = "badge-digital"
            elif "Impulse" in s_type:
                badge_class = "badge-checkout"

            recommendations_html += f"""
            <div class="strategy-card">
                <div class="card-header">
                    <span class="rule-title">{rec['Rule']}</span>
                    <span class="strategy-badge {badge_class}">{s_type}</span>
                </div>
                <div class="card-body">
                    <p class="rationale"><strong>Rationale:</strong> {rec['Rationale']}</p>
                    <p class="recommendation"><strong>Action Recommendation:</strong> {rec['Recommendation']}</p>
                </div>
                <div class="card-footer">
                    <span>Confidence: <strong>{rec['Confidence (%)']}%</strong></span>
                    <span>Lift Score: <strong>{rec['Lift']}</strong></span>
                </div>
            </div>
            """

    # Complete HTML template with beautiful styling
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Business Strategy Proposal: Market Basket Analysis</title>
    <style>
        :root {{
            --primary: #1e3a8a;
            --primary-light: #3b82f6;
            --text-dark: #1f2937;
            --text-light: #4b5563;
            --bg-light: #f3f4f6;
            --white: #ffffff;
            --border: #e5e7eb;
            
            --color-layout: #059669;
            --color-bundle: #d97706;
            --color-digital: #2563eb;
            --color-checkout: #7c3aed;
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: var(--text-dark);
            background-color: var(--bg-light);
            line-height: 1.6;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            background-color: var(--white);
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            padding: 40px;
        }}
        
        header {{
            border-bottom: 2px solid var(--bg-light);
            padding-bottom: 30px;
            margin-bottom: 40px;
        }}
        
        .logo {{
            color: var(--primary);
            font-size: 28px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}
        
        .doc-title {{
            font-size: 32px;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 12px;
        }}
        
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
            font-size: 14px;
            color: var(--text-light);
        }}
        
        h2 {{
            color: var(--primary);
            font-size: 22px;
            font-weight: 700;
            margin-top: 40px;
            margin-bottom: 20px;
            border-left: 4px solid var(--primary-light);
            padding-left: 12px;
        }}
        
        p {{
            color: var(--text-light);
            margin-bottom: 20px;
            font-size: 15px;
        }}
        
        /* KPI Cards Styling */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .kpi-card {{
            background-color: var(--bg-light);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            border: 1px solid var(--border);
        }}
        
        .kpi-val {{
            font-size: 28px;
            font-weight: 800;
            color: var(--primary);
            margin-bottom: 4px;
        }}
        
        .kpi-label {{
            font-size: 12px;
            font-weight: 600;
            color: var(--text-light);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        /* Rules Table Styling */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 40px;
            font-size: 14px;
        }}
        
        th {{
            background-color: var(--primary);
            color: var(--white);
            text-align: left;
            padding: 12px 16px;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            color: var(--text-dark);
        }}
        
        tr:nth-child(even) {{
            background-color: #fafafa;
        }}
        
        .badge-lift {{
            font-weight: bold;
            color: var(--primary);
        }}
        
        /* Recommendations Cards */
        .strategy-grid {{
            display: flex;
            flex-direction: column;
            gap: 24px;
        }}
        
        .strategy-card {{
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
            background-color: #fcfcfc;
        }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: var(--bg-light);
            padding: 14px 20px;
            border-bottom: 1px solid var(--border);
        }}
        
        .rule-title {{
            font-size: 16px;
            font-weight: 700;
            color: var(--primary);
        }}
        
        .strategy-badge {{
            font-size: 11px;
            font-weight: bold;
            padding: 4px 10px;
            border-radius: 20px;
            text-transform: uppercase;
            color: var(--white);
        }}
        
        .badge-layout {{ background-color: var(--color-layout); }}
        .badge-bundle {{ background-color: var(--color-bundle); }}
        .badge-digital {{ background-color: var(--color-digital); }}
        .badge-checkout {{ background-color: var(--color-checkout); }}
        .badge-default {{ background-color: var(--text-light); }}
        
        .card-body {{
            padding: 20px;
        }}
        
        .rationale {{
            margin-bottom: 10px;
            font-size: 14px;
        }}
        
        .recommendation {{
            font-size: 15px;
            color: var(--text-dark);
            background-color: #f0fdf4;
            padding: 12px;
            border-left: 4px solid var(--color-layout);
            border-radius: 0 4px 4px 0;
            margin-bottom: 0;
        }}
        
        .card-footer {{
            display: flex;
            gap: 30px;
            padding: 12px 20px;
            background-color: var(--bg-light);
            border-top: 1px solid var(--border);
            font-size: 13px;
            color: var(--text-light);
        }}
        
        /* Print Styles */
        @media print {{
            body {{
                background-color: var(--white);
                padding: 0;
            }}
            .container {{
                box-shadow: none;
                padding: 0;
            }}
            .strategy-card {{
                page-break-inside: avoid;
                margin-bottom: 20px;
            }}
            table {{
                page-break-inside: avoid;
            }}
            h2 {{
                page-break-after: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">Retail Analytics Suite</div>
            <h1 class="doc-title">Market Basket Analysis &amp; Strategic Proposal</h1>
            <div class="meta-grid">
                <div><strong>Role:</strong> Data Science Intern, Retail Analytics</div>
                <div><strong>Analysis Focus:</strong> Cross-Selling &amp; Shelf Layout</div>
                <div><strong>Report Scope:</strong> High-Lift Association Rules</div>
            </div>
        </header>
        
        <section>
            <h2>1. Executive Summary</h2>
            <p>
                Market Basket Analysis (MBA) is an algorithmic modeling technique based on the theory that if a customer buys a specific group of items, they are significantly more (or less) likely to buy another group of items. Using transaction logs, we run <strong>Association Rule Mining</strong> to detect hidden product purchase clusters.
            </p>
            <p>
                This proposal translates mathematical probability parameters—<strong>Support</strong>, <strong>Confidence</strong>, and <strong>Lift</strong>—into physical business strategies. The insights below provide actionable store layouts, product bundle campaigns, and online recommendation rules targeted directly at increasing our **Average Order Value (AOV)**.
            </p>
        </section>
        
        <section>
            <h2>2. High-Level Transactional KPIs</h2>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-val">{total_tx:,}</div>
                    <div class="kpi-label">Total Transactions</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-val">{unique_prod:,}</div>
                    <div class="kpi-label">Unique Products</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-val">{avg_basket}</div>
                    <div class="kpi-label">Avg Basket Size</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-val">{strong_rules_count}</div>
                    <div class="kpi-label">Strong Rules Found</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-val">{highest_lift:.2f}</div>
                    <div class="kpi-label">Highest Lift Score</div>
                </div>
            </div>
        </section>
        
        <section>
            <h2>3. Discovered Product Associations (Top 15 Rules by Lift)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Antecedent (If bought...)</th>
                        <th>Consequent (Then also buy...)</th>
                        <th>Support</th>
                        <th>Confidence</th>
                        <th>Lift Ratio</th>
                    </tr>
                </thead>
                <tbody>
                    {rules_rows_html}
                </tbody>
            </table>
        </section>
        
        <section>
            <h2>4. Strategic Business Proposals</h2>
            <div class="strategy-grid">
                {recommendations_html}
            </div>
        </section>
    </div>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Business strategy proposal report successfully compiled to {output_path}")
    return True
