import os
import sqlite3
import warnings
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st

# Handle SSL certificates safely across environments
try:
    import certifi
    os.environ["SSL_CERT_FILE"] = certifi.where()
    os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
except ImportError:
    pass  # Uses system default certificates if certifi is not installed

warnings.filterwarnings("ignore")

# Set page config
st.set_page_config(
    page_title="Food Delivery Analytics",
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Set style
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")

# ============================================
# LOAD DATA
# ============================================
@st.cache_data
def load_data():
    df = pd.read_csv(r"D:\New folder (2)\.vscode\Online_FoodDelivery\CLEANED_FOOD_DELIVERY_DATA.zip")
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ 'CLEANED_FOOD_DELIVERY_DATA.zip' not found. Please ensure the dataset is in the same folder as this script.")
    st.stop()

# Helper function to display reusable data table section
def display_table_view(table_df, title="📄 Detailed Data Table", filename="data_export.csv"):
    st.markdown("---")
    st.subheader(title)
    
    records_count = int(table_df.shape[0])
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption(f"Showing **{records_count:,}** records")
    with col2:
        csv_data = table_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Table CSV",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            use_container_width=True
        )
    
    st.dataframe(table_df, use_container_width=True, hide_index=True)

# ============================================
# SIDEBAR NAVIGATION
# ============================================
st.sidebar.title("🍕 Food Delivery Analytics")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Select Analysis",
    ["📊 Dashboard Overview",
     "📈 Order Distributions",
     "🏙️ City & Cuisine Analysis",
     "📅 Weekend vs Weekday",
     "🚗 Distance & Delivery",
     "❌ Cancellations",
     "📉 Correlations",
     "💡 Business Insights",
     "🛢️ SQL Queries"]
)

st.sidebar.markdown("---")
st.sidebar.info(f"""
### 📋 Dataset Info
- **Total Orders**: {df['Order_ID'].nunique():,}
- **Total Customers**: {df['Customer_ID'].nunique():,}
- **Total Restaurants**: {df['Restaurant_ID'].nunique():,}
- **Delivery Partners**: {df['Delivery_Partner_ID'].nunique():,}
""")

# ============================================
# PAGE 1: DASHBOARD OVERVIEW
# ============================================
if page == "📊 Dashboard Overview":
    st.title("🍕 Online Food Delivery Analytics Dashboard")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Orders", f"{df.shape[0]:,}", delta="100%", delta_color="off")
    with col2:
        st.metric("Avg Order Value", f"₹{df['Order_Value'].mean():.0f}", delta=f"Median: ₹{df['Order_Value'].median():.0f}", delta_color="off")
    with col3:
        st.metric("Avg Delivery Time", f"{df['Delivery_Time_Min'].mean():.0f} min", delta=f"Max: {df['Delivery_Time_Min'].max():.0f} min", delta_color="off")
    with col4:
        cancel_rate = (df['Order_Status'] == 'Cancelled').mean() * 100
        st.metric("Cancellation Rate", f"{cancel_rate:.1f}%", delta=f"{(df['Order_Status'] == 'Delivered').sum():,} Delivered", delta_color="normal")
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("💰 Revenue Metrics")
        st.write(f"""
        - **Total Revenue**: ₹{df['Final_Amount'].sum()/1e6:.1f}M
        - **Avg Discount**: ₹{df['Discount_Applied'].mean():.0f}
        - **Avg Profit Margin**: {df['Profit_Margin'].mean():.2f}
        """)
    
    with col2:
        st.subheader("⭐ Rating Metrics")
        st.write(f"""
        - **Avg Restaurant Rating**: {df['Restaurant_Rating'].mean():.2f}⭐
        - **Avg Delivery Rating**: {df['Delivery_Rating'].mean():.2f}⭐
        - **Ratings Count**: {df['Restaurant_Rating'].notna().sum():,}
        """)
    
    with col3:
        st.subheader("📍 Geographic Metrics")
        st.write(f"""
        - **Cities**: {df['City'].nunique()}
        - **Areas**: {df['Area'].nunique()}
        - **Cuisines**: {df['Cuisine_Type'].nunique()}
        """)

    display_table_view(df.head(100), title="📋 Dataset Preview (First 100 Orders)", filename="raw_orders_sample.csv")

