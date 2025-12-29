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

# Nalaganje podatkov
products_df = load_data('products.csv')
testimonials_df = load_data('testimonials.csv')
reviews_df = load_data('reviews_analyzed.csv')

st.sidebar.title("🔍 Brand Monitor")
navigation = st.sidebar.radio("Navigation:", ["Products", "Testimonials", "Reviews Analysis"])

if navigation == "Products":
    st.header("📦 Product List")
    if not products_df.empty:
        st.dataframe(products_df, use_container_width=True, height=500)

elif navigation == "Testimonials":
    st.header("💬 Customer Testimonials")
    if not testimonials_df.empty:
        st.dataframe(testimonials_df, use_container_width=True, height=500)

elif navigation == "Reviews Analysis":
    st.header("📊 Sentiment Analysis Dashboard")
    
    if not reviews_df.empty:
        # Pretvori datume in pripravi stolpce za filtriranje
        reviews_df['Datum'] = pd.to_datetime(reviews_df['Datum'])
        reviews_df['Year'] = reviews_df['Datum'].dt.year
        reviews_df['Month'] = reviews_df['Datum'].dt.month
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            years = ["All"] + sorted(reviews_df['Year'].unique().tolist(), reverse=True)
            sel_year = st.selectbox("Select Year:", years)
        
        with col2:
            use_month = st.checkbox("Filter by Month?", value=False)
            
        with col3:
            month_names = ["January", "February", "March", "April", "May", "June", 
                           "July", "August", "September", "October", "November", "December"]
            sel_month_idx = st.select_slider("Select Month:", options=range(1, 13), 
                                            format_func=lambda x: month_names[x-1], 
                                            disabled=not use_month)

        # LOGIKA FILTRIRANJA (Popravljena za "All")
        filtered_df = reviews_df.copy()
        
        if sel_year != "All":
            filtered_df = filtered_df[filtered_df['Year'] == int(sel_year)]
        
        if use_month:
            filtered_df = filtered_df[filtered_df['Month'] == sel_month_idx]

        if not filtered_df.empty:
            c1, c2 = st.columns([1, 2])
            with c1:
                st.subheader("Stats")
                st.metric("Avg Confidence", f"{filtered_df['score'].mean()*100:.2f}%")
                
                # POPRAVEK GRAFA: Uporaba barvnega seznama, ki ustreza dejanskim podatkom
                sentiment_counts = filtered_df['label'].value_counts().reset_index()
                sentiment_counts.columns = ['label', 'count']
                
                # Definiramo barve ročno za bar_chart
                st.bar_chart(data=sentiment_counts, x='label', y='count', color='label')

            with c2:
                st.subheader("Review Details")
                def style_sentiment(val):
                    color = '#28a745' if val == 'POSITIVE' else '#dc3545'
                    return f'background-color: {color}; color: white; font-weight: bold'
                
                st.dataframe(filtered_df.style.applymap(style_sentiment, subset=['label']), 
                             use_container_width=True, height=500)
        else:
            st.info("No data found for this selection. Try adjusting the year or month filter.")