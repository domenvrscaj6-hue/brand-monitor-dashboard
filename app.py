import streamlit as st
import pandas as pd
from transformers import pipeline
import os

# Konfiguracija strani
st.set_page_config(page_title="Brand Monitor AI", layout="wide")

# Funkcija za varno nalaganje podatkov
def load_data(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        st.error(f"Datoteka {file_path} ni bila najdena na GitHubu!")
        return pd.DataFrame()

# Naloži podatke iz mape data/
products_df = load_data('data/products.csv')
testimonials_df = load_data('data/testimonials.csv')
reviews_df = load_data('data/reviews.csv')

# Optimiziran AI model (DistilBERT je lažji za Render Free tier)
@st.cache_resource
def load_sentiment_model():
    return pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

sentiment_pipeline = load_sentiment_model()

# Stranski meni (Sidebar)
st.sidebar.title("🔍 Brand Monitor")
navigation = st.sidebar.radio("Navigation:", ["Products", "Testimonials", "Reviews Analysis"])

# 1. SEKCIJA: PRODUCTS
if navigation == "Products":
    st.header("📦 Product List")
    if not products_df.empty:
        st.dataframe(products_df, use_container_width=True)
    else:
        st.warning("Seznam produktov je prazen.")

# 2. SEKCIJA: TESTIMONIALS
elif navigation == "Testimonials":
    st.header("💬 Customer Testimonials")
    if not testimonials_df.empty:
        st.table(testimonials_df)
    else:
        st.warning("Ni podatkov o pričevanjih.")

# 3. SEKCIJA: REVIEWS ANALYSIS
elif navigation == "Reviews Analysis":
    st.header("📊 Sentiment Analysis Dashboard")
    
    if not reviews_df.empty:
        # Pretvori datume in filtriraj za leto 2023
        reviews_df['Datum'] = pd.to_datetime(reviews_df['Datum'])
        reviews_df['Year'] = reviews_df['Datum'].dt.year
        
        # Filtri (Year in Month slider)
        col1, col2 = st.columns(2)
        with col1:
            selected_year = st.selectbox("Select Year:", sorted(reviews_df['Year'].unique(), reverse=True))
        with col2:
            month_names = ["January", "February", "March", "April", "May", "June", 
                           "July", "August", "September", "October", "November", "December"]
            selected_month_idx = st.select_slider("Select Month:", options=range(1, 13), format_func=lambda x: month_names[x-1])

        # Filtriranje podatkov
        filtered_df = reviews_df[(reviews_df['Year'] == selected_year) & (reviews_df['Datum'].dt.month == selected_month_idx)].copy()

        if not filtered_df.empty:
            # Izvedi AI analizo na filtriranih podatkih
            results = sentiment_pipeline(filtered_df['Vsebina'].tolist())
            filtered_df['label'] = [res['label'] for res in results]
            filtered_df['score'] = [res['score'] for res in results]

            # Prikaz statistike
            c1, c2 = st.columns([1, 3])
            with c1:
                st.subheader("Stats")
                avg_conf = filtered_df['score'].mean() * 100
                st.metric("Avg Confidence", f"{avg_conf:.2f}%")
                
                # Graf sentimenta
                sentiment_counts = filtered_df['label'].value_counts()
                st.bar_chart(sentiment_counts)

            with c2:
                st.subheader("Detailed Review List")
                # Barvno označevanje label (pomožna funkcija)
                def color_sentiment(val):
                    color = '#28a745' if val == 'POSITIVE' else '#dc3545'
                    return f'background-color: {color}; color: white; font-weight: bold'

                st.dataframe(filtered_df.style.applymap(color_sentiment, subset=['label']), use_container_width=True)
        else:
            st.info(f"Ni podatkov za izbrano obdobje ({month_names[selected_month_idx-1]} {selected_year}).")
    else:
        st.error("Podatki za analizo ocen niso na voljo.")