# ============================================
# PAGE 2: ORDER DISTRIBUTIONS
# ============================================
elif page == "📈 Order Distributions":
    st.title("📈 Distribution of Order Values & Delivery Time")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Order Value Distribution")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(df['Order_Value'].dropna(), bins=50, color='steelblue', edgecolor='white', alpha=0.8)
        ax.axvline(df['Order_Value'].mean(), color='red', linestyle='--', linewidth=2, label=f"Mean: ₹{df['Order_Value'].mean():.0f}")
        ax.axvline(df['Order_Value'].median(), color='green', linestyle='--', linewidth=2, label=f"Median: ₹{df['Order_Value'].median():.0f}")
        ax.set_xlabel('Order Value (₹)')
        ax.set_ylabel('Frequency')
        ax.legend()
        st.pyplot(fig)
    
    with col2:
        st.subheader("Delivery Time Distribution")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(df['Delivery_Time_Min'].dropna(), bins=50, color='coral', edgecolor='white', alpha=0.8)
        ax.axvline(df['Delivery_Time_Min'].mean(), color='red', linestyle='--', linewidth=2, label=f"Mean: {df['Delivery_Time_Min'].mean():.0f} min")
        ax.axvline(df['Delivery_Time_Min'].median(), color='green', linestyle='--', linewidth=2, label=f"Median: {df['Delivery_Time_Min'].median():.0f} min")
        ax.set_xlabel('Delivery Time (Minutes)')
        ax.set_ylabel('Frequency')
        ax.legend()
        st.pyplot(fig)

    summary_stats = df[['Order_Value', 'Delivery_Time_Min', 'Final_Amount', 'Profit_Margin']].describe().T
    summary_stats = summary_stats.reset_index().rename(columns={'index': 'Metric'})
    display_table_view(summary_stats, title="📊 Order Distribution Summary Statistics Table", filename="order_distribution_stats.csv")

