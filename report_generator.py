#!/usr/bin/env python3
"""
report_generator.py
Reads sales_data.csv and prints a summary report,
also writes report to ./report/report_<timestamp>.txt
"""

import os, sys
from datetime import datetime

# optional: use pandas if available for easier grouping
try:
    import pandas as pd
except Exception:
    pd = None

INPUT = "sales_data.csv"
OUTDIR = "report"
OUTFILE = os.path.join(OUTDIR, f"sales_report_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.txt")

def load_data(path):
    if not os.path.exists(path):
        print(f"ERROR: input file {path} not found", file=sys.stderr)
        sys.exit(2)
    if pd:
        return pd.read_csv(path)
    else:
        # fallback: parse csv with basic logic
        import csv
        rows = []
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                r['units_sold'] = int(r['units_sold'])
                r['unit_price'] = float(r['unit_price'])
                rows.append(r)
        return rows


#comment_1

def generate_summary(df):
    # If pandas available, use it
    if pd:
        total_revenue = (df['units_sold'] * df['unit_price']).sum()
        total_units = df['units_sold'].sum()
        by_artisan = df.assign(revenue=df['units_sold']*df['unit_price']).groupby('artisan').agg(
            units_sold=('units_sold','sum'),
            revenue=('revenue','sum')
        ).sort_values('revenue', ascending=False)
        by_product = df.assign(revenue=df['units_sold']*df['unit_price']).groupby('product').agg(
            units_sold=('units_sold','sum'),
            revenue=('revenue','sum')
        ).sort_values('revenue', ascending=False)
        return total_revenue, total_units, by_artisan, by_product
    else:
        # basic Python grouping
        total_revenue = 0.0
        total_units = 0
        by_artisan = {}
        by_product = {}
        for r in df:
            rev = r['units_sold'] * r['unit_price']
            total_revenue += rev
            total_units += r['units_sold']
            by_artisan.setdefault(r['artisan'], {'units':0,'revenue':0.0})
            by_artisan[r['artisan']]['units'] += r['units_sold']
            by_artisan[r['artisan']]['revenue'] += rev
            by_product.setdefault(r['product'], {'units':0,'revenue':0.0})
            by_product[r['product']]['units'] += r['units_sold']
            by_product[r['product']]['revenue'] += rev
        # convert to sorted lists
        by_artisan_sorted = sorted(by_artisan.items(), key=lambda x: x[1]['revenue'], reverse=True)
        by_product_sorted = sorted(by_product.items(), key=lambda x: x[1]['revenue'], reverse=True)
        return total_revenue, total_units, by_artisan_sorted, by_product_sorted

def print_and_save(total_revenue, total_units, by_artisan, by_product):
    if not os.path.exists(OUTDIR):
        os.makedirs(OUTDIR, exist_ok=True)

    lines = []
    lines.append(f"Sales Summary Report - generated at {datetime.utcnow().isoformat()} UTC")
    lines.append("="*60)
    lines.append(f"Total units sold: {total_units}")
    lines.append(f"Total revenue: INR {total_revenue:.2f}")
    lines.append("")
    lines.append("Revenue by artisan:")
    if pd:
        for idx, row in by_artisan.reset_index().iterrows():
            lines.append(f" - {row['artisan']}: units={row['units_sold']}, revenue=INR {row['revenue']:.2f}")
    else:
        for artisan, vals in by_artisan:
            lines.append(f" - {artisan}: units={vals['units']}, revenue=INR {vals['revenue']:.2f}")

    lines.append("")
    lines.append("Revenue by product:")
    if pd:
        for idx, row in by_product.reset_index().iterrows():
            lines.append(f" - {row['product']}: units={row['units_sold']}, revenue=INR {row['revenue']:.2f}")
    else:
        for product, vals in by_product:
            lines.append(f" - {product}: units={vals['units']}, revenue=INR {vals['revenue']:.2f}")

    report_text = "\n".join(lines)
    print(report_text)
    with open(OUTFILE, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"\nSaved report to: {OUTFILE}")

def main():
    try:
        df = load_data(INPUT)
        total_revenue, total_units, by_artisan, by_product = generate_summary(df)
        print_and_save(total_revenue, total_units, by_artisan, by_product)
        sys.exit(0)
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

