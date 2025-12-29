import pandas as pd
from transformers import pipeline

# Naloži podatke
df = pd.read_csv('data/reviews.csv')

# Naloži model (lokalno imaš dovolj RAM-a)
model = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Izvedi analizo
print("Analiziram sentiment... počakaj trenutek.")
results = model(df['Vsebina'].tolist())

# Dodaj rezultate v tabelo
df['label'] = [res['label'] for res in results]
df['score'] = [res['score'] for res in results]

# Shrani v novo datoteko
df.to_csv('data/reviews_analyzed.csv', index=False)
print("Končano! Ustvarjena je datoteka data/reviews_analyzed.csv")