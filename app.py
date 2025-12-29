import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Brand Monitor AI", layout="wide")

# Funkcija za varno nalaganje podatkov
def load_data(file_name):
    path = os.path.join('data', file_name)
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

# Nalaganje vseh potrebnih datotek
products_df = load_data('products.csv')
testimonials_df = load_data('testimonials.csv')
reviews_df = load_data('reviews_analyzed.csv')

st.sidebar.title("🔍 Brand Monitor")
navigation = st.sidebar.radio("Navigation:", ["Products", "Testimonials", "Reviews Analysis"])

# 1. PRODUCTS (Popravljen prikaz)
if navigation == "Products":
    st.header("📦 Product List")
    if not products_df.empty:
        st.dataframe(products_df, use_container_width=True)
    else:
        st.warning("Products data not found in data/products.csv")

# 2. TESTIMONIALS (Popravljen prikaz)
elif navigation == "Testimonials":
    st.header("💬 Customer Testimonials")
    if not testimonials_df.empty:
        st.table(testimonials_df)
    else:
        st.warning("Testimonials data not found in data/testimonials.csv")

# 3. REVIEWS ANALYSIS (Dodane barve, slider in stilizacija)
elif navigation == "Reviews Analysis":
    st.header("📊 Sentiment Analysis Dashboard")
    
    if not reviews_df.empty:
        reviews_df['Datum'] = pd.to_datetime(reviews_df['Datum'])
        reviews_df['Year'] = reviews_df['Datum'].dt.year
        
        col1, col2 = st.columns(2)
        with col1:
            years = ["All"] + sorted(reviews_df['Year'].unique().tolist(), reverse=True)
            sel_year = st.selectbox("Select Year:", years)
        with col2:
            # Slider za mesece (zahteva profesorja)
            month_names = ["January", "February", "March", "April", "May", "June", 
                           "July", "August", "September", "October", "November", "December"]
            sel_month_idx = st.select_slider("Select Month:", options=range(1, 13), format_func=lambda x: month_names[x-1])

        # Filtriranje
        if sel_year == "All":
            filtered_df = reviews_df.copy()
        else:
            filtered_df = reviews_df[(reviews_df['Year'] == int(sel_year)) & (reviews_df['Datum'].dt.month == sel_month_idx)].copy()

        if not filtered_df.empty:
            c1, c2 = st.columns([1, 2])
            with c1:
                st.subheader("Stats")
                st.metric("Avg Confidence", f"{filtered_df['score'].mean()*100:.2f}%")
                
                # Barvni graf (Zelena za Positive, Rdeča za Negative)
                sentiment_counts = filtered_df['label'].value_counts()
                colors = {'POSITIVE': '#28a745', 'NEGATIVE': '#dc3545'}
                # Ustvarimo seznam barv glede na prisotne labele v counts
                current_colors = [colors.get(x, '#808080') for x in sentiment_counts.index]
                st.bar_chart(sentiment_counts, color=current_colors)

            with c2:
                st.subheader("Review Details")
                # Funkcija za barvno označevanje celic v tabeli
                def style_sentiment(val):
                    color = '#28a745' if val == 'POSITIVE' else '#dc3545'
                    return f'background-color: {color}; color: white; font-weight: bold'
                
                # Prikaz stilizirane tabele
                st.dataframe(filtered_df.style.applymap(style_sentiment, subset=['label']), use_container_width=True)
        else:
            st.info(f"No reviews found for {month_names[sel_month_idx-1]} {sel_year}.")
    else:
        st.error("Analyzed reviews file not found!")