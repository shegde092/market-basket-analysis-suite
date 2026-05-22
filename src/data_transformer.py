import pandas as pd
import numpy as np

def load_csv_robust(file_path_or_buffer):
    """
    Robustly reads a CSV file trying multiple encodings to handle special currency 
    symbols (like £ or 0xa3) gracefully without throwing UnicodeDecodeError.
    """
    encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
    is_buffer = hasattr(file_path_or_buffer, 'seek')
    
    for encoding in encodings:
        try:
            if is_buffer:
                file_path_or_buffer.seek(0)
            return pd.read_csv(file_path_or_buffer, encoding=encoding)
        except UnicodeDecodeError:
            continue
            
    # Fallback if all fail
    if is_buffer:
        file_path_or_buffer.seek(0)
    return pd.read_csv(file_path_or_buffer)

def clean_data(df):
    """
    Cleans raw transactional data:
    1. Removes cancellations (Invoices starting with 'C' or Quantity < 0).
    2. Drops rows with null descriptions or quantities.
    3. Strips description strings of white spaces.
    """
    df_cleaned = df.copy()
    
    # Drop rows with critical null fields
    df_cleaned = df_cleaned.dropna(subset=['InvoiceNo', 'Description', 'Quantity'])
    
    # Clean description spaces
    df_cleaned['Description'] = df_cleaned['Description'].astype(str).str.strip()
    
    # Cast Quantity and UnitPrice to correct numeric formats
    df_cleaned['Quantity'] = pd.to_numeric(df_cleaned['Quantity'], errors='coerce')
    df_cleaned['UnitPrice'] = pd.to_numeric(df_cleaned['UnitPrice'], errors='coerce')
    df_cleaned = df_cleaned.dropna(subset=['Quantity', 'UnitPrice'])
    
    # Exclude cancellations: Invoices starting with "C" or quantities <= 0
    df_cleaned['InvoiceNo'] = df_cleaned['InvoiceNo'].astype(str).str.strip()
    cancellation_mask = df_cleaned['InvoiceNo'].str.startswith('C') | (df_cleaned['Quantity'] <= 0)
    df_cleaned = df_cleaned[~cancellation_mask]
    
    return df_cleaned

def transform_to_basket(df_cleaned):
    """
    Converts a long transaction DataFrame into a memory-efficient One-Hot Encoded (binary) matrix.
    Rows: InvoiceNo
    Columns: Product Descriptions
    Values: True/False (Cast to bool for strict RAM conservation!)
    """
    # Create group-by counts of products per invoice
    basket = (df_cleaned.groupby(['InvoiceNo', 'Description'])['Quantity']
              .sum()
              .unstack()
              .reset_index()
              .fillna(0)
              .set_index('InvoiceNo'))
    
    # MEMORY EFFICIENCY OPTIMIZATION:
    # Instead of leaving it as float64/int64, convert all columns to bool.
    # Boolean representation takes 1 byte per element instead of 8 bytes (int64/float64),
    # reducing memory usage by 87.5% and perfectly aligning with mlxtend's requirements.
    basket_bool = basket.astype(bool)
    
    return basket_bool

def get_eda_stats(df_cleaned, basket_bool):
    """
    Computes key Exploratory Data Analysis metrics:
    - Total Cleaned Transactions
    - Unique Products Count
    - Average Basket Size
    - Top Selling Products (Counts and Support)
    - Sales distribution details
    """
    stats = {}
    stats['total_transactions'] = basket_bool.shape[0]
    stats['unique_products'] = basket_bool.shape[1]
    
    # Calculate average basket size (number of items purchased per invoice)
    items_per_invoice = basket_bool.sum(axis=1)
    stats['avg_basket_size'] = float(np.round(items_per_invoice.mean(), 2))
    stats['max_basket_size'] = int(items_per_invoice.max())
    stats['min_basket_size'] = int(items_per_invoice.min())
    
    # Top selling items
    product_sales = df_cleaned.groupby('Description')['Quantity'].sum().sort_values(ascending=False)
    stats['top_selling'] = product_sales.head(10).to_dict()
    
    # Item frequency/support
    product_support = (basket_bool.sum(axis=0) / basket_bool.shape[0]).sort_values(ascending=False)
    stats['top_support'] = product_support.head(15).to_dict()
    
    return stats
