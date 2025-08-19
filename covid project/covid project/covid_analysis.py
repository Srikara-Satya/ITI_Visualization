import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import plotly.io as pio

pio.renderers.default = 'browser'  # ✅ Force Plotly to open graphs in browser

# ========== Load COVID-19 data ==========
print("Loading COVID-19 dataset...")
df = pd.read_csv("C:\project\covid project\covid project\owid-covid-data.csv")

# ========== Preprocessing ==========
df = df[['location', 'date', 'total_cases', 'new_cases', 'total_deaths', 'new_deaths',
         'total_vaccinations', 'people_vaccinated', 'people_fully_vaccinated',
         'continent', 'iso_code']]
df['date'] = pd.to_datetime(df['date'])
df = df[df['continent'].notna()]  # Remove aggregates (e.g., World)
df.fillna(0, inplace=True)

print("Data shape:", df.shape)
print("Date range:", df['date'].min(), "to", df['date'].max())

# ========== Global Daily Line Plot ==========
global_daily = df.groupby('date')[['new_cases', 'new_deaths']].sum().reset_index()
fig1 = px.line(global_daily, x='date', y=['new_cases', 'new_deaths'],
               title='🌍 Global COVID-19: Daily New Cases and Deaths')
fig1.show()

# ========== Latest Valid Snapshot ==========
latest_per_country = df[df['total_cases'] > 0].groupby('location')['date'].max().reset_index()
latest = df.merge(latest_per_country, on=['location', 'date'], how='inner')
latest = latest[latest['total_cases'] > 0]
print("Latest valid country data:", latest.shape)

# ========== Top 10 Countries Bar Chart ==========
top10 = latest.sort_values('total_cases', ascending=False).head(10)
fig2 = px.bar(top10, x='location', y='total_cases', color='location',
              title='🏆 Top 10 Countries by Total COVID-19 Cases')
fig2.show()

# ========== Scatter Plot: Cases vs Deaths ==========
fig3 = px.scatter(latest, x='total_cases', y='total_deaths', size='total_cases',
                  color='continent', hover_name='location', log_x=True,
                  title='⚖️ Total Cases vs Total Deaths by Country')
fig3.show()

# ========== Choropleth Map: Total Cases ==========
fig4 = px.choropleth(latest, locations='iso_code', color='total_cases',
                     hover_name='location', color_continuous_scale='Reds',
                     title='🗺️ Total COVID-19 Cases (Global Map)')
fig4.show()

# ========== Bubble Chart: Vaccination ==========
vacc_data = latest[
    (latest['people_vaccinated'] > 0) &
    (latest['people_fully_vaccinated'] > 0) &
    (latest['total_vaccinations'] > 0)
]
print("Countries with vaccination data:", vacc_data.shape[0])

fig5 = px.scatter(vacc_data, x='people_vaccinated', y='people_fully_vaccinated',
                  size='total_vaccinations', color='continent', hover_name='location',
                  title='💉 Vaccination Status by Country')
fig5.show()

# ========== Word Cloud: Total Cases by Country ==========
word_freq = dict(zip(latest['location'], latest['total_cases']))
wordcloud = WordCloud(width=1000, height=500, background_color='white').generate_from_frequencies(word_freq)
plt.figure(figsize=(15, 7))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('☁️ COVID-19 Cases WordCloud by Country')
plt.show()

# ========== Country-Specific Trend (India) ==========
country = 'India'
india_df = df[df['location'] == country]
fig6 = px.line(india_df, x='date', y=['new_cases', 'new_deaths'],
               title=f'📉 {country}: Daily New Cases and Deaths')
fig6.show()