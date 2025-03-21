import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set_theme(style='dark')

def load_data():
    df_day = pd.read_csv("Dashboard/clean_day.csv")
    df_hour = pd.read_csv("Dashboard/clean_hour.csv")
    
    df_day["dteday"] = pd.to_datetime(df_day["dteday"])
    df_hour["dteday"] = pd.to_datetime(df_hour["dteday"])
    
    return df_day, df_hour

df_day, df_hour = load_data()

with st.sidebar:
    st.image("https://media.istockphoto.com/id/1329906434/vector/city-bicycle-sharing-system-isolated-on-white.jpg?s=612x612&w=0&k=20&c=weiMZhJoWWzNGtx7khfXPbE3s2Lpw5n6M7iWoxCsBPU=")
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=df_day["dteday"].min().date(),
        max_value=df_day["dteday"].max().date(),
        value=[df_day["dteday"].min().date(), df_day["dteday"].max().date()]
    )

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

filtered_day = df_day[(df_day["dteday"] >= start_date) & (df_day["dteday"] <= end_date)]
filtered_hour = df_hour[(df_hour["dteday"] >= start_date) & (df_hour["dteday"] <= end_date)]

st.header('By Bike Rent from Hackone Industries 🚴')

# Total metrics
st.subheader('Daily Update')
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Rentals", filtered_day["total_rent"].sum())
with col2:
    st.metric("Total Registered", filtered_day["registered"].sum())
with col3:
    st.metric("Total Casual", filtered_day["casual"].sum())

# Top 5 busiest days
st.subheader("Top 5 Busiest Hours")
top_hours = filtered_hour.groupby("hour")["total_rent"].sum().nlargest(5).reset_index()
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x="hour", y="total_rent", data=top_hours, palette=["#D3D3D3", "#90CAF9", "#D3D3D3"])
st.pyplot(fig)

# Comparison of Total Rentals by Weekday and Weekend
st.subheader("Comparison of Total Rentals by Weekday and Weekend")
day_category_rent = filtered_hour.groupby("day_category")["total_rent"].sum().reset_index()
fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(x='day_category', y='total_rent', data=day_category_rent, palette='viridis')
st.pyplot(fig)

# Heatmap tren rent
st.subheader("Heatmap of Total Rentals by Weekday and Hour")
weekly_trend = filtered_hour.pivot_table(index='weekday', columns='hour', values='total_rent', aggfunc='mean')
fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(weekly_trend, cmap="coolwarm", annot=False, cbar=True, linewidths=0.5)
st.pyplot(fig)

# Plot total rentals over time
st.subheader("Total Perfomance of Rentals Over Time")
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(filtered_day["dteday"], filtered_day["total_rent"], marker='o', linewidth=2, color="#90CAF9")
st.pyplot(fig)

# Rent by season
st.subheader("Comparison of Total Rentals by Season")
season_rent = filtered_day.groupby("season")["total_rent"].sum().reset_index()
fig, ax = plt.subplots(figsize=(10, 8))
sns.barplot(x='season', y='total_rent', data=season_rent, palette='viridis')
st.pyplot(fig)

# Pie chart musim
fig, ax = plt.subplots(figsize=(8, 8))
ax.pie(season_rent['total_rent'], labels=season_rent['season'], autopct='%1.1f%%', 
       colors=sns.color_palette('viridis', len(season_rent)))
st.pyplot(fig)

st.subheader("RFM Analysis to Identify Customer Segments")
current_date = filtered_hour["dteday"].max()
rfm_df = filtered_hour.groupby("registered").agg({
    "dteday": lambda x: (current_date - x.max()).days,  # Recency
    "total_rent": "sum",                             # Monetary
    "registered": "count"                            # Frequency
}).rename_axis('customer_id').reset_index()
rfm_df.columns = ["Customer_ID", "Recency", "Monetary", "Frequency"]
st.dataframe(rfm_df.head())

# find the relationship between Frequency and Monetary, colored by Recency
plt.figure(figsize=(8, 6))
scatter = plt.scatter(x=rfm_df['Frequency'], y=rfm_df['Monetary'], c=rfm_df['Recency'], cmap='coolwarm')
plt.title('Frequency vs Monetary (colored by Recency)')
plt.xlabel('Frequency')
plt.ylabel('Monetary')
plt.colorbar(scatter, label='Recency')
plt.show()

# Visualisasi distribusi RFM
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

sns.histplot(rfm_df['Recency'], bins=30, kde=True, ax=axes[0], color='blue')
axes[0].set_title('Distribution of Recency')
axes[0].set_xlabel('Recency (days)')

sns.histplot(rfm_df['Frequency'], bins=30, kde=True, ax=axes[1], color='green')
axes[1].set_title('Distribution of Frequency')
axes[1].set_xlabel('Frequency (count)')

sns.histplot(rfm_df['Monetary'], bins=30, kde=True, ax=axes[2], color='red')
axes[2].set_title('Distribution of Monetary')
axes[2].set_xlabel('Monetary (total rent)')

plt.tight_layout()
st.pyplot(plt.gcf())

st.subheader("Clustering of Unique Total Rent Counts by Weather")

weather_rent = df_hour.groupby(by="weather").total_rent.nunique().sort_values(ascending=False).reset_index()

# Pie Chart
plt.figure(figsize=(7, 7))
plt.pie(weather_rent['total_rent'], labels=weather_rent['weather'], autopct='%1.1f%%', colors=sns.color_palette('viridis', len(weather_rent)))
plt.title('Clustering of Unique Total Rent Counts by Weather')
st.pyplot(plt.gcf())

st.subheader("Clustering of Total Rent Counts by humidity")

humidity_rent = df_hour.groupby(by="humidity_category").agg({"total_rent": "count"}).reset_index()

# Bar Chart
plt.figure(figsize=(8, 5))
sns.barplot(x='humidity_category', y='total_rent', data=humidity_rent, palette='coolwarm')
plt.title('Total Bike Rentals by Humidity Category')
plt.xlabel('Humidity Category')
plt.ylabel('Total Rentals')
st.pyplot(plt.gcf())


# Pie Chart
plt.figure(figsize=(7, 7))
plt.pie(humidity_rent['total_rent'], labels=humidity_rent['humidity_category'], autopct='%1.1f%%', colors=sns.color_palette('coolwarm', len(humidity_rent)))
plt.title('Clustering of Bike Rentals by Humidity Category')
st.pyplot(plt.gcf())