# ============================================
# PAGE 3: CITY & CUISINE ANALYSIS
# ============================================
elif page == "🏙️ City & Cuisine Analysis":
    st.title("🏙️ City-Wise & Cuisine-Wise Order Analysis")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Orders by City")
        city_orders = df['City'].value_counts()
        fig = px.bar(city_orders, x=city_orders.index, y=city_orders.values, labels={'x': 'City', 'y': 'Orders'}, color=city_orders.values, color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Orders by Cuisine")
        cuisine_orders = df['Cuisine_Type'].value_counts()
        fig = px.bar(cuisine_orders, x=cuisine_orders.index, y=cuisine_orders.values, labels={'x': 'Cuisine', 'y': 'Orders'}, color=cuisine_orders.values, color_continuous_scale='Greens')
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.subheader("Avg Rating by Cuisine")
        cuisine_rating = df.groupby('Cuisine_Type')['Restaurant_Rating'].mean().sort_values(ascending=False)
        fig = px.bar(cuisine_rating, x=cuisine_rating.index, y=cuisine_rating.values, labels={'x': 'Cuisine', 'y': 'Rating'}, color=cuisine_rating.values, color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)

    city_cuisine_table = pd.crosstab(df['City'], df['Cuisine_Type'], margins=True, margins_name="Total").reset_index()
    display_table_view(city_cuisine_table, title="🏙️ City vs Cuisine Order Breakdown Table", filename="city_cuisine_breakdown.csv")

# ============================================
# PAGE 4: WEEKEND VS WEEKDAY
# ============================================
elif page == "📅 Weekend vs Weekday":
    st.title("📅 Weekend vs Weekday Demand Analysis")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.subheader("Order Split")
        day_orders = df['Order_Day'].value_counts()
        fig = px.pie(day_orders, names=day_orders.index, values=day_orders.values, title="Orders: Weekend vs Weekday")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Avg Order Value")
        day_value = df.groupby('Order_Day')['Order_Value'].mean()
        fig = px.bar(day_value, x=day_value.index, y=day_value.values, labels={'x': 'Day', 'y': 'Avg Value (₹)'}, color=day_value.values, color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.subheader("Avg Delivery Time")
        day_delivery = df.groupby('Order_Day')['Delivery_Time_Min'].mean()
        fig = px.bar(day_delivery, x=day_delivery.index, y=day_delivery.values, labels={'x': 'Day', 'y': 'Avg Time (min)'}, color=day_delivery.values, color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        st.subheader("Cancellation Rate")
        cancel_day = df.groupby('Order_Day')['Order_Status'].apply(lambda s: (s == 'Cancelled').mean() * 100)
        fig = px.bar(cancel_day, x=cancel_day.index, y=cancel_day.values, labels={'x': 'Day', 'y': 'Cancel Rate (%)'}, color=cancel_day.values, color_continuous_scale='Oranges')
        st.plotly_chart(fig, use_container_width=True)

    day_table = df.groupby('Order_Day').agg(
        Total_Orders=('Order_ID', 'count'),
        Avg_Order_Value=('Order_Value', 'mean'),
        Avg_Delivery_Time_Min=('Delivery_Time_Min', 'mean'),
        Avg_Profit_Margin=('Profit_Margin', 'mean')
    ).reset_index()
    display_table_view(day_table, title="📅 Weekend vs Weekday Performance Summary Table", filename="weekend_weekday_summary.csv")

# ============================================
# PAGE 5: DISTANCE & DELIVERY
# ============================================
elif page == "🚗 Distance & Delivery":
    st.title("🚗 Distance vs Delivery Delay Relationship")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distance vs Delivery Time (Scatter)")
        sample_size = min(2000, df.shape[0])
        sample_df = df.sample(sample_size, random_state=42)
        fig = px.scatter(sample_df, x='Distance_km', y='Delivery_Time_Min', opacity=0.5, title="Distance vs Delivery Time")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Delivery Time by Distance Range")
        df['Distance_Bin'] = pd.cut(df['Distance_km'], bins=[0, 5, 10, 15, 20, 30, 40], labels=['0-5km', '5-10km', '10-15km', '15-20km', '20-30km', '30-40km'])
        dist_delivery = df.groupby('Distance_Bin', observed=False)['Delivery_Time_Min'].mean()
        fig = px.bar(dist_delivery, x=dist_delivery.index, y=dist_delivery.values, labels={'x': 'Distance Range', 'y': 'Avg Delivery (min)'}, color=dist_delivery.values, color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)

    dist_table = df.groupby('Distance_Bin', observed=False).agg(
        Total_Orders=('Order_ID', 'count'),
        Avg_Delivery_Time_Min=('Delivery_Time_Min', 'mean'),
        Avg_Delivery_Rating=('Delivery_Rating', 'mean')
    ).reset_index()
    display_table_view(dist_table, title="🚗 Delivery Time by Distance Range Table", filename="distance_delivery_table.csv")

# ============================================
# PAGE 6: CANCELLATIONS
# ============================================
elif page == "❌ Cancellations":
    st.title("❌ Cancellation Reasons Analysis")
    st.markdown("---")
    
    cancelled_df = df[df['Order_Status'] == 'Cancelled']
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cancellation Reasons Distribution")
        cancel_reasons = cancelled_df['Cancellation_Reason'].value_counts()
        fig = px.pie(cancel_reasons, names=cancel_reasons.index, values=cancel_reasons.values, title="Why Orders Were Cancelled")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Cancellation Rate by City")
        cancel_city = cancelled_df.groupby('City').size()
        total_city = df.groupby('City').size()
        cancel_rate_city = (cancel_city / total_city * 100).sort_values(ascending=False)
        fig = px.bar(cancel_rate_city, x=cancel_rate_city.index, y=cancel_rate_city.values, labels={'x': 'City', 'y': 'Cancellation Rate (%)'}, color=cancel_rate_city.values, color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)

    cancel_table = cancelled_df[['Order_ID', 'City', 'Cuisine_Type', 'Order_Value', 'Cancellation_Reason', 'Payment_Mode']].head(100)
    display_table_view(cancel_table, title="❌ Recent Cancelled Orders Log Table", filename="cancelled_orders_log.csv")

# ============================================
# PAGE 7: CORRELATIONS
# ============================================
elif page == "📉 Correlations":
    st.title("📉 Correlation Analysis")
    st.markdown("---")
    
    numeric_cols = ['Customer_Age', 'Delivery_Time_Min', 'Distance_km', 'Order_Value', 'Discount_Applied', 'Final_Amount', 'Delivery_Rating', 'Restaurant_Rating', 'Peak_Hour', 'Profit_Margin']
    valid_numeric_cols = [col for col in numeric_cols if col in df.columns]
    corr_matrix = df[valid_numeric_cols].corr()
    
    st.subheader("Correlation Heatmap")
    fig = px.imshow(corr_matrix, labels=dict(color="Correlation"), color_continuous_scale="RdYlGn", zmin=-1, zmax=1, text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

    corr_table = corr_matrix.reset_index().rename(columns={'index': 'Feature'})
    display_table_view(corr_table, title="📉 Correlation Matrix Table", filename="correlation_matrix.csv")

# ============================================
# PAGE 8: BUSINESS INSIGHTS
# ============================================
elif page == "💡 Business Insights":
    st.title("💡 Business Insights & Recommendations")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🎯 Key Findings")
        st.write(f"""
        1. **Order Volume**: {df.shape[0]:,} total orders processed
        2. **Average Order Value**: ₹{df['Order_Value'].mean():.0f}
        3. **Cancellation Rate**: {(df['Order_Status']=='Cancelled').mean()*100:.1f}%
        4. **Top City**: {df['City'].value_counts().index[0]} with {df['City'].value_counts().values[0]:,} orders
        5. **Top Cuisine**: {df['Cuisine_Type'].value_counts().index[0]} with {df['Cuisine_Type'].value_counts().values[0]:,} orders
        6. **Avg Delivery Time**: {df['Delivery_Time_Min'].mean():.0f} minutes
        7. **Profit Margin**: {df['Profit_Margin'].mean():.2f} (Avg)
        8. **Loss Making Orders**: {(df['Profit_Margin']<0).sum():,} ({(df['Profit_Margin']<0).mean()*100:.1f}%)
        """)
    
    with col2:
        st.subheader("💰 Revenue Insights")
        st.write(f"""
        - **Total Revenue**: ₹{df['Final_Amount'].sum()/1e6:.1f}M
        - **Top Revenue City**: {df.groupby('City')['Final_Amount'].sum().idxmax()}
        - **Top Revenue Cuisine**: {df.groupby('Cuisine_Type')['Final_Amount'].sum().idxmax()}
        - **Best Rated Cuisine**: {df.groupby('Cuisine_Type')['Restaurant_Rating'].mean().idxmax()} ({df.groupby('Cuisine_Type')['Restaurant_Rating'].mean().max():.2f}⭐)
        - **Most Reliable Delivery**: {df.groupby('Order_Day')['Delivery_Rating'].mean().idxmax()} ({df.groupby('Order_Day')['Delivery_Rating'].mean().max():.2f}⭐)
        """)

    city_kpi_table = df.groupby('City').agg(
        Total_Orders=('Order_ID', 'count'),
        Total_Revenue=('Final_Amount', 'sum'),
        Avg_Rating=('Restaurant_Rating', 'mean'),
        Avg_Delivery_Time=('Delivery_Time_Min', 'mean')
    ).reset_index()
    display_table_view(city_kpi_table, title="💡 City Executive KPI Scorecard Table", filename="city_kpi_scorecard.csv")

# ============================================
# PAGE 9: SQL QUERIES
# ============================================
elif page == "🛢️ SQL Queries":
    st.title("🛢️ SQL Query Analytical Views")
    st.markdown("All pre-calculated analytical queries executed live against the `df` SQLite table.")
    st.markdown("---")

    conn = sqlite3.connect(":memory:")
    df.to_sql("df", conn, index=False, if_exists="replace")

    all_queries = {
        "🏙️ Top 5 Cities by Revenue": {
            "sql": """
            SELECT 
                City, 
                COUNT(Order_ID) AS Total_Orders, 
                ROUND(SUM(Final_Amount), 2) AS Total_Revenue,
                ROUND(AVG(Order_Value), 2) AS Avg_Order_Value
            FROM df
            GROUP BY City
            ORDER BY Total_Revenue DESC
            LIMIT 5;
            """,
            "filename": "top_cities_revenue.csv",
            "chart_type": "bar",
            "x": "City",
            "y": "Total_Revenue",
            "color": "Total_Revenue"
        },
        "❌ Cancellation Breakdown by Reason": {
            "sql": """
            SELECT 
                Cancellation_Reason, 
                COUNT(*) AS Cancelled_Orders,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM df WHERE Order_Status = 'Cancelled'), 2) AS Percentage
            FROM df
            WHERE Order_Status = 'Cancelled'
            GROUP BY Cancellation_Reason
            ORDER BY Cancelled_Orders DESC;
            """,
            "filename": "cancellation_reasons.csv",
            "chart_type": "pie",
            "names": "Cancellation_Reason",
            "values": "Cancelled_Orders"
        },
        "🍕 Cuisine Performance & Ratings": {
            "sql": """
            SELECT 
                Cuisine_Type, 
                COUNT(Order_ID) AS Total_Orders,
                ROUND(AVG(Restaurant_Rating), 2) AS Avg_Rating,
                ROUND(AVG(Delivery_Time_Min), 1) AS Avg_Delivery_Min
            FROM df
            GROUP BY Cuisine_Type
            ORDER BY Total_Orders DESC;
            """,
            "filename": "cuisine_performance.csv",
            "chart_type": "bar",
            "x": "Cuisine_Type",
            "y": "Total_Orders",
            "color": "Avg_Rating"
        },
        "📉 Loss-Making Orders Analysis": {
            "sql": """
            SELECT 
                City,
                Cuisine_Type,
                COUNT(Order_ID) AS Loss_Orders_Count,
                ROUND(AVG(Profit_Margin), 2) AS Avg_Profit_Margin
            FROM df
            WHERE Profit_Margin < 0
            GROUP BY City, Cuisine_Type
            ORDER BY Loss_Orders_Count DESC
            LIMIT 10;
            """,
            "filename": "loss_making_orders.csv",
            "chart_type": "bar",
            "x": "Cuisine_Type",
            "y": "Loss_Orders_Count",
            "color": "City"
        }
    }

    for title, query_info in all_queries.items():
        with st.container():
            st.subheader(title)
            
            res_df = pd.read_sql_query(query_info["sql"], conn)
            
            with st.expander("🔍 View SQL Query Code"):
                st.code(query_info["sql"], language="sql")
            
            col_info, col_toggle, col_btn = st.columns([2, 1, 1])
            with col_info:
                st.caption(f"Returned **{res_df.shape[0]:,}** rows")
            with col_toggle:
                view_type = st.radio(
                    "View As:",
                    ["📋 Table", "📊 Chart"],
                    key=f"toggle_{query_info['filename']}",
                    horizontal=True
                )
            with col_btn:
                csv_data = res_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Export CSV",
                    data=csv_data,
                    file_name=query_info["filename"],
                    mime="text/csv",
                    key=f"dl_{query_info['filename']}",
                    use_container_width=True
                )
            
            if view_type == "📋 Table":
                st.dataframe(res_df, use_container_width=True, hide_index=True)
            else:
                if query_info["chart_type"] == "pie":
                    fig = px.pie(
                        res_df, 
                        names=query_info["names"], 
                        values=query_info["values"], 
                        title=f"{title} - Pie Chart"
                    )
                else:
                    fig = px.bar(
                        res_df, 
                        x=query_info["x"], 
                        y=query_info["y"], 
                        color=query_info["color"],
                        title=f"{title} - Bar Chart"
                    )
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

    st.subheader("✍️ Run Custom SQL Query")
    
    custom_query = st.text_area(
        "Enter your SQL query below (table name is `df`):", 
        value="SELECT City, AVG(Delivery_Time_Min) AS Avg_Delivery FROM df GROUP BY City ORDER BY Avg_Delivery ASC;", 
        height=120
    )

    if st.button("🚀 Run Custom Query", use_container_width=True):
        try:
            custom_res = pd.read_sql_query(custom_query, conn)
            st.success(f"Execution Successful! ({custom_res.shape[0]} rows returned)")
            display_table_view(custom_res, title="📋 Custom Query Results Table", filename="custom_query_results.csv")
        except Exception as err:
            st.error(f"❌ SQL Execution Error: {err}")
