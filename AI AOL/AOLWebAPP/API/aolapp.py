from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64

app = FastAPI(
    title="Rice Production Prediction API",
    version="1.0",
    description="Upload dataset → Train model → Predict province/farmer output"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globals
df_global = None
models = {}  # maps normalized province -> trained sklearn model
model_stats = {}  # maps normalized province -> stats dict


def normalize_prov(p: str) -> str:
    return p.strip().upper()


@app.post("/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
    global df_global, models, model_stats

    try:
        df = pd.read_csv(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV file: {e}")

    # rename columns if present
    rename_map = {
        "province": "province",
        "year": "year",
        "harvest_area": "area_ha",
        "productivity": "productivity_kgha",
        "production": "production_kg"
    }
    df = df.rename(columns=rename_map)

    # Basic validation
    required = ["province", "year", "productivity_kgha", "production_kg"]
    for col in required:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Missing required column: {col}")

    # Ensure types
    df = df.dropna(subset=["province", "year", "production_kg"])
    df["year"] = df["year"].astype(int)

    df_global = df

    # clear any previous models
    models = {}
    model_stats = {}

    provinces = sorted(df_global["province"].unique())
    return {"status": "success", "rows": len(df_global), "provinces": provinces}


@app.get("/provinces")
def get_provinces():
    if df_global is None:
        raise HTTPException(400, "Dataset not uploaded yet")
    return {"provinces": sorted(df_global["province"].unique())}


def make_regression_plot(years, actual, plot_years, pred_vals, province_name):
    plt.figure(figsize=(8,4.5))
    plt.scatter(years, actual, label="Actual Data")
    plt.plot(plot_years, pred_vals, label="Regression Line")
    plt.title(f"Rice Production — {province_name}")
    plt.xlabel("Year")
    plt.ylabel("Production (kg)")
    plt.grid(True, alpha=0.25)
    plt.legend()

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=120)
    plt.close()
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    return img_b64


@app.post("/train")
def train_province(province: str):
    global models, model_stats
    if df_global is None:
        raise HTTPException(400, "Dataset not uploaded yet")

    prov_norm = normalize_prov(province)
    province_df = df_global[df_global["province"].str.upper() == prov_norm].copy()

    if province_df.shape[0] < 2:
        raise HTTPException(400, f"Not enough data to train model for: {province}")

    X = province_df[["year"]].values
    y = province_df["production_kg"].values

        # --- Train-Test Split Validation ---
    if province_df.shape[0] >= 4:  # only if enough data
        from sklearn.model_selection import train_test_split

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )

        val_model = LinearRegression()
        val_model.fit(X_train, y_train)

        val_pred = val_model.predict(X_test)

        val_r2 = float(r2_score(y_test, val_pred))
        val_rmse = float(np.sqrt(mean_squared_error(y_test, val_pred)))

        # store validation stats
        model_stats.setdefault(prov_norm, {})
        model_stats[prov_norm].update({
            "val_r2": val_r2,
            "val_rmse": val_rmse,
            "train_rows": len(X_train),
            "test_rows": len(X_test)
        })
    else:
        # not enough data for split
        model_stats.setdefault(prov_norm, {})
        model_stats[prov_norm].update({
            "val_r2": None,
            "val_rmse": None,
            "train_rows": None,
            "test_rows": None
        })

    model = LinearRegression()
    model.fit(X, y)

    y_pred = model.predict(X)
    r2 = float(r2_score(y, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y, y_pred)))
    slope = float(model.coef_[0])
    intercept = float(model.intercept_)

    # Prepare plot (extend to 2030 or +5 years)
    min_year = int(province_df["year"].min())
    max_year = max(int(province_df["year"].max()), 2030)
    plot_years = np.arange(min_year, max_year + 1).reshape(-1,1)
    plot_preds = model.predict(plot_years)

    img_b64 = make_regression_plot(province_df["year"].values, y, plot_years.flatten(), plot_preds, province)

    models[prov_norm] = model
    model_stats[prov_norm] = {
        "r2": r2,
        "rmse": rmse,
        "slope": slope,
        "intercept": intercept,
        "trained_rows": int(province_df.shape[0])
    }

    return {
        "status": "trained",
        "province": province,
        "r2": r2,
        "rmse": rmse,
        "slope": slope,
        "intercept": intercept,
        "plot_png_base64": img_b64
    }


@app.get("/predict-province")
def predict_province(province: str, year: int):
    prov_norm = normalize_prov(province)
    if prov_norm not in models:
        raise HTTPException(400, "Model not trained for this province")

    model = models[prov_norm]
    pred_kg = float(model.predict(np.array([[year]]))[0])
    pred_tons = pred_kg / 1000.0

    province_df = df_global[df_global["province"].str.upper() == prov_norm]
    avg_prod_kgha = float(province_df["productivity_kgha"].mean())
    tons_per_ha = avg_prod_kgha / 1000.0  # convert kg/ha to tons/ha

    stats = model_stats.get(prov_norm, {})

    return {
        "province": province,
        "year": year,
        "predicted_tons": pred_tons,
        "predicted_tons_per_ha": tons_per_ha,
        "model_stats": stats
    }


@app.get("/predict-farmer")
def predict_farmer(province: str, area_ha: float, year: int | None = None):
    """
    year is optional. If provided, use regression model for year-based scaling.
    Otherwise use average productivity.
    """
    if df_global is None:
        raise HTTPException(400, "Dataset not uploaded yet")

    prov_norm = normalize_prov(province)
    province_df = df_global[df_global["province"].str.upper() == prov_norm].copy()

    if province_df.empty:
        raise HTTPException(400, "Province not found in dataset")

    # Base productivity (kg/ha)
    avg_prod_kgha = float(province_df["productivity_kgha"].mean())

    # If year provided & model trained, scale productivity using slope trend
    if year is not None and prov_norm in models:
        model = models[prov_norm]
        # predicted production for entire province this year
        pred_kg_total = float(model.predict(np.array([[year]]))[0])

        # estimate productivity trend:
        # productivity = total_production / avg_area (approximation)
        # fallback: use slope ratio
        last_year = province_df["year"].max()
        last_total = province_df[province_df["year"] == last_year]["production_kg"].iloc[0]

        scale = pred_kg_total / last_total if last_total > 0 else 1
        adjusted_prod_kgha = avg_prod_kgha * scale
    else:
        adjusted_prod_kgha = avg_prod_kgha

    # Farmer’s yield
    kg = area_ha * adjusted_prod_kgha
    tons = kg / 1000.0
    tons_per_ha = adjusted_prod_kgha / 1000.0

    return {
        "province": province,
        "area_ha": area_ha,
        "year": year,
        "predicted_tons": tons,
        "predicted_tons_per_ha": tons_per_ha
    }