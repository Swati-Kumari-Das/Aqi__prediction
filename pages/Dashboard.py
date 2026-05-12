# import streamlit as st
# import pandas as pd
# import seaborn as sns
# import matplotlib.pyplot as plt

# st.markdown("""
# <style>
#     [data-testid="stSidebarNav"] ul li:first-child {
#         display: none;
#     }
# </style>
# """, unsafe_allow_html=True)

# # Load the dataset
# data = pd.read_csv('city_day.csv')

# # ❗ removed set_page_config

# # Introduction
# st.title('🏭 Air Quality Dashboard')
# st.write(""" Visualizing Air Pollution Levels in Indian Cities. """)

# # Data cleaning and preprocessing
# data['Date'] = pd.to_datetime(data['Date'])
# data.dropna(subset=['AQI'], inplace=True)


# # Sidebar options
# st.sidebar.title('Study the AQI Patterns')
# display_aqi_by_city = st.sidebar.checkbox('📶 AQI by City ')
# display_aqi_by_year = st.sidebar.checkbox(' 📉 AQI by Year')
# display_aqi_by_bucket = st.sidebar.checkbox('💹 AQI by AQI_Bucket')
# display_pollutants_over_time = st.sidebar.checkbox('📜 Pollutants Over Time',value = True)


# # AQI by City
# if display_aqi_by_city:
#     st.subheader('AQI by City')
#     cities = data['City'].unique()
#     selected_city = st.selectbox('Select a city', cities)
#     city_data = data[data['City'] == selected_city]

#     fig_aqi_city, ax_aqi_city = plt.subplots()
#     sns.barplot(x=city_data['Date'].dt.year, y=city_data['AQI'], ax=ax_aqi_city)
#     ax_aqi_city.set_xlabel('Year')
#     ax_aqi_city.set_ylabel('Average AQI')
#     ax_aqi_city.set_title(f'AQI Trend for {selected_city}')
#     sns.despine(fig=fig_aqi_city)
#     st.pyplot(fig_aqi_city)

#     st.write('Observations:')
#     st.write('- The graph shows the average AQI trend for the selected city over the years.')
#     st.write('- Higher AQI values indicate worse air quality.')
#     st.write('- The trend can help identify if air quality has improved or deteriorated over time in the selected city.')

# # AQI by Year
# if display_aqi_by_year:
#     st.subheader('AQI by Year')
#     years = data['Date'].dt.year.unique()
#     selected_year = st.selectbox('Select a year', years)
#     year_data = data[data['Date'].dt.year == selected_year]

#     fig_aqi_year, ax_aqi_year = plt.subplots()
#     sns.barplot(x=year_data['City'], y=year_data['AQI'], ax=ax_aqi_year)
#     ax_aqi_year.set_xlabel('City')
#     ax_aqi_year.set_ylabel('Average AQI')
#     ax_aqi_year.set_title(f'AQI by City for {selected_year}')
#     plt.xticks(rotation=45)
#     sns.despine(fig=fig_aqi_year)
#     st.pyplot(fig_aqi_year)

#     st.write('Observations:')
#     st.write('- The graph shows the average AQI for different cities in the selected year.')
#     st.write('- It allows comparing air quality across cities for a specific year.')
#     st.write('- Cities with higher bars have worse air quality compared to those with lower bars.')

# # AQI by AQI_Bucket
# if display_aqi_by_bucket:
#     st.subheader('AQI by AQI_Bucket')
#     aqi_buckets = data['AQI_Bucket'].unique()

#     fig_aqi_bucket, ax_aqi_bucket = plt.subplots()
#     sns.countplot(x=data['AQI_Bucket'], ax=ax_aqi_bucket)
#     ax_aqi_bucket.set_xlabel('AQI_Bucket')
#     ax_aqi_bucket.set_ylabel('Count')
#     plt.xticks(rotation=45)
#     sns.despine(fig=fig_aqi_bucket)
#     st.pyplot(fig_aqi_bucket)

#     st.write('Observations:')
#     st.write('- The graph shows the count of AQI values falling into each AQI_Bucket.')
#     st.write('- It provides an overview of the distribution of AQI values across different buckets.')
#     st.write('- Higher counts in the "Poor" or "Very Poor" buckets indicate a higher frequency of poor air quality.')

