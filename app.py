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

# 1. PRODUCTS - Pregledna tabela s scrollbarom
if navigation == "Products":
    st.header("📦 Product List")
    if not products_df.empty:
        # st.dataframe samodejno doda scrollbar, če je podatkov veliko
        st.dataframe(products_df, use_container_width=True, height=500)
    else:
        st.warning("Products data not found.")

# 2. TESTIMONIALS - Zdaj v obliki pregledne tabele kot pri produktih
elif navigation == "Testimonials":
    st.header("💬 Customer Testimonials")
    if not testimonials_df.empty:
        # Spremenjeno iz st.table v st.dataframe za boljšo preglednost in scroll
        st.dataframe(testimonials_df, use_container_width=True, height=500)
    else:
        st.warning("Testimonials data not found.")

# 3. REVIEWS ANALYSIS - Popravljene barve in opcijski mesečni filter
elif navigation == "Reviews Analysis":
    st.header("📊 Sentiment Analysis Dashboard")
    
    if not reviews_df.empty:
        reviews_df['Datum'] = pd.to_datetime(reviews_df['Datum'])
        reviews_df['Year'] = reviews_df['Datum'].dt.year
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            years = ["All"] + sorted(reviews_df['Year'].unique().tolist(), reverse=True)
            sel_year = st.selectbox("Select Year:", years)
        
        with col2:
            # Checkbox za aktivacijo mesečnega filtra
            use_month = st.checkbox("Filter by Month?")
            
        with col3:
            month_names = ["January", "February", "March", "April", "May", "June", 
                           "July", "August", "September", "October", "November", "December"]
            sel_month_idx = st.select_slider("Select Month:", options=range(1, 13), 
                                            format_func=lambda x: month_names[x-1], 
                                            disabled=not use_month)

        # Logika filtriranja
        filtered_df = reviews_df.copy()
        if sel_year != "All":
            filtered_df = filtered_df[filtered_df['Year'] == int(sel_year)]
        
        if use_month:
            filtered_df = filtered_df[filtered_df['Datum'].dt.month == sel_month_idx]

        if not filtered_df.empty:
            c1, c2 = st.columns([1, 2])
            with c1:
                st.subheader("Stats")
                st.metric("Avg Confidence", f"{filtered_df['score'].mean()*100:.2f}%")
                
                # POPRAVEK BARV: Dinamično določanje barv za graf
                sentiment_counts = filtered_df['label'].value_counts()
                # Ustvarimo barvno mapo, ki se prilagodi številu stolpcev
                chart_colors = []
                for label in sentiment_counts.index:
                    if label == 'POSITIVE': chart_colors.append('#28a745')
                    elif label == 'NEGATIVE': chart_colors.append('#dc3545')
                    else: chart_colors.append('#808080')
                
                st.bar_chart(sentiment_counts, color=chart_colors)

            with c2:
                st.subheader("Review Details")
                def style_sentiment(val):
                    color = '#28a745' if val == 'POSITIVE' else '#dc3545'
                    return f'background-color: {color}; color: white; font-weight: bold'
                
                st.dataframe(filtered_df.style.applymap(style_sentiment, subset=['label']), use_container_width=True, height=500)
        else:
            st.info("No data found for this selection.")