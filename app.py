import streamlit as st
import pandas as pd
import os

# Konfiguracija strani za širok prikaz
st.set_page_config(page_title="Brand Monitor AI", layout="wide")

# Funkcija za varno nalaganje podatkov iz mape data/
def load_data(file_name):
    path = os.path.join('data', file_name)
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

# Nalaganje vseh potrebnih datotek
products_df = load_data('products.csv')
testimonials_df = load_data('testimonials.csv')
reviews_df = load_data('reviews_analyzed.csv')

# Stranski meni za navigacijo
st.sidebar.title("🔍 Brand Monitor")
navigation = st.sidebar.radio("Navigation:", ["Products", "Testimonials", "Reviews Analysis"])

# 1. SEKCIJA: PRODUCTS
if navigation == "Products":
    st.header("📦 Product List")
    if not products_df.empty:
        # Prikaz v tabeli s scrollbarom
        st.dataframe(products_df, use_container_width=True, height=600)
    else:
        st.warning("Products data not found in data/products.csv")

# 2. SEKCIJA: TESTIMONIALS
elif navigation == "Testimonials":
    st.header("💬 Customer Testimonials")
    if not testimonials_df.empty:
        # Prikaz v pregledni tabeli, ki omogoča scrollanje
        st.dataframe(testimonials_df, use_container_width=True, height=600)
    else:
        st.warning("Testimonials data not found in data/testimonials.csv")

# 3. SEKCIJA: REVIEWS ANALYSIS
elif navigation == "Reviews Analysis":
    st.header("📊 Sentiment Analysis Dashboard")
    
    if not reviews_df.empty:
        # Priprava datumskih stolpcev
        reviews_df['Datum'] = pd.to_datetime(reviews_df['Datum'])
        reviews_df['Year'] = reviews_df['Datum'].dt.year
        reviews_df['Month'] = reviews_df['Datum'].dt.month
        
        # Vrstica s filtri
        col_y, col_ch, col_m = st.columns([2, 1, 2])
        with col_y:
            years = ["All"] + sorted(reviews_df['Year'].unique().tolist(), reverse=True)
            sel_year = st.selectbox("Select Year:", years)
        
        with col_ch:
            # Checkbox za aktivacijo mesečnega filtra
            use_month = st.checkbox("Filter by Month?", value=False)
            
        with col_m:
            month_names = ["January", "February", "March", "April", "May", "June", 
                           "July", "August", "September", "October", "November", "December"]
            sel_month_idx = st.select_slider("Select Month:", options=range(1, 13), 
                                            format_func=lambda x: month_names[x-1], 
                                            disabled=not use_month)

        # Logika filtriranja podatkov
        filtered_df = reviews_df.copy()
        
        if sel_year != "All":
            filtered_df = filtered_df[filtered_df['Year'] == int(sel_year)]
        
        if use_month:
            filtered_df = filtered_df[filtered_df['Month'] == sel_month_idx]

        # Prikaz rezultatov analize
        if not filtered_df.empty:
            # Vizualna razporeditev: ožji graf (1) in zelo široka tabela (4)
            c1, c2 = st.columns([1, 4]) 
            
            with c1:
                st.subheader("Stats")
                st.metric("Avg Confidence", f"{filtered_df['score'].mean()*100:.2f}%")
                
                # Priprava podatkov za graf brez barvnih napak
                sentiment_counts = filtered_df['label'].value_counts().reset_index()
                sentiment_counts.columns = ['label', 'count']
                
                # Izris grafa z avtomatskimi barvami glede na labelo
                st.bar_chart(data=sentiment_counts, x='label', y='count', color='label')

            with c2:
                st.subheader("Review Details")
                # Funkcija za barvno označevanje celic v tabeli
                def style_sentiment(val):
                    color = '#28a745' if val == 'POSITIVE' else '#dc3545'
                    return f'background-color: {color}; color: white; font-weight: bold'
                
                # Prikaz razširjene tabele z barvnimi oznakami
                st.dataframe(filtered_df.style.applymap(style_sentiment, subset=['label']), 
                             use_container_width=True, height=600)
        else:
            st.info("No data found for this selection. Try adjusting the filters.")
    else:
        st.error("Analyzed reviews file not found in data/reviews_analyzed.csv!")