import os
import warnings
import zipfile
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st

warnings.filterwarnings("ignore")

# Define SSL CA Certificate Path
CA_PATH = "isrgrootx1.pem"  # Replace with your actual file name
os.environ["SSL_CERT_FILE"] = CA_PATH
os.environ["REQUESTS_CA_BUNDLE"] = CA_PATH

# Set page config
st.set_page_config(
    page_title="Food Delivery Analytics",
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# ============================================
# LOAD DATA
# ============================================
@st.cache_data
def load_data():
    with zipfile.ZipFile('CLEANED_FOOD_DELIVERY_DATA.zip') as z:
        with z.open('CLEANED_FOOD_DELIVERY_DATA.csv') as f:
            df = pd.read_csv(f)
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], errors='coerce')
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ 'CLEANED_FOOD_DELIVERY_DATA.zip' not found. Please ensure the dataset zip file is in the repository.")
    st.stop()

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
     "💡 Business Insights"]
)

st.sidebar.markdown("---")
st.sidebar.info("""
### 📋 Dataset Info
- **Total Orders**: {:,}
- **Total Customers**: {:,}
- **Total Restaurants**: {:,}
- **Delivery Partners**: {:,}
""".format(
    df['Order_ID'].nunique(),
    df['Customer_ID'].nunique(),
    df['Restaurant_ID'].nunique(),
    df['Delivery_Partner_ID'].nunique()
))

# ============================================
# PAGE 1: DASHBOARD OVERVIEW
# ============================================
if page == "📊 Dashboard Overview":
    st.title("🍕 Online Food Delivery Analytics Dashboard")
    st.markdown("---")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Orders",
            f"{len(df):,}",
            delta="100%",
            delta_color="off"
        )
    
    with col2:
        st.metric(
            "Avg Order Value",
            f"₹{df['Order_Value'].mean():.0f}",
            delta=f"Median: ₹{df['Order_Value'].median():.0f}",
            delta_color="off"
        )
    
    with col3:
        st.metric(
            "Avg Delivery Time",
            f"{df['Delivery_Time_Min'].mean():.0f} min",
            delta=f"Max: {df['Delivery_Time_Min'].max():.0f} min",
            delta_color="off"
        )
    
    with col4:
        cancel_rate = (df['Order_Status'] == 'Cancelled').mean() * 100
        st.metric(
            "Cancellation Rate",
            f"{cancel_rate:.1f}%",
            delta=f"{(df['Order_Status'] == 'Delivered').sum():,} Delivered",
            delta_color="normal"
        )
    
    st.markdown("---")
    
    # Summary Stats
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
        ax.hist(df['Order_Value'].dropna(), bins=50,
                color='steelblue', edgecolor='white', alpha=0.8)
        ax.axvline(df['Order_Value'].mean(), color='red',
                   linestyle='--', linewidth=2, label=f"Mean: ₹{df['Order_Value'].mean():.0f}")
        ax.axvline(df['Order_Value'].median(), color='green',
                   linestyle='--', linewidth=2, label=f"Median: ₹{df['Order_Value'].median():.0f}")
        ax.set_xlabel('Order Value (₹)')
        ax.set_ylabel('Frequency')
        ax.legend()
        st.pyplot(fig)
    
    with col2:
        st.subheader("Delivery Time Distribution")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(df['Delivery_Time_Min'].dropna(), bins=50,
                color='coral', edgecolor='white', alpha=0.8)
        ax.axvline(df['Delivery_Time_Min'].mean(), color='red',
                   linestyle='--', linewidth=2, label=f"Mean: {df['Delivery_Time_Min'].mean():.0f} min")
        ax.axvline(df['Delivery_Time_Min'].median(), color='green',
                   linestyle='--', linewidth=2, label=f"Median: {df['Delivery_Time_Min'].median():.0f} min")
        ax.set_xlabel('Delivery Time (Minutes)')
        ax.set_ylabel('Frequency')
        ax.legend()
        st.pyplot(fig)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Final Amount Distribution")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(df['Final_Amount'].dropna(), bins=50,
                color='mediumseagreen', edgecolor='white', alpha=0.8)
        ax.axvline(df['Final_Amount'].mean(), color='red',
                   linestyle='--', linewidth=2, label=f"Mean: ₹{df['Final_Amount'].mean():.0f}")
        ax.set_xlabel('Final Amount (₹)')
        ax.set_ylabel('Frequency')
        ax.legend()
        st.pyplot(fig)
    
    with col2:
        st.subheader("Profit Margin Distribution")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(df['Profit_Margin'].dropna(), bins=50,
                color='mediumpurple', edgecolor='white', alpha=0.8)
        ax.axvline(df['Profit_Margin'].mean(), color='red',
                   linestyle='--', linewidth=2, label=f"Mean: {df['Profit_Margin'].mean():.2f}")
        ax.axvline(0, color='black', linestyle='-', linewidth=2, label='Break-Even')
        ax.set_xlabel('Profit Margin')
        ax.set_ylabel('Frequency')
        ax.legend()
        st.pyplot(fig)

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
        fig = px.bar(city_orders, 
                     x=city_orders.index, 
                     y=city_orders.values,
                     labels={'x': 'City', 'y': 'Orders'},
                     color=city_orders.values,
                     color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Orders by Cuisine")
        cuisine_orders = df['Cuisine_Type'].value_counts()
        fig = px.bar(cuisine_orders, 
                     x=cuisine_orders.index, 
                     y=cuisine_orders.values,
                     labels={'x': 'Cuisine', 'y': 'Orders'},
                     color=cuisine_orders.values,
                     color_continuous_scale='Greens')
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.subheader("Avg Rating by Cuisine")
        cuisine_rating = df.groupby('Cuisine_Type')['Restaurant_Rating'].mean().sort_values(ascending=False)
        fig = px.bar(cuisine_rating,
                     x=cuisine_rating.index,
                     y=cuisine_rating.values,
                     labels={'x': 'Cuisine', 'y': 'Rating'},
                     color=cuisine_rating.values,
                     color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("City vs Cuisine Heatmap")
    city_cuisine = pd.crosstab(df['City'], df['Cuisine_Type'])
    fig = px.imshow(city_cuisine, labels=dict(x="Cuisine", y="City", color="Orders"),
                    color_continuous_scale="YlOrRd")
    st.plotly_chart(fig, use_container_width=True)

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
        fig = px.pie(day_orders, 
                     names=day_orders.index, 
                     values=day_orders.values,
                     title="Orders: Weekend vs Weekday")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Avg Order Value")
        day_value = df.groupby('Order_Day')['Order_Value'].mean()
        fig = px.bar(day_value,
                     x=day_value.index,
                     y=day_value.values,
                     labels={'x': 'Day', 'y': 'Avg Value (₹)'},
                     color=day_value.values,
                     color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.subheader("Avg Delivery Time")
        day_delivery = df.groupby('Order_Day')['Delivery_Time_Min'].mean()
        fig = px.bar(day_delivery,
                     x=day_delivery.index,
                     y=day_delivery.values,
                     labels={'x': 'Day', 'y': 'Avg Time (min)'},
                     color=day_delivery.values,
                     color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        st.subheader("Cancellation Rate")
        cancel_day = df.groupby('Order_Day').apply(
            lambda x: (x['Order_Status'] == 'Cancelled').mean() * 100)
        fig = px.bar(cancel_day,
                     x=cancel_day.index,
                     y=cancel_day.values,
                     labels={'x': 'Day', 'y': 'Cancel Rate (%)'},
                     color=cancel_day.values,
                     color_continuous_scale='Oranges')
        st.plotly_chart(fig, use_container_width=True)

# ============================================
# PAGE 5: DISTANCE & DELIVERY
# ============================================
elif page == "🚗 Distance & Delivery":
    st.title("🚗 Distance vs Delivery Delay Relationship")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distance vs Delivery Time (Scatter)")
        sample_df = df.sample(min(2000, len(df)), random_state=42)
        fig = px.scatter(sample_df, 
                         x='Distance_km', 
                         y='Delivery_Time_Min',
                         opacity=0.5,
                         title="Distance vs Delivery Time")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Delivery Time by Distance Range")
        df['Distance_Bin'] = pd.cut(df['Distance_km'],
                                    bins=[0, 5, 10, 15, 20, 30, 40],
                                    labels=['0-5km', '5-10km', '10-15km',
                                            '15-20km', '20-30km', '30-40km'])
        dist_delivery = df.groupby('Distance_Bin')['Delivery_Time_Min'].mean()
        fig = px.bar(dist_delivery,
                     x=dist_delivery.index,
                     y=dist_delivery.values,
                     labels={'x': 'Distance Range', 'y': 'Avg Delivery (min)'},
                     color=dist_delivery.values,
                     color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)

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
        fig = px.pie(cancel_reasons,
                     names=cancel_reasons.index,
                     values=cancel_reasons.values,
                     title="Why Orders Were Cancelled")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Cancellation Rate by City")
        cancel_city = cancelled_df.groupby('City').size()
        total_city = df.groupby('City').size()
        cancel_rate_city = (cancel_city / total_city * 100).sort_values(ascending=False)
        fig = px.bar(cancel_rate_city,
                     x=cancel_rate_city.index,
                     y=cancel_rate_city.values,
                     labels={'x': 'City', 'y': 'Cancellation Rate (%)'},
                     color=cancel_rate_city.values,
                     color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cancellation Rate by Cuisine")
        cancel_cuisine = cancelled_df.groupby('Cuisine_Type').size()
        total_cuisine = df.groupby('Cuisine_Type').size()
        cancel_rate_cuisine = (cancel_cuisine / total_cuisine * 100).sort_values(ascending=False)
        fig = px.bar(cancel_rate_cuisine,
                     x=cancel_rate_cuisine.index,
                     y=cancel_rate_cuisine.values,
                     labels={'x': 'Cuisine', 'y': 'Cancellation Rate (%)'},
                     color=cancel_rate_cuisine.values,
                     color_continuous_scale='Oranges')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Cancellation Rate by Payment Mode")
        cancel_payment = cancelled_df.groupby('Payment_Mode').size()
        total_payment = df.groupby('Payment_Mode').size()
        cancel_rate_payment = (cancel_payment / total_payment * 100).sort_values(ascending=False)
        fig = px.bar(cancel_rate_payment,
                     x=cancel_rate_payment.index,
                     y=cancel_rate_payment.values,
                     labels={'x': 'Payment Mode', 'y': 'Cancellation Rate (%)'},
                     color=cancel_rate_payment.values,
                     color_continuous_scale='Purples')
        st.plotly_chart(fig, use_container_width=True)

# ============================================
# PAGE 7: CORRELATIONS
# ============================================
elif page == "📉 Correlations":
    st.title("📉 Correlation Analysis")
    st.markdown("---")
    
    numeric_cols = ['Customer_Age', 'Delivery_Time_Min', 'Distance_km',
                    'Order_Value', 'Discount_Applied', 'Final_Amount',
                    'Delivery_Rating', 'Restaurant_Rating',
                    'Peak_Hour', 'Profit_Margin']
    
    corr_matrix = df[numeric_cols].corr()
    
    st.subheader("Correlation Heatmap")
    fig = px.imshow(corr_matrix,
                    labels=dict(color="Correlation"),
                    color_continuous_scale="RdYlGn",
                    zmin=-1, zmax=1,
                    text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

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
        1. **Order Volume**: {len(df):,} total orders processed
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
    
    st.markdown("---")
    st.subheader("🚀 Recommendations")
    st.write("""
    1. **Reduce Cancellations**: Focus on late delivery and restaurant issues (top 2 reasons)
    2. **Optimize Delivery**: Improve performance for long-distance deliveries (>20km)
    3. **Profitability**: Review pricing strategy for loss-making orders (27.7% of orders)
    4. **Peak Hours**: Increase delivery capacity during peak hours
    5. **City Strategy**: Scale operations in high-performing cities
    6. **Cuisine Focus**: Promote high-rated cuisines and low-rated restaurants
    7. **Payment Options**: Encourage COD (highest cancellation) to move to digital payments
    8. **Weekend Strategy**: Capitalize on weekend demand with promotional offers
    """)
