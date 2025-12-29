import streamlit as st
import pandas as pd
import os
from transformers import pipeline

# 1. AI BRAINS: Loading high-accuracy model for English sentiment
@st.cache_resource
def load_sentiment_model():
    # RoBERTa is more accurate for social media/web review styles
    return pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")

# 2. CACHING: Ensuring switching filters is instant after first calculation
@st.cache_data
def analyze_sentiment(df):
    model = load_sentiment_model()
    # Processing the 'Vsebina' column from your reviews.csv
    results = model(df['Vsebina'].tolist(), truncation=True)
    
    # Adding results to the dataframe
    df['label'] = [r['label'].upper() for r in results]
    df['score'] = [round(r['score'], 3) for r in results]
    return df

# Page Setup
st.set_page_config(page_title="Brand Monitor AI Dashboard", layout="wide")

# Helper function to load CSVs from the 'data' folder
def load_data(file_name):
    path = os.path.join("data", file_name)
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

# --- SIDEBAR (Navigation) ---
st.sidebar.title("🔍 Brand Monitor")
choice = st.sidebar.radio("Navigation:", ["Products", "Testimonials", "Reviews Analysis"])

# --- TAB 1: PRODUCTS ---
if choice == "Products":
    st.header("📦 Product Overview")
    df = load_data("products.csv") #
    if df is not None:
        # Scrollable table for easy navigation
        st.dataframe(df, use_container_width=True, height=600)
    else:
        st.error("File 'data/products.csv' not found.")

# --- TAB 2: TESTIMONIALS ---
elif choice == "Testimonials":
    st.header("💬 Customer Testimonials")
    df = load_data("testimonials.csv") #
    if df is not None:
        # Now scrollable instead of a static table
        st.dataframe(df, use_container_width=True, height=600)
    else:
        st.error("File 'data/testimonials.csv' not found.")

# --- TAB 3: REVIEWS ANALYSIS (The AI Part) ---
elif choice == "Reviews Analysis":
    st.header("⭐ AI Sentiment Analysis")
    df = load_data("reviews.csv") #
    
    if df is not None:
        # Data preparation
        df['Datum'] = pd.to_datetime(df['Datum'])
        df['Year'] = df['Datum'].dt.year
        
        # Filtering Controls
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            years = ["All"] + sorted(df['Year'].unique().tolist(), reverse=True)
            selected_year = st.selectbox("Select Year:", options=years)
        
        if selected_year == "All":
            df_filtered = df.copy()
        else:
            df_filtered = df[df['Year'] == selected_year].copy()
            with col_f2:
                months = ["January", "February", "March", "April", "May", "June", 
                          "July", "August", "September", "October", "November", "December"]
                selected_month = st.select_slider("Select Month:", options=months)
                month_num = months.index(selected_month) + 1
                df_filtered = df_filtered[df_filtered['Datum'].dt.month == month_num].copy()

        # Display Section
        if not df_filtered.empty:
            with st.spinner('AI is analyzing feedback...'):
                processed_df = analyze_sentiment(df_filtered)
            
            # --- WIDE TABLE LAYOUT ---
            # Ratio 1 to 4: Narrow chart, Wide table
            stats_col, table_col = st.columns([1, 4])
            
            with stats_col:
                st.subheader("Stats")
                st.metric("Avg Confidence", f"{processed_df['score'].mean():.2%}")
                # Narrow bar chart
                sentiment_counts = processed_df['label'].value_counts()
                st.bar_chart(sentiment_counts)
            
            with table_col:
                st.subheader("Detailed Review List")
                
                # High-contrast color styling
                def apply_styles(val):
                    if val == 'POSITIVE': 
                        return 'background-color: #28a745; color: white; font-weight: bold;' # Vibrant Green
                    elif val == 'NEGATIVE': 
                        return 'background-color: #dc3545; color: white; font-weight: bold;' # Vibrant Red
                    return 'background-color: #ffc107; color: black; font-weight: bold;' # Vibrant Yellow
                
                st.dataframe(
                    processed_df.style.applymap(apply_styles, subset=['label']), 
                    use_container_width=True,
                    height=550
                )
        else:
            st.info("No reviews available for the selected period.")
    else:
        st.error("File 'data/reviews.csv' not found.")