import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import numpy as np
import os

# Setup page configuration to increase width
# Page configuration
st.set_page_config(
    page_title="Dynamic Superstore Dashboard",
    page_icon="🏬",
    layout="wide",
    initial_sidebar_state="expanded")

DATABASE_URL = os.getenv("DATABASE_URL")

# Set up connection
engine = create_engine(DATABASE_URL)

def load_data(query):
    return pd.read_sql(query, engine)

# Sidebar for filter selection
st.sidebar.title('Filters')
segment = st.sidebar.selectbox('Select Customer Segment', ['ALL'] + pd.read_sql("SELECT DISTINCT segment FROM customer", engine)['segment'].tolist())
category = st.sidebar.selectbox('Select Product Category', ['ALL'] + pd.read_sql("SELECT DISTINCT category FROM product", engine)['category'].tolist())
subcategory = st.sidebar.selectbox('Select Product Subcategory', ['ALL'] + pd.read_sql("SELECT DISTINCT subcategory FROM product", engine)['subcategory'].tolist())
region = st.sidebar.selectbox('Select Region', ['ALL'] + pd.read_sql("SELECT DISTINCT region FROM address", engine)['region'].tolist())
priority = st.sidebar.selectbox('Select Order Priority', ['ALL'] + pd.read_sql("SELECT DISTINCT priority FROM \"Order\"", engine)['priority'].tolist())
shipmode = st.sidebar.selectbox('Select Shipping Mode', ['ALL'] + pd.read_sql("SELECT DISTINCT shipmode FROM shipping", engine)['shipmode'].tolist())
state_province = st.sidebar.selectbox('Select State/Province', ['ALL'] + pd.read_sql("SELECT DISTINCT state_province FROM address", engine)['state_province'].tolist())

# Build dynamic query based on selected filters
filters = []
if segment != 'ALL':
    filters.append(f"c.segment = '{segment}'")
if category != 'ALL':
    filters.append(f"p.category = '{category}'")
if subcategory != 'ALL':
    filters.append(f"p.subcategory = '{subcategory}'")
if region != 'ALL':
    filters.append(f"a.region = '{region}'")
if priority != 'ALL':
    filters.append(f"o.priority = '{priority}'")
if shipmode != 'ALL':
    filters.append(f"sh.shipmode = '{shipmode}'")
if state_province != 'ALL':
    filters.append(f"a.state_province = '{state_province}'")

where_clause = ' AND '.join(filters) if filters else '1=1'

# Queries for various data visualizations
query_sales_time = """
SELECT DATE_TRUNC('month', o.dateordered) as month, SUM(s.sales) as total_sales
FROM sales s
JOIN \"Order\" o ON s.orderguid = o.orderguid
JOIN customer c ON o.customerguid = c.customerguid
JOIN product p ON s.productguid = p.productguid
JOIN shipping sh ON o.shippingguid = sh.shippingguid
JOIN address a ON sh.addressguid = a.addressguid
WHERE {where_clause}
GROUP BY DATE_TRUNC('month', o.dateordered)
ORDER BY month;
""".format(where_clause=where_clause)
sales_time_data = load_data(query_sales_time)

# Top Products by Category
query_top_product_category = """
SELECT p.category, SUM(s.sales) AS total_sales
FROM sales s
JOIN \"Order\" o ON s.orderguid = o.orderguid
JOIN customer c ON o.customerguid = c.customerguid
JOIN product p ON s.productguid = p.productguid
JOIN shipping sh ON o.shippingguid = sh.shippingguid
JOIN address a ON sh.addressguid = a.addressguid
WHERE {where_clause}
GROUP BY p.category
ORDER BY total_sales DESC LIMIT 5;
""".format(where_clause=where_clause)
top_product_category_data = load_data(query_top_product_category)

# Top Customer by Segment
query_top_customer_segment = f"""
SELECT c.segment, SUM(s.sales) AS total_sales
FROM sales s
JOIN \"Order\" o ON s.orderguid = o.orderguid
JOIN customer c ON o.customerguid = c.customerguid
JOIN product p ON s.productguid = p.productguid
JOIN shipping sh ON o.shippingguid = sh.shippingguid
JOIN address a ON sh.addressguid = a.addressguid
WHERE {where_clause}
GROUP BY c.segment
ORDER BY total_sales DESC LIMIT 5;
"""
top_customer_segment_data = load_data(query_top_customer_segment)