# # Pollutants Over Time
# if display_pollutants_over_time:
#     st.subheader('Pollutants Over Time')
#     pollutants = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'CO', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene']
#     selected_pollutants = st.multiselect('Select pollutants', pollutants, default=['PM2.5', 'PM10'])

#     cities = data['City'].unique()
#     selected_city = st.selectbox('Select a city', cities, key='pollutant_city')
#     city_data = data[data['City'] == selected_city]

#     fig_pollutants, ax_pollutants = plt.subplots(figsize=(10, 6))
#     for pollutant in selected_pollutants:
#         sns.lineplot(x=city_data['Date'], y=city_data[pollutant], label=pollutant, ax=ax_pollutants)
#     ax_pollutants.set_xlabel('Date')
#     ax_pollutants.set_ylabel('Pollutant Level')
#     ax_pollutants.set_title(f'Pollutants Over Time for {selected_city}')
#     ax_pollutants.legend()
#     sns.despine(fig=fig_pollutants)
#     st.pyplot(fig_pollutants)

#     st.write('Observations:')
#     st.write('- The graph shows the levels of selected pollutants over time for the selected city.')
#     st.write('- It allows monitoring the trends and patterns of pollutant levels.')
#     st.write('- Higher pollutant levels indicate worse air quality.')
#     st.write('- The graph can help identify any seasonal or long-term variations in pollutant levels.')

####################################################################################

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

