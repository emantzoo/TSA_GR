# 📊 TSA Analysis Dashboard - Complete Specifications

## Table of Contents
- [Overview](#overview)
- [Data Upload & Validation](#data-upload--validation)
- [Core Analysis Dashboard](#core-analysis-dashboard)
- [Tourism Ratios Analysis](#tourism-ratios-analysis)
- [Employment Analysis](#employment-analysis)
- [Scenario Analysis & Forecasting](#scenario-analysis--forecasting)
- [Executive Summary](#executive-summary)
- [Data Validation & Quality Assessment](#data-validation--quality-assessment)
- [Technical Implementation](#technical-implementation)

---

## Overview

The TSA Analysis Dashboard implements the **UN Tourism Satellite Account Framework 2008** providing comprehensive economic analysis of tourism's contribution to national economies. The system processes real TSA data and generates standardized reports with interactive visualizations.

### Framework Compliance
- ✅ UN TSA Recommended Methodology Framework (RMF) 2008
- ✅ System of National Accounts (SNA) 2008 compatibility
- ✅ OECD Tourism Statistics guidelines
- ✅ World Tourism Organization (UNWTO) standards

---

## 🏠 Data Upload & Validation

### Required TSA Tables

#### Core Tables (Mandatory)
| Table | Name | Key Columns | Purpose |
|-------|------|-------------|---------|
| `Table_4_Internal_Consumption` | Internal Tourism Consumption | `Products`, `Internal_Tourism_Consumption` | Demand-side analysis |
| `Table_6_Supply_Demand_Core` | Supply and Demand | `Products`, `Domestic_Supply`, `Internal_Tourism_Consumption`, `Tourism_Ratio_Percent` | Supply-demand balance, tourism ratios |
| `Table_7_Employment` | Tourism Employment | `Tourism_Industries`, `Full_Time_Equivalent_Jobs` | Employment analysis |

#### Required Tables (Full Analysis)
- `Table_1_Inbound_Expenditure` - Inbound visitor expenditure
- `Table_2_Domestic_Expenditure` - Domestic tourism expenditure  
- `Table_3_Outbound_Expenditure` - Outbound resident expenditure
- `Table_5_Production_Accounts` - Tourism industry production

#### Optional Tables (Enhanced Analysis)
- `Table_8_Capital_Formation` - Tourism investment
- `Table_9_Collective_Consumption` - Government tourism consumption
- `Table_10a_Trips_Overnights` - Visitor statistics
- `Table_10b_Transport_Arrivals` - Transport statistics
- `Table_10c_Accommodation` - Accommodation statistics

### Data Validation Rules

#### Structural Validation
```python
# Table 4 validation
required_cols_t4 = ['Products', 'Internal_Tourism_Consumption']
optional_cols_t4 = ['Inbound_Tourism_Expenditure', 'Domestic_Tourism_Expenditure', 
                    'Internal_Tourism_Expenditure', 'Other_Components']

# Table 6 validation  
required_cols_t6 = ['Products', 'Domestic_Supply', 'Internal_Tourism_Consumption', 
                    'Tourism_Ratio_Percent']
optional_cols_t6 = ['Total_Domestic_Output', 'Imports', 'Taxes_less_Subsidies', 
                    'Trade_Transport_Margins']

# Table 7 validation
required_cols_t7 = ['Tourism_Industries', 'Full_Time_Equivalent_Jobs']
optional_cols_t7 = ['Total_Jobs', 'Number_of_Establishments', 'GVA_Tourism_Share',
                    'Jobs_Employees_Male', 'Jobs_Employees_Female', 
                    'Jobs_Self_employed_Male', 'Jobs_Self_employed_Female']
```

#### Data Quality Checks
- **Completeness**: Missing value detection and reporting
- **Consistency**: Cross-table validation of tourism consumption figures
- **Reasonableness**: Tourism ratio bounds checking (0% ≤ ratio ≤ 300%)
- **Balance**: Supply-demand reconciliation where data permits

---

## 📊 Core Analysis Dashboard

### 1. Demand-Side Economic Aggregates

#### Internal Tourism Consumption
**Data Source:** `Table_4_Internal_Consumption`
- **Primary Column:** `Internal_Tourism_Consumption`
- **Unit:** Millions of euros (current prices)
- **Calculation:** 
```python
internal_tourism_consumption = Table_4['Internal_Tourism_Consumption'].sum()
```
- **Definition:** Total final consumption expenditure of visitors on tourism products within the economy
- **TSA Reference:** RMF Table 4, total tourism internal consumption

#### Expenditure by Visitor Type
**Data Source:** `Table_4_Internal_Consumption`
- **Inbound Expenditure:** `Inbound_Tourism_Expenditure` (if available)
- **Domestic Expenditure:** `Domestic_Tourism_Expenditure` (if available)
- **Alternative:** `Internal_Tourism_Expenditure`

**Calculations:**
```python
if 'Inbound_Tourism_Expenditure' in Table_4.columns:
    inbound_expenditure = Table_4['Inbound_Tourism_Expenditure'].sum()
    domestic_expenditure = Table_4['Domestic_Tourism_Expenditure'].sum()
    total_expenditure = inbound_expenditure + domestic_expenditure
    
    # Market share analysis
    inbound_share = (inbound_expenditure / total_expenditure) * 100
    domestic_share = (domestic_expenditure / total_expenditure) * 100
else:
    # Fallback to total internal expenditure
    inbound_expenditure = 0
    domestic_expenditure = Table_4['Internal_Tourism_Expenditure'].sum()
```

#### Tourism Consumption per Capita
**Data Sources:** 
- Tourism consumption: `Table_4['Internal_Tourism_Consumption'].sum()`
- Population: User input parameter
**Calculation:** 
```python
tourism_consumption_per_capita = internal_tourism_consumption / population
```
- **Unit:** Euros per resident per year
- **Interpretation:** Individual tourism spending intensity, international comparability indicator

#### Other Tourism Components
**Data Source:** `Table_4_Internal_Consumption`
- **Column:** `Other_Components` (optional)
- **Default:** 0 if not available
- **Examples:** Social transfers in kind, imputed rentals, other non-monetary flows

### 2. Supply-Side Economic Aggregates

#### Tourism Direct Gross Value Added (TDGVA)
**Primary Source:** `Table_7_Employment['GVA_Tourism_Share']`
```python
if 'GVA_Tourism_Share' in Table_7.columns:
    tourism_direct_gva = Table_7['GVA_Tourism_Share'].sum()
else:
    # Alternative estimation method
    tourism_ratios = Table_6['Tourism_Ratio_Percent'] / 100
    domestic_supply = Table_6['Domestic_Supply']
    estimated_gva_ratio = 0.4  # Typical GVA to output ratio
    tourism_direct_gva = (tourism_ratios * domestic_supply * estimated_gva_ratio).sum()
    st.warning("⚠️ GVA estimated from tourism ratios (no direct GVA data)")
```
- **Definition:** Value added generated by tourism characteristic industries attributable to tourism consumption
- **TSA Reference:** RMF Table 5, tourism direct gross value added

#### Net Taxes on Tourism Products
**Data Source:** `Table_6_Supply_Demand_Core`
- **Column:** `Taxes_less_Subsidies` (if available)
```python
if 'Taxes_less_Subsidies' in Table_6.columns:
    tourism_taxes = (Table_6['Taxes_less_Subsidies'] * 
                    Table_6['Tourism_Ratio_Percent'] / 100).sum()
else:
    # Estimated tax rate approach
    tourism_taxes = tourism_direct_gva * 0.15  # 15% typical tax rate
    st.warning("⚠️ Taxes estimated (no direct tax data)")
```
- **Components:** VAT, excise taxes, import duties, less subsidies on tourism products
- **Estimation:** When unavailable, estimated as 10-20% of TDGVA based on country tax structure

#### Tourism Direct Gross Domestic Product (TDGDP)
**Calculation:** 
```python
tourism_direct_gdp = tourism_direct_gva + tourism_taxes
```
- **Definition:** Total direct contribution of tourism to GDP
- **Formula:** TDGDP = TDGVA + Net taxes on tourism products
- **TSA Reference:** RMF aggregated measure of tourism's direct economic impact

### 3. Economic Impact Indicators

#### Tourism GDP Share
**Formula:**
```python
tourism_gdp_share = (tourism_direct_gdp / total_gdp) * 100
```
- **Data Sources:** Calculated TDGDP + user input `total_gdp`
- **Unit:** Percentage of total national GDP
- **Benchmarks:** 
  - <3%: Low tourism economy
  - 3-10%: Moderate tourism economy  
  - >10%: High tourism economy

#### Tourism Employment Share
**Data Sources:**
- Tourism employment: `Table_7['Full_Time_Equivalent_Jobs'].sum()`
- Total employment: User input `total_employment`
```python
total_tourism_fte = Table_7['Full_Time_Equivalent_Jobs'].sum()
tourism_employment_share = (total_tourism_fte / total_employment) * 100
```

#### Labor Productivity in Tourism
**Calculation:**
```python
tourism_labor_productivity = (tourism_direct_gdp * 1000000) / total_tourism_fte
```
- **Unit:** Euros per FTE employee per year
- **Interpretation:** Higher values indicate more productive/capital-intensive tourism sector

#### Tourism Economic Multiplier
**Calculation:**
```python
tourism_multiplier = internal_tourism_consumption / tourism_direct_gdp
```
- **Interpretation:** 
  - Ratio >1: Tourism generates additional indirect economic activity
  - Ratio ≈1: Direct effects dominate
  - Higher ratios suggest stronger linkages with other sectors

---

## 🎯 Tourism Ratios Analysis

### 1. Product-Level Tourism Intensity

#### Tourism Ratio Calculation
**Data Source:** `Table_6_Supply_Demand_Core`
- **Formula:** `Tourism_Ratio = (Internal_Tourism_Consumption / Domestic_Supply) × 100`
- **Pre-calculated Column:** `Tourism_Ratio_Percent`
- **Unit:** Percentage

#### Tourism Intensity Classification
```python
ratios_df['Tourism_Intensity'] = pd.cut(
    ratios_df['Tourism_Ratio'], 
    bins=[0, 10, 30, 50, 100, 200],
    labels=['Very Low (<10%)', 'Low (10-30%)', 'Medium (30-50%)', 
           'High (50-100%)', 'Very High (>100%)'],
    include_lowest=True
)
```

**Classification Meanings:**
- **Very Low (<10%):** Minimal tourism dependency, primarily serves domestic market
- **Low (10-30%):** Limited tourism market penetration
- **Medium (30-50%):** Moderate tourism specialization
- **High (50-100%):** Strong tourism specialization
- **Very High (>100%):** Extreme tourism dependency, may indicate imports or stock depletion

#### Product Rankings and Analysis
```python
# Sort products by tourism intensity
ratios_df = ratios_df.sort_values('Tourism_Ratio', ascending=False)

# Top tourism-dependent products
top_ratios = ratios_df.head(10)

# Statistical measures
avg_ratio_unweighted = ratios_df['Tourism_Ratio'].mean()
avg_ratio_weighted = (ratios_df['Internal_Tourism_Consumption'].sum() / 
                     ratios_df['Domestic_Supply'].sum()) * 100
max_ratio = ratios_df['Tourism_Ratio'].max()
high_intensity_count = (ratios_df['Tourism_Ratio'] > 50).sum()
```

### 2. Supply-Demand Relationships

#### Enhanced Ratio Analysis (if additional data available)
**Tourism Share of Domestic Output:**
```python
if 'Total_Domestic_Output' in Table_6.columns:
    ratios_df['Tourism_Share_Output'] = (
        ratios_df['Internal_Tourism_Consumption'] / 
        ratios_df['Total_Domestic_Output'] * 100
    )
```

**Import Dependency Analysis:**
```python
if 'Imports' in Table_6.columns:
    ratios_df['Import_Share'] = (
        ratios_df['Imports'] / ratios_df['Domestic_Supply'] * 100
    )
    ratios_df['Tourism_Import_Dependency'] = (
        ratios_df['Import_Share'] * ratios_df['Tourism_Ratio'] / 100
    )
```

#### Supply-Consumption Comparison
**Visualization Data:**
- **X-axis:** Product names (top 8 by consumption)
- **Y-axis 1:** `Domestic_Supply` (total available supply)
- **Y-axis 2:** `Internal_Tourism_Consumption` (tourism demand)
- **Chart Type:** Grouped bar chart showing supply vs tourism demand

### 3. Sector Specialization Analysis

#### Tourism Specialization Index
```python
# Products highly specialized in tourism (>80% ratio)
highly_specialized = ratios_df[ratios_df['Tourism_Ratio'] > 80]

# Tourism characteristic products (typically >25% ratio)
characteristic_products = ratios_df[ratios_df['Tourism_Ratio'] > 25]

# Mixed-use products (5-25% ratio)
mixed_use_products = ratios_df[
    (ratios_df['Tourism_Ratio'] >= 5) & 
    (ratios_df['Tourism_Ratio'] <= 25)
]
```

---

## 👥 Employment Analysis

### 1. Industry Employment Structure

#### Core Employment Metrics
**Data Source:** `Table_7_Employment`
- **Primary Key:** `Tourism_Industries`
- **Main Metric:** `Full_Time_Equivalent_Jobs`
- **Additional Metrics:** `Total_Jobs`, `Number_of_Establishments`

```python
# Employment share calculation
employment_analysis = Table_7.copy()
employment_analysis['Employment_Share'] = (
    employment_analysis['Full_Time_Equivalent_Jobs'] / 
    employment_analysis['Full_Time_Equivalent_Jobs'].sum() * 100
)

# Sort by employment share
employment_analysis = employment_analysis.sort_values('Employment_Share', ascending=False)
```

#### Industry Classification (Typical TSA Industries)
- **Accommodation services** (ISIC 55)
- **Food and beverage serving activities** (ISIC 56)
- **Railway passenger transport** (ISIC 4911)
- **Road passenger transport** (ISIC 4922)
- **Water passenger transport** (ISIC 5011)
- **Air passenger transport** (ISIC 5110)
- **Transport equipment rental** (ISIC 7710)
- **Travel agencies and tour operators** (ISIC 7912, 7911)
- **Cultural activities** (ISIC 90-93)
- **Sports and recreation activities** (ISIC 93)

### 2. Employment Quality and Structure

#### Gender Distribution Analysis
**Data Sources:** `Table_7_Employment` (if available)
```python
if all(col in employment_analysis.columns for col in 
       ['Jobs_Employees_Male', 'Jobs_Employees_Female']):
    
    employment_analysis['Total_Male_Jobs'] = (
        employment_analysis.get('Jobs_Employees_Male', 0) + 
        employment_analysis.get('Jobs_Self_employed_Male', 0)
    )
    employment_analysis['Total_Female_Jobs'] = (
        employment_analysis.get('Jobs_Employees_Female', 0) + 
        employment_analysis.get('Jobs_Self_employed_Female', 0)
    )
    
    total_gender_jobs = (employment_analysis['Total_Male_Jobs'] + 
                        employment_analysis['Total_Female_Jobs'])
    employment_analysis['Female_Share'] = (
        employment_analysis['Total_Female_Jobs'] / total_gender_jobs * 100
    ).fillna(0)
```

#### Employment Type Analysis
**FTE to Total Jobs Ratio:**
```python
if 'Total_Jobs' in employment_analysis.columns:
    employment_analysis['FTE_Ratio'] = (
        employment_analysis['Full_Time_Equivalent_Jobs'] / 
        employment_analysis['Total_Jobs'] * 100
    )
```
- **High FTE Ratio (>90%):** Predominantly full-time employment
- **Medium FTE Ratio (70-90%):** Mixed employment patterns
- **Low FTE Ratio (<70%):** High part-time/seasonal employment

**Self-Employment Rate:**
```python
if all(col in employment_analysis.columns for col in 
       ['Jobs_Self_employed_Male', 'Jobs_Self_employed_Female']):
    
    total_self_employed = (employment_analysis['Jobs_Self_employed_Male'] + 
                          employment_analysis['Jobs_Self_employed_Female'])
    total_jobs_for_rate = employment_analysis.get('Total_Jobs', 
                                                 employment_analysis['Full_Time_Equivalent_Jobs'])
    employment_analysis['Self_Employment_Rate'] = (
        total_self_employed / total_jobs_for_rate * 100
    ).fillna(0)
```

### 3. Productivity and Performance Analysis

#### Labor Productivity by Industry
**Data Source:** `Table_7_Employment['GVA_Tourism_Share']` (if available)
```python
if 'GVA_Tourism_Share' in employment_analysis.columns:
    employment_analysis['Labor_Productivity'] = (
        employment_analysis['GVA_Tourism_Share'] / 
        employment_analysis['Full_Time_Equivalent_Jobs'] * 1000
    )
```
- **Unit:** Euros per FTE employee per year
- **Benchmarking:** Compare productivity across tourism industries

#### Establishment Analysis
**Jobs per Establishment:**
```python
if 'Number_of_Establishments' in employment_analysis.columns:
    employment_analysis['Jobs_per_Establishment'] = (
        employment_analysis['Full_Time_Equivalent_Jobs'] / 
        employment_analysis['Number_of_Establishments']
    )
```
- **Interpretation:**
  - High ratios: Large enterprises, potentially capital-intensive
  - Low ratios: Small business structure, potentially labor-intensive

### 4. Employment Concentration Analysis

#### Industry Concentration Metrics
```python
# Concentration ratios
top_3_employment_share = employment_analysis.head(3)['Employment_Share'].sum()
top_5_employment_share = employment_analysis.head(5)['Employment_Share'].sum()

# Herfindahl-Hirschman Index for employment concentration
hhi_employment = ((employment_analysis['Employment_Share'] / 100) ** 2).sum()

# Classification:
# HHI < 0.15: Competitive/diversified
# 0.15 ≤ HHI < 0.25: Moderately concentrated  
# HHI ≥ 0.25: Highly concentrated
```

---

## 🔮 Scenario Analysis & Forecasting

### 1. Growth Scenarios (5-10 Year Projections)

#### Scenario Parameter Definitions
**Pessimistic Scenario:**
- Annual tourism growth rate: 1%
- Employment elasticity: 0.8 (employment grows slower than demand)
- Productivity growth: 0.5% annually

**Realistic Scenario:**
- Annual tourism growth rate: 4%
- Employment elasticity: 0.9 (employment tracks demand closely)
- Productivity growth: 2% annually

**Optimistic Scenario:**
- Annual tourism growth rate: 7%
- Employment elasticity: 1.1 (employment grows faster than demand)
- Productivity growth: 3.5% annually

#### Projection Methodology
**Base Year Values:**
```python
base_consumption = analyzer.core_aggregates['internal_tourism_consumption']
base_employment = analyzer.core_aggregates['total_tourism_fte']
base_gdp = analyzer.core_aggregates['tourism_direct_gdp']
```

**Annual Calculations:**
```python
for year in range(1, years_ahead + 1):
    # Tourism consumption projection
    projected_consumption = base_consumption * ((1 + annual_growth_rate) ** year)
    
    # Employment projection with elasticity
    employment_growth_rate = annual_growth_rate * employment_elasticity
    projected_employment = base_employment * ((1 + employment_growth_rate) ** year)
    
    # GDP projection including productivity effects
    productivity_factor = (1 + productivity_growth) ** year
    gdp_growth_factor = (1 + annual_growth_rate) ** year
    projected_gdp = base_gdp * gdp_growth_factor * productivity_factor
    
    # Derived indicators
    projected_gdp_share = (projected_gdp / total_gdp) * 100
    projected_emp_share = (projected_employment / total_employment) * 100
    projected_productivity = (projected_gdp * 1000000) / projected_employment
```

### 2. Policy Intervention Analysis

#### Marketing Boost Intervention
**Assumptions:**
- Target: Increase inbound tourism by 15%
- Spillover: Increase domestic tourism by 2%
- Cost: €50 per additional visitor

**Impact Calculations:**
```python
# Market composition (typical assumption)
inbound_share = 0.4  # 40% of consumption from inbound
domestic_share = 0.6  # 60% from domestic

additional_inbound = base_consumption * inbound_share * 0.15
additional_domestic = base_consumption * domestic_share * 0.02
new_consumption = base_consumption + additional_inbound + additional_domestic

# Employment impact (elasticity-based)
consumption_growth = (new_consumption - base_consumption) / base_consumption
new_employment = base_employment * (1 + consumption_growth * 0.8)

# GDP impact
new_gdp = base_gdp * (new_consumption / base_consumption)

# Cost-benefit analysis
if total_inbound_visitors > 0:  # From Table_10a if available
    expenditure_per_visitor = (base_consumption * inbound_share * 1000) / total_inbound_visitors
    additional_visitors = (additional_inbound * 1000) / expenditure_per_visitor
    total_cost = additional_visitors * 50  # €50 per visitor
else:
    total_cost = 50000000  # €50M estimate

roi = ((new_gdp - base_gdp) * 1000000) / total_cost
```

#### Infrastructure Investment Intervention
**Assumptions:**
- Capacity increase: 25%
- Productivity boost: 20%
- Investment required: €500 million

```python
capacity_multiplier = 1.25
productivity_multiplier = 1.20

new_consumption = base_consumption * capacity_multiplier
new_employment = base_employment * (1 + 0.25 / 1.3)  # Employment multiplier
new_gdp = base_gdp * capacity_multiplier * productivity_multiplier

investment_cost = 500000000  # €500M
roi = ((new_gdp - base_gdp) * 1000000) / investment_cost
payback_years = investment_cost / ((new_gdp - base_gdp) * 1000000)
```

#### Skills Development Intervention
**Assumptions:**
- Productivity improvement: 30%
- Training cost: €2000 per worker
- Employment level maintained

```python
productivity_multiplier = 1.30
new_gdp = base_gdp * productivity_multiplier
new_employment = base_employment  # Same employment, higher productivity
new_consumption = base_consumption * (1 + 0.30 * 0.5)  # 50% consumption effect

total_cost = base_employment * 2000  # €2000 per worker
roi = ((new_gdp - base_gdp) * 1000000) / total_cost
```

#### Digital Transformation Intervention
**Assumptions:**
- Efficiency gains: 25%
- New market access: 10%
- Job displacement: 5%
- Investment: €150 million

```python
efficiency_multiplier = 1.25
market_multiplier = 1.10

new_consumption = base_consumption * market_multiplier
new_employment = base_employment * 0.95  # 5% job reduction
new_gdp = base_gdp * efficiency_multiplier * market_multiplier

investment_cost = 150000000  # €150M
roi = ((new_gdp - base_gdp) * 1000000) / investment_cost
```

### 3. Sensitivity Analysis

#### Parameter Impact Testing
**Tourism Ratios Sensitivity:**
```python
ratio_changes = [-20, -10, -5, 0, 5, 10, 20]  # Percentage changes
for change in ratio_changes:
    ratio_multiplier = 1 + (change / 100)
    new_gdp = base_gdp * ratio_multiplier
    gdp_change = ((new_gdp - base_gdp) / base_gdp) * 100
```

**Productivity Sensitivity:**
```python
productivity_changes = [-15, -10, -5, 0, 5, 10, 15]
for change in productivity_changes:
    productivity_multiplier = 1 + (change / 100)
    new_gdp = base_gdp * productivity_multiplier
    # Employment unchanged for productivity changes
    gdp_change = ((new_gdp - base_gdp) / base_gdp) * 100
```

**Employment Elasticity Analysis:**
```python
elasticity_values = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]
demand_shock = 0.10  # 10% demand increase

for elasticity in elasticity_values:
    employment_response = demand_shock * elasticity
    new_employment = base_employment * (1 + employment_response)
    employment_change = ((new_employment - base_employment) / base_employment) * 100
```

### 4. Crisis Recovery Simulation

#### Crisis Parameters
- **Crisis impact:** -40% decline in tourism demand
- **Recovery scenarios:** V-shaped (rapid), U-shaped (gradual), L-shaped (slow)
- **Time horizon:** 3 years

**Recovery Patterns:**
```python
recovery_scenarios = {
    'v_shaped': {
        'year_1_recovery': 0.6,  # 60% recovery in year 1
        'year_2_recovery': 0.9,  # 90% recovery in year 2  
        'year_3_recovery': 1.05  # 105% of pre-crisis by year 3
    },
    'u_shaped': {
        'year_1_recovery': 0.3,  # 30% recovery
        'year_2_recovery': 0.6,  # 60% recovery
        'year_3_recovery': 0.95  # 95% recovery
    },
    'l_shaped': {
        'year_1_recovery': 0.1,  # 10% recovery
        'year_2_recovery': 0.3,  # 30% recovery  
        'year_3_recovery': 0.6   # 60% recovery
    }
}

# Crisis year calculations
crisis_impact = -0.4
crisis_consumption = base_consumption * (1 + crisis_impact)
crisis_employment = base_employment * (1 + crisis_impact * 0.8)  # Employment more resilient
crisis_gdp = base_gdp * (1 + crisis_impact)
```

---

## 📋 Executive Summary

### 1. Automated Economic Assessment

#### Economic Significance Classification
```python
gdp_share = core_aggregates['tourism_gdp_share']
emp_share = core_aggregates['tourism_employment_share']

if gdp_share > 15:
    significance = "Very High"
    risk_level = "High Dependency Risk"
    recommendations = ["Diversification", "Crisis Preparedness"]
elif gdp_share > 10:
    significance = "High" 
    risk_level = "Moderate Dependency Risk"
    recommendations = ["Balanced Growth", "Risk Management"]
elif gdp_share > 5:
    significance = "Moderate"
    risk_level = "Balanced Development"
    recommendations = ["Optimization", "Sustainable Growth"]
else:
    significance = "Low"
    risk_level = "Growth Potential"
    recommendations = ["Market Development", "Infrastructure"]
```

#### Performance Benchmarking
```python
# Labor productivity assessment
productivity = (tourism_direct_gdp * 1000000) / total_tourism_fte

if productivity > 100000:
    productivity_rating = "Very High"
elif productivity > 80000:
    productivity_rating = "High"  
elif productivity > 60000:
    productivity_rating = "Moderate"
else:
    productivity_rating = "Low"

# Tourism intensity assessment
avg_ratio = tourism_ratios['Tourism_Ratio'].mean()
high_ratio_count = (tourism_ratios['Tourism_Ratio'] > 100).sum()

if high_ratio_count > 10:
    intensity_rating = "Very High Specialization"
elif high_ratio_count > 5:
    intensity_rating = "High Specialization"
elif avg_ratio > 30:
    intensity_rating = "Moderate Specialization"
else:
    intensity_rating = "Low Specialization"
```

### 2. Strategic Recommendations Engine

#### Rule-Based Recommendation System
```python
strategic_recommendations = []

# GDP-based recommendations
if gdp_share > 15:
    strategic_recommendations.extend([
        "🛡️ Economic Diversification: Reduce tourism dependency",
        "💾 Crisis Preparedness: Build resilience mechanisms",
        "🔄 Market Diversification: Spread visitor sources"
    ])
elif gdp_share < 3:
    strategic_recommendations.extend([
        "🚀 Growth Strategy: Expand tourism capacity",
        "📊 Market Development: Target new visitor segments", 
        "🏗️ Infrastructure: Invest in tourism facilities"
    ])

# Employment concentration
top_3_share = employment_analysis.head(3)['Employment_Share'].sum()
if top_3_share > 70:
    strategic_recommendations.append(
        "🌐 Industry Diversification: Develop broader tourism sectors"
    )

# Productivity-based
if productivity < 60000:
    strategic_recommendations.extend([
        "🎓 Skills Development: Invest in workforce training",
        "💻 Technology Adoption: Implement digital solutions"
    ])

# Universal recommendations
strategic_recommendations.extend([
    "📈 Regular Monitoring: Implement TSA updates",
    "🌱 Sustainable Development: Balance growth with sustainability"
])
```

### 3. Key Findings Generation

#### Automated Insight Discovery
```python
key_findings = []

# Economic impact finding
if gdp_share > 10:
    key_findings.append(
        f"🔍 **Major Economic Driver**: Tourism contributes {gdp_share:.1f}% to GDP, "
        f"indicating high economic importance"
    )
elif gdp_share < 3:
    key_findings.append(
        f"🔍 **Growth Opportunity**: Tourism at {gdp_share:.1f}% of GDP shows "
        f"significant expansion potential"
    )

# Industry structure finding
top_industry = employment_analysis.iloc[0]['Tourism_Industries']
top_share = employment_analysis.iloc[0]['Employment_Share']
key_findings.append(
    f"💼 **Employment Leader**: {top_industry} dominates with "
    f"{top_share:.1f}% of tourism jobs"
)

# Product specialization finding
top_product = tourism_ratios.iloc[0]['Product']
top_ratio = tourism_ratios.iloc[0]['Tourism_Ratio']
if top_ratio > 100:
    key_findings.append(
        f"📈 **High Specialization**: {top_product} shows extreme tourism "
        f"dependency at {top_ratio:.1f}%"
    )
```

---

## ✅ Data Validation & Quality Assessment

### 1. Comprehensive Quality Scoring

#### Scoring Methodology
```python
validation_score = 100  # Start with perfect score
issues = []

# Tourism consumption consistency (25 points)
table4_total = Table_4['Internal_Tourism_Consumption'].sum()
table6_total = Table_6['Internal_Tourism_Consumption'].sum()
consumption_discrepancy = abs(table4_total - table6_total)
consumption_pct_error = (consumption_discrepancy / table4_total * 100) if table4_total > 0 else 0

if consumption_pct_error > 5:
    validation_score -= 25
    issues.append(f"Major consumption inconsistency: {consumption_pct_error:.1f}%")
elif consumption_pct_error > 1:
    validation_score -= 15
    issues.append(f"Minor consumption inconsistency: {consumption_pct_error:.1f}%")

# Tourism ratios reasonableness (30 points)
extreme_ratios = Table_6[Table_6['Tourism_Ratio_Percent'] > 200]
very_high_ratios = Table_6[Table_6['Tourism_Ratio_Percent'] > 150]

if len(extreme_ratios) > 0:
    validation_score -= 30
    issues.append(f"{len(extreme_ratios)} products have extreme ratios (>200%)")
elif len(very_high_ratios) > 0:
    validation_score -= 15
    issues.append(f"{len(very_high_ratios)} products have very high ratios (>150%)")

# Data completeness (20 points maximum deduction)
missing_values = (
    Table_4['Internal_Tourism_Consumption'].isna().sum() +
    Table_6['Tourism_Ratio_Percent'].isna().sum() +
    Table_7['Full_Time_Equivalent_Jobs'].isna().sum()
)

if missing_values > 0:
    deduction = min(20, missing_values * 2)
    validation_score -= deduction
    issues.append(f"{missing_values} missing values in core data")

# Supply-demand balance (25 points)
if all(col in Table_6.columns for col in 
       ['Total_Domestic_Output', 'Imports', 'Taxes_less_Subsidies']):
    
    supply_discrepancies = 0
    for _, row in Table_6.iterrows():
        calculated_supply = (row['Total_Domestic_Output'] + 
                           row.get('Imports', 0) + 
                           row.get('Taxes_less_Subsidies', 0))
        reported_supply = row['Domestic_Supply']
        discrepancy = abs(calculated_supply - reported_supply)
        
        if discrepancy > reported_supply * 0.05:  # 5% tolerance
            supply_discrepancies += 1
    
    if supply_discrepancies > len(Table_6) * 0.1:  # >10% of products
        validation_score -= 25
        issues.append(f"Supply-demand imbalances in {supply_discrepancies} products")
```

#### Quality Rating Classification
```python
if validation_score >= 95:
    quality_rating = "EXCELLENT"
    quality_color = "🟢"
elif validation_score >= 85:
    quality_rating = "VERY GOOD"
    quality_color = "🟢"
elif validation_score >= 75:
    quality_rating = "GOOD"
    quality_color = "🟡"
elif validation_score >= 60:
    quality_rating = "ACCEPTABLE"
    quality_color = "🟡"
else:
    quality_rating = "NEEDS IMPROVEMENT"
    quality_color = "🔴"
```

### 2. Detailed Validation Checks

#### Cross-Table Consistency
```python
# Tourism consumption reconciliation
table_comparisons = {
    'Table 4 Total': table4_total,
    'Table 6 Total': table6_total,
    'Absolute Difference': consumption_discrepancy,
    'Percentage Difference': consumption_pct_error
}

# Employment data consistency
if 'Total_Jobs' in Table_7.columns:
    fte_total = Table_7['Full_Time_Equivalent_Jobs'].sum()
    total_jobs = Table_7['Total_Jobs'].sum()
    fte_ratio = (fte_total / total_jobs) * 100
    
    if fte_ratio > 100:
        issues.append("FTE jobs exceed total jobs - data inconsistency")
```

#### Structural Validation
```python
# Required column verification
structural_issues = []

for table_name, required_cols in [
    ('Table_4', ['Products', 'Internal_Tourism_Consumption']),
    ('Table_6', ['Products', 'Domestic_Supply', 'Tourism_Ratio_Percent']),
    ('Table_7', ['Tourism_Industries', 'Full_Time_Equivalent_Jobs'])
]:
    table = tables.get(table_name)
    if table is not None:
        missing_cols = [col for col in required_cols if col not in table.columns]
        if missing_cols:
            structural_issues.append(f"{table_name}: Missing {missing_cols}")

# Data type validation
numeric_columns = {
    'Table_4': ['Internal_Tourism_Consumption'],
    'Table_6': ['Tourism_Ratio_Percent', 'Domestic_Supply'],
    'Table_7': ['Full_Time_Equivalent_Jobs']
}

for table_name, cols in numeric_columns.items():
    table = tables.get(table_name)
    if table is not None:
        for col in cols:
            if col in table.columns:
                non_numeric = pd.to_numeric(table[col], errors='coerce').isna().sum()
                if non_numeric > 0:
                    issues.append(f"{table_name}.{col}: {non_numeric} non-numeric values")
```

### 3. Data Quality Improvement Recommendations

#### Automated Recommendation Generation
```python
improvement_recommendations = []

# Based on validation score
if validation_score < 85:
    improvement_recommendations.extend([
        "📊 Implement data validation procedures before TSA compilation",
        "🔍 Review data collection methodology and sources",
        "📋 Establish quality control checkpoints in data processing"
    ])

# Based on specific issues
if consumption_pct_error > 1:
    improvement_recommendations.append(
        "🔄 Reconcile tourism consumption figures between Table 4 and Table 6"
    )

if len(extreme_ratios) > 0:
    improvement_recommendations.append(
        "🎯 Review products with extreme tourism ratios (>150%) for accuracy"
    )

if missing_values > 0:
    improvement_recommendations.append(
        "📝 Address missing values in core tables through improved data collection"
    )

# General recommendations
improvement_recommendations.extend([
    "📈 Establish regular data quality monitoring procedures",
    "🎓 Provide TSA methodology training for data compilers",
    "🤝 Improve coordination between data sources and NSO"
])
```

---

## 🔧 Technical Implementation

### Core Dependencies
```python
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')
```

### Session State Management
```python
# Initialize session state variables
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None
if 'tables' not in st.session_state:
    st.session_state.tables = None
if 'scenario_analyzer' not in st.session_state:
    st.session_state.scenario_analyzer = None
if 'country_params' not in st.session_state:
    st.session_state.country_params = {}
```

### Data Caching Strategy
```python
@st.cache_data
def load_tsa_from_excel(uploaded_file):
    """Cache Excel file loading to improve performance"""
    
@st.cache_data  
def validate_table_structure(tables):
    """Cache validation results"""
    
@st.cache_data
def calculate_core_aggregates(_analyzer):
    """Cache core calculations"""
```

### Error Handling
```python
try:
    # TSA analysis operations
    results = analyzer.calculate_core_aggregates()
except Exception as e:
    st.error(f"Analysis error: {str(e)}")
    st.info("Please check your data format and try again")
    
    # Detailed error logging
    import traceback
    with st.expander("Technical Details"):
        st.code(traceback.format_exc())
```

### Performance Optimization
- **Lazy Loading**: Only compute analyses when tabs are accessed
- **Data Caching**: Cache expensive calculations using `@st.cache_data`
- **Incremental Updates**: Update only changed components
- **Memory Management**: Clear large objects when not needed

### Export Capabilities
```python
# Report generation
def generate_executive_report(analyzer):
    report_content = f"""
    TOURISM SATELLITE ACCOUNT ANALYSIS REPORT
    ==========================================
    Country: {analyzer.country_name}
    Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}
    
    [Detailed report content...]
    """
    return report_content

# Download functionality
st.download_button(
    label="📥 Download Full Report",
    data=generate_executive_report(analyzer),
    file_name=f"TSA_Report_{analyzer.country_name}_{pd.Timestamp.now().strftime('%Y%m%d')}.txt",
    mime="text/plain"
)
```

---

## 📊 Visualization Standards

### Chart Types and Usage
- **Bar Charts**: Industry comparisons, product rankings
- **Pie Charts**: Market share, composition analysis
- **Line Charts**: Time series, scenario projections
- **Scatter Plots**: Productivity analysis, correlations
- **Heatmaps**: Cross-table comparisons (when applicable)

### Color Schemes
- **Green (`#2E8B57`)**: Positive indicators, good performance
- **Orange (`#FF8C00`)**: Moderate/warning indicators
- **Red (`#DC143C`)**: High risk, negative indicators
- **Blue (`#4169E1`)**: Neutral metrics, information

### Accessibility Standards
- High contrast ratios for text readability
- Color-blind friendly palettes
- Alternative text for visualizations
- Keyboard navigation support

---

## 🔗 International Standards Compliance

### UN TSA Framework 2008
- **Table Structure**: Follows RMF table specifications
- **Definitions**: Uses standard TSA concepts and terminology
- **Methodology**: Implements recommended calculation procedures
- **Aggregates**: Produces all required economic aggregates

### SNA 2008 Compatibility
- **Value Added**: Consistent with national accounts definitions
- **GDP Calculation**: Follows production approach methodology
- **Employment**: Uses standard labor statistics concepts

### OECD Guidelines
- **Tourism Industries**: Standard industry classification (ISIC Rev.4)
- **Tourism Products**: Standard product classification (CPC Ver.2.1)
- **Quality Standards**: Meets OECD data quality framework

This comprehensive specification document ensures the TSA Analysis Dashboard provides world-class tourism economic analysis capabilities while maintaining full compliance with international statistical standards.