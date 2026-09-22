import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

st.title("🌾 Rice Production Prediction App")
st.write("Upload your rice production dataset and predict future outputs!")

uploaded = st.file_uploader("📤 Upload your CSV file", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)


    df = df.rename(columns={
        "province": "province",
        "year": "year",
        "harvest_area": "area_ha",
        "productivity": "productivity_kgha",
        "production": "production_kg"
    })

    st.subheader("📌 Preview of Uploaded Dataset")
    st.dataframe(df.head())

    provinces = sorted(df["province"].unique())
    province_name = st.selectbox("Select a Province:", provinces)

    def train_province_model(province_name):
        province_df = df[df["province"].str.upper() == province_name.upper()].copy()

        if len(province_df) < 2:
            st.error(f"Not enough data for: {province_name}")
            return None, None, None, None, None

        X = province_df[["year"]].values
        y = province_df["production_kg"].values

        model = LinearRegression()
        model.fit(X, y)

        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))

        # Extended plot up to 2030
        min_year = province_df["year"].min()
        max_year = max(province_df["year"].max(), 2030)
        plot_years = np.arange(min_year, max_year + 1).reshape(-1, 1)
        plot_pred = model.predict(plot_years)

        return model, X, y, plot_years, plot_pred, r2, rmse

    if st.button("Train Model"):
        model, X, y, plot_years, plot_pred, r2, rmse = train_province_model(province_name)

        if model is not None:
            st.subheader(f"📊 Model Results for {province_name}")

            st.write(f"**R² Score:** {r2:.4f}")
            st.write(f"**RMSE:** {rmse:.4f}")
            st.write(f"**Slope:** {model.coef_[0]:.4f}")
            st.write(f"**Intercept:** {model.intercept_:.4f}")

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.scatter(X, y, label="Actual Data")
            ax.plot(plot_years, plot_pred, label="Regression Line")
            ax.set_title(f"Production Trend — {province_name}")
            ax.set_xlabel("Year")
            ax.set_ylabel("Production (kg)")
            ax.grid(True)
            ax.legend()
            st.pyplot(fig)

            st.success("Model trained successfully!")

            st.subheader("🔮 Prediction Options")

            mode = st.radio("Choose Prediction Mode:", [
                "Predict Province-Level Production",
                "Predict Individual Farmland Output"
            ])

            if mode == "Predict Province-Level Production":
                year = st.number_input("Enter year to predict:", min_value=2024, max_value=2100, step=1)
                if st.button("Predict Production"):
                    pred_kg = float(model.predict(np.array([[year]]))[0])
                    pred_ton = pred_kg / 1000.0

                    st.success(f"Projected production for {province_name} in {year}: **{pred_ton:,.2f} tons**")

            if mode == "Predict Individual Farmland Output":
                area = st.number_input("Your farmland area (ha):", min_value=0.1, step=0.1)
                if st.button("Predict Farmland Output"):
                    province_df = df[df["province"].str.upper() == province_name.upper()].copy()
                    avg_prod = province_df["productivity_kgha"].mean()

                    output_ton = (avg_prod * area) / 1000.0

                    st.success(f"Estimated output for {area} ha in {province_name}: **{output_ton:.2f} tons**")