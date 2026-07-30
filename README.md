<<<<<<< HEAD
# Student Performance Analytics Dashboard

A multi-page analytics dashboard built with Dash, Plotly, Pandas, and
Scikit-learn. Explore how study habits, attendance, and background
factors relate to exam performance, and predict a student's likely
exam score with a trained ML model.

## Features

- **Dashboard** — KPI cards, filters (gender, school type, income,
  parental involvement, hours studied, attendance), overview charts,
  and auto-generated text insights.
- **Analytics** — correlation heatmap, category-driven box plots,
  ML feature-importance ranking, previous-score regression.
- **Data Explorer** — searchable, sortable, filterable DataTable with
  CSV export of exactly what's on screen.
- **ML Prediction** — form-based exam score prediction using a
  pre-trained RandomForestRegressor.
- **About** — project, dataset, and tech-stack summary.

## Project Structure

```
student_performance_dashboard/
├── app.py                  # Entry point: layout shell + page routing
├── requirements.txt
├── Procfile                 # gunicorn start command (Render/Railway)
├── runtime.txt               # pinned Python version
├── assets/
│   └── style.css              # all custom CSS (auto-loaded by Dash)
├── data/
│   └── StudentPerformanceFactors.csv
├── components/                # reusable, callback-free UI pieces
│   ├── sidebar.py
│   ├── header.py
│   ├── cards.py
│   └── footer.py
├── pages/                     # one module per route (dash.register_page)
│   ├── dashboard.py            # "/"
│   ├── analytics.py            # "/analytics"
│   ├── explorer.py             # "/explorer"
│   ├── ml_prediction.py        # "/predict"
│   └── about.py                 # "/about"
├── utils/
│   ├── data_loader.py           # load/clean/filter the dataset (cached)
│   ├── chart_theme.py           # shared Plotly styling
│   └── ml_utils.py              # loads model artifacts, runs predictions
└── models/
    ├── train_model.py           # offline training script
    ├── model.joblib              # trained RandomForestRegressor
    ├── scaler.joblib              # StandardScaler for numeric features
    └── encoders.joblib            # LabelEncoders + feature-order metadata
```

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# (Optional) retrain the model after changing the dataset:
python models/train_model.py

python app.py
```

Visit `http://localhost:8050`.

## Retraining the Model

The app never trains at request time — it only loads the artifacts in
`models/`. If you replace `data/StudentPerformanceFactors.csv`, retrain
with:

```bash
python models/train_model.py
```

This regenerates `model.joblib`, `scaler.joblib`, and `encoders.joblib`
using the identical preprocessing the prediction page expects, so
there's never a mismatch between training and serving.

## Deployment (Render / Railway)

Both platforms auto-detect Python and use `requirements.txt` +
`Procfile`:

1. Push this project to a Git repository.
2. Create a new **Web Service** (Render) or project (Railway) from
   the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command is read from `Procfile`:
   `gunicorn app:server --workers 2 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT`
5. No environment variables are required for a default deployment.

## Data Notes

The bundled dataset (`StudentPerformanceFactors.csv`) has a small
number of missing values in `Teacher_Quality`, `Parental_Education_Level`,
and `Distance_from_Home`. `utils/data_loader.py` imputes categorical
gaps with the column mode and numeric gaps with the column median, and
drops exact duplicate rows, so every page works from one consistent,
clean copy of the data.
=======
# studentperfomance
>>>>>>> 644738be4c345d64cbd54b6a7cbce7d1db32b201