st.markdown("""
<style>
    [data-testid="stSidebarNav"] ul li:first-child {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Load & clean dataset
# ─────────────────────────────────────────────
@st.cache_data
def load_and_extend_data():
    data = pd.read_csv('city_day.csv')
    data['Date'] = pd.to_datetime(data['Date'])
    data.dropna(subset=['AQI'], inplace=True)

    numeric_cols = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3',
                    'CO', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene', 'AQI']

    cities = data['City'].unique()
    # Generate daily dates from 2021-01-01 to 2025-12-31
    future_dates = pd.date_range(start='2021-01-01', end='2025-12-31', freq='D')
    synthetic_rows = []

    np.random.seed(42)

    for city in cities:
        city_data = data[data['City'] == city].copy()
        city_data['Year'] = city_data['Date'].dt.year
        city_data['DayOfYear'] = city_data['Date'].dt.dayofyear

        yearly = city_data.groupby('Year')[numeric_cols].mean().reset_index()

        if len(yearly) < 2:
            continue

        # Fit linear model per column
        models = {}
        stds = {}
        for col in numeric_cols:
            col_data = yearly[['Year', col]].dropna()
            if len(col_data) < 2:
                models[col] = None
                stds[col] = 0
                continue
            lr = LinearRegression()
            lr.fit(col_data['Year'].values.reshape(-1, 1), col_data[col].values)
            models[col] = lr
            # Capture std of original daily data to mimic noise level
            stds[col] = city_data[col].dropna().std()

        for date in future_dates:
            yr = date.year
            doy = date.dayofyear
            row = {'City': city, 'Date': date, 'is_predicted': True}

            for col in numeric_cols:
                if models[col] is None:
                    row[col] = np.nan
                    continue
                base = models[col].predict([[yr]])[0]
                # Add realistic noise: random spike + seasonal sine wave variation
                noise = np.random.normal(0, stds[col] * 0.6)
                # Occasional spikes (like the real data has)
                if np.random.rand() < 0.05:
                    noise += np.random.uniform(stds[col], stds[col] * 3)
                # Seasonal variation
                seasonal = stds[col] * 0.3 * np.sin(2 * np.pi * doy / 365)
                row[col] = max(base + noise + seasonal, 0)

            # AQI Bucket
            aqi = row.get('AQI', np.nan)
            if pd.isna(aqi):
                row['AQI_Bucket'] = np.nan
            elif aqi <= 50:
                row['AQI_Bucket'] = 'Good'
            elif aqi <= 100:
                row['AQI_Bucket'] = 'Satisfactory'
            elif aqi <= 200:
                row['AQI_Bucket'] = 'Moderate'
            elif aqi <= 300:
                row['AQI_Bucket'] = 'Poor'
            elif aqi <= 400:
                row['AQI_Bucket'] = 'Very Poor'
            else:
                row['AQI_Bucket'] = 'Severe'

            synthetic_rows.append(row)

    data['is_predicted'] = False
    synthetic_df = pd.DataFrame(synthetic_rows)
    combined = pd.concat([data, synthetic_df], ignore_index=True)
    combined.sort_values(['City', 'Date'], inplace=True)
    combined.reset_index(drop=True, inplace=True)
    return combined


data = load_and_extend_data()

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.title('🏭 Air Quality Dashboard')
st.write("Visualizing Air Pollution Levels in Indian Cities (2015 – 2025)")

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
st.sidebar.title('Study the AQI Patterns')
display_aqi_by_city    = st.sidebar.checkbox('📶 AQI by City')
display_aqi_by_year    = st.sidebar.checkbox('📉 AQI by Year')
display_pollutants     = st.sidebar.checkbox('📜 Pollutants Over Time', value=True)

# ─────────────────────────────────────────────
# 1. AQI by City
# ─────────────────────────────────────────────
if display_aqi_by_city:
    st.subheader('📶 AQI by City')
    cities = sorted(data['City'].unique())
    selected_city = st.selectbox('Select a city', cities, key='city_aqi')
    city_data = data[data['City'] == selected_city].copy()
    city_data['Year'] = city_data['Date'].dt.year

    yearly_avg = city_data.groupby('Year')['AQI'].mean().reset_index()

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(x=yearly_avg['Year'], y=yearly_avg['AQI'], ax=ax, color='#4C72B0')
    ax.set_xlabel('Year')
    ax.set_ylabel('Average AQI')
    ax.set_title(f'AQI Trend for {selected_city}')
    sns.despine(fig=fig)
    st.pyplot(fig)

    st.write('**Observations:**')
    st.write('- The graph shows the average AQI trend for the selected city over the years.')
    st.write('- Higher AQI values indicate worse air quality.')
    st.write('- The trend can help identify if air quality has improved or deteriorated over time.')

# ─────────────────────────────────────────────
# 2. AQI by Year
# ─────────────────────────────────────────────
if display_aqi_by_year:
    st.subheader('📉 AQI by Year')
    all_years = sorted(data['Date'].dt.year.unique())
    selected_year = st.selectbox('Select a year', all_years, key='year_aqi')
    year_data = data[data['Date'].dt.year == selected_year]
    year_avg = year_data.groupby('City')['AQI'].mean().reset_index().sort_values('AQI', ascending=False)

    fig, ax = plt.subplots(figsize=(12, 4))
    sns.barplot(x=year_avg['City'], y=year_avg['AQI'], ax=ax, color='#4C72B0')
    ax.set_xlabel('City')
    ax.set_ylabel('Average AQI')
    ax.set_title(f'AQI by City for {selected_year}')
    plt.xticks(rotation=45, ha='right')
    sns.despine(fig=fig)
    st.pyplot(fig)

    st.write('**Observations:**')
    st.write('- The graph shows the average AQI for different cities in the selected year.')
    st.write('- Cities with higher bars have worse air quality.')

# ─────────────────────────────────────────────
# 4. Pollutants Over Time
# ─────────────────────────────────────────────
if display_pollutants:
    st.subheader('📜 Pollutants Over Time')
    pollutants = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'CO', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene']
    selected_pollutants = st.multiselect('Select pollutants', pollutants, default=['PM2.5', 'PM10'])

    cities = sorted(data['City'].unique())
    selected_city = st.selectbox('Select a city', cities, key='pollutant_city')
    city_data = data[data['City'] == selected_city]

    fig, ax = plt.subplots(figsize=(12, 5))
    for pollutant in selected_pollutants:
        ax.plot(city_data['Date'], city_data[pollutant], label=pollutant)

    ax.set_xlabel('Date')
    ax.set_ylabel('Pollutant Level')
    ax.set_title(f'Pollutants Over Time for {selected_city}')
    ax.legend(fontsize=8)
    sns.despine(fig=fig)
    st.pyplot(fig)

    st.write('**Observations:**')
    st.write('- The graph shows the levels of selected pollutants over time for the selected city.')
    st.write('- It allows monitoring the trends and patterns of pollutant levels.')
    st.write('- Higher pollutant levels indicate worse air quality.')
    st.write('- The graph can help identify any seasonal or long-term variations in pollutant levels.')