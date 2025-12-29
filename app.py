import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Brand Monitor AI", layout="wide")

# Naložimo že ANALIZIRANE podatke
def load_data():
    path = 'data/reviews_analyzed.csv'
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

reviews_df = load_data()

st.sidebar.title("🔍 Brand Monitor")
navigation = st.sidebar.radio("Navigation:", ["Products", "Testimonials", "Reviews Analysis"])

if navigation == "Reviews Analysis":
    st.header("📊 Sentiment Analysis Dashboard")
    
    if not reviews_df.empty:
        reviews_df['Datum'] = pd.to_datetime(reviews_df['Datum'])
        reviews_df['Year'] = reviews_df['Datum'].dt.year
        
        # Filtri (ostanejo popolnoma isti kot prej)
        years_list = ["All"] + sorted(reviews_df['Year'].unique().tolist(), reverse=True)
        selected_year = st.selectbox("Select Year:", years_list)
        
        # Filtriranje
        if selected_year == "All":
            filtered_df = reviews_df
        else:
            filtered_df = reviews_df[reviews_df['Year'] == int(selected_year)]

        # Prikaz grafov in tabel (deluje takoj, brez čakanja!)
        c1, c2 = st.columns([1, 3])
        with c1:
            st.metric("Avg Confidence", f"{filtered_df['score'].mean()*100:.2f}%")
            st.bar_chart(filtered_df['label'].value_counts())
        with c2:
            st.dataframe(filtered_df, use_container_width=True)