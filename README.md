# PaySim Synthetic Financial Datasets For Fraud Detection

This is a streamlit based dashboard for the following dataset:

Source link: [Synthetic Financial Datasets For Fraud Detection](https://www.kaggle.com/datasets/ealaxi/paysim1/data)

To launch the project, you can take the following steps:

1. `git clone https://github.com/sgoley/paysim-dashboard.git`
2. `cd paysim-dashboard`
3. `uv venv`
4. `source .venv/bin/activate`
5. `uv sync` or `uv pip install -r requirements.txt`
6. Create `.streamlit/secrets.toml` as described below
7. `python startup.py`
8. `streamlit run streamlit_app.py`

## Required files

> [!NOTE]
> `url` value in `secrets.toml` is only required if you intend to connect to a remotely hosted duckdb file.

`.streamlit/secrets.toml`

``` toml
[constants]
url=""
datetime_base='2025-01-01'
```