# Heatmap of Sales by State (corrected for column name case sensitivity)
query_us_heatmap = f"""
SELECT a.state_code, CAST(REPLACE(REPLACE(CAST(SUM(s.sales) AS TEXT), '$', ''), ',', '') AS FLOAT) AS total_sales
FROM sales s
JOIN \"Order\" o ON s.orderguid = o.orderguid
JOIN customer c ON o.customerguid = c.customerguid
JOIN product p ON s.productguid = p.productguid
JOIN shipping sh ON o.shippingguid = sh.shippingguid
JOIN address a ON sh.addressguid = a.addressguid
WHERE {where_clause}
GROUP BY a.state_code
"""
heatmap_data = load_data(query_us_heatmap)

# Dashboard Visualizations
st.title('Dynamic Superstore Dashboard')

# Total Sales and Profit Query with corrected joins
query_total_sales_profit = f"""
SELECT 
    COALESCE(SUM(CAST(REPLACE(REPLACE(CAST(s.sales AS TEXT), '$', ''), ',', '') AS NUMERIC)), 0) AS total_sales,
    COALESCE(SUM(CAST(REPLACE(REPLACE(CAST(s.profit AS TEXT), '$', ''), ',', '') AS NUMERIC)), 0) AS total_profit
FROM sales s
JOIN \"Order\" o ON s.orderguid = o.orderguid
JOIN customer c ON o.customerguid = c.customerguid
JOIN product p ON s.productguid = p.productguid
JOIN shipping sh ON o.shippingguid = sh.shippingguid
JOIN address a ON sh.addressguid = a.addressguid
WHERE {where_clause}
"""

total_sales_profit_data = load_data(query_total_sales_profit)

# Extract and validate total sales and profit data
if total_sales_profit_data.isna().any().any():
    st.error("Data conversion error: Non-numeric data found.")
else:
    total_sales = total_sales_profit_data.loc[0, 'total_sales']
    total_profit = total_sales_profit_data.loc[0, 'total_profit']

    # Utility function to format numbers in K/M/B notation
def format_number(num):
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)

# Adjusting column widths for layout optimization
col1, col2 = st.columns([3, 2])  # Adjusting to 3:2 ratio for a better fit

# Display key metrics
with col1:
    # Displaying key metrics side by side
    st.subheader("Key Metrics")
    metrics_col1, metrics_col2 = st.columns(2)  # Create two columns for metrics
    with metrics_col1:
        st.metric(label="Total Sales", value=f"${format_number(total_sales)}")
    with metrics_col2:
        st.metric(label="Total Profit", value=f"${format_number(total_profit)}")

    # Heatmap of Sales by State
    st.subheader("US Heatmap of Sales")
    fig_us_heatmap = px.choropleth(
        heatmap_data,
        locations='state_code',
        locationmode='USA-states',
        color='total_sales',
        color_continuous_scale=px.colors.sequential.Plasma,
        scope="usa",
        labels={'total_sales': 'Total Sales'}
    )
    st.plotly_chart(fig_us_heatmap, use_container_width=True)

with col2:
    # Top Products by Category
    st.subheader("Top Products by Category")
    fig_top_product_by_category = px.bar(
        top_product_category_data,
        x='total_sales',
        y='category',
        orientation='h',
        title='Top Products'
    )
    st.plotly_chart(fig_top_product_by_category, use_container_width=True)

# Using two columns for bottom visualizations
col1, col2 = st.columns(2)
with col1:
    st.header('Monthly Sales Over Time')
    fig_sales_time = px.line(sales_time_data, x='month', y='total_sales', title='Monthly Sales Over Time')
    st.plotly_chart(fig_sales_time)

with col2:
    st.header('Top Customers by Segment')

    # Ensure data is cleaned and formatted correctly
    if not top_customer_segment_data.empty and 'total_sales' in top_customer_segment_data:
        # Remove dollar signs and commas, then convert to float
        top_customer_segment_data['total_sales'] = top_customer_segment_data['total_sales'].replace('[\$,]', '', regex=True).astype(float)

        # Create the pie chart visualization
        fig_top_customer_by_segment = px.pie(top_customer_segment_data, 
                                            values='total_sales', 
                                            names='segment', 
                                            title='Top Customers by Segment', 
                                            hole=0.4)  # Adjust the hole size for donut appearance

        # Update layout to place the legend on the right side
        fig_top_customer_by_segment.update_layout(
            legend_title_text='Customer Segment',
            legend=dict(
                orientation="v",  # Vertical layout for the legend
                yanchor="middle",  # Anchor legend at the middle vertically
                y=0.5,  # Position at the middle of the plot vertically
                xanchor="left",  # Anchor legend at the left side of its box
                x=1.05  # Position the legend just outside the right side of the chart
            )
        )

        # Display the plot
        st.plotly_chart(fig_top_customer_by_segment)
    else:
        st.error('Data is not loaded correctly or missing required columns.')


