# TSA Analysis Dashboard

## Overview
This Streamlit app analyzes Tourism Satellite Account (TSA) data based on the UN TSA Framework 2008.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run the app: `streamlit run tsa_app.py`
3. Open `http://localhost:8501` in your browser.
4. Upload a TSA Excel file with:
   - Table_4_Internal_Consumption (Columns: Products, Internal_Tourism_Consumption)
   - Table_6_Supply_Demand_Core (Columns: Products, Domestic_Supply, Internal_Tourism_Consumption, Tourism_Ratio_Percent)
   - Table_7_Employment (Columns: Tourism_Industries, Full_Time_Equivalent_Jobs)

## Deployment
Deploy to Streamlit Community Cloud by connecting this repository.