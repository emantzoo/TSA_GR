import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="TSA Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling (minimal, Streamlit-native)
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff6b6b;
    }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA LOADING FUNCTIONS (Adapted for Streamlit)
# =============================================================================

@st.cache_data
def load_tsa_from_excel(uploaded_file):
    """Load TSA tables from uploaded Excel file"""
    try:
        excel_data = pd.read_excel(uploaded_file, sheet_name=None)
        
        required_tables = [
            'Table_1_Inbound_Expenditure',
            'Table_2_Domestic_Expenditure', 
            'Table_3_Outbound_Expenditure',
            'Table_4_Internal_Consumption',
            'Table_5_Production_Accounts',
            'Table_6_Supply_Demand_Core',
            'Table_7_Employment'
        ]
        
        tables = {}
        missing_tables = []
        
        for table_name in required_tables:
            if table_name in excel_data:
                tables[table_name] = excel_data[table_name]
            else:
                missing_tables.append(table_name)
        
        # Load optional tables
        optional_tables = [
            'Table_8_Capital_Formation',
            'Table_9_Collective_Consumption',
            'Table_10a_Trips_Overnights',
            'Table_10b_Transport_Arrivals',
            'Table_10c_Accommodation'
        ]
        
        for table_name in optional_tables:
            if table_name in excel_data:
                tables[table_name] = excel_data[table_name]
        
        return tables, missing_tables
        
    except Exception as e:
        st.error(f"Error loading Excel file: {str(e)}")
        return None, []

def validate_table_structure(tables):
    """Validate that loaded tables have correct structure"""
    validation_results = {}
    
    # Table 4 validation
    if 'Table_4_Internal_Consumption' in tables:
        table4 = tables['Table_4_Internal_Consumption']
        required_cols = ['Products', 'Internal_Tourism_Consumption']
        missing_cols = [col for col in required_cols if col not in table4.columns]
        validation_results['Table_4'] = "✅ Valid" if not missing_cols else f"❌ Missing: {missing_cols}"
    
    # Table 6 validation  
    if 'Table_6_Supply_Demand_Core' in tables:
        table6 = tables['Table_6_Supply_Demand_Core']
        required_cols = ['Products', 'Domestic_Supply', 'Internal_Tourism_Consumption', 'Tourism_Ratio_Percent']
        missing_cols = [col for col in required_cols if col not in table6.columns]
        validation_results['Table_6'] = "✅ Valid" if not missing_cols else f"❌ Missing: {missing_cols}"
    
    # Table 7 validation
    if 'Table_7_Employment' in tables:
        table7 = tables['Table_7_Employment']
        required_cols = ['Tourism_Industries', 'Full_Time_Equivalent_Jobs']
        missing_cols = [col for col in required_cols if col not in table7.columns]
        validation_results['Table_7'] = "✅ Valid" if not missing_cols else f"❌ Missing: {missing_cols}"
    
    return validation_results

# =============================================================================
# TSA ANALYZER CLASS (Streamlit Adapted)
# =============================================================================

class StreamlitTSAAnalyzer:
    """TSA Analyzer adapted for Streamlit interface"""
    
    def __init__(self, tables, country_params):
        self.tables = tables
        self.table4 = tables['Table_4_Internal_Consumption']
        self.table6 = tables['Table_6_Supply_Demand_Core'] 
        self.table7 = tables['Table_7_Employment']
        
        self.country_name = country_params.get('country_name', 'Country')
        self.total_gdp = country_params.get('total_gdp', 200000)
        self.total_employment = country_params.get('total_employment', 4000000)
        self.population = country_params.get('population', 10000000)
        
        self.core_aggregates = {}
        self.tourism_ratios = pd.DataFrame()
        self.employment_analysis = pd.DataFrame()
    
    def calculate_core_aggregates(self):
        """Calculate core TSA aggregates"""
        
        # Demand-side aggregates
        internal_tourism_consumption = self.table4['Internal_Tourism_Consumption'].sum()
        
        inbound_expenditure = 0
        domestic_expenditure = 0
        if 'Inbound_Tourism_Expenditure' in self.table4.columns:
            inbound_expenditure = self.table4['Inbound_Tourism_Expenditure'].sum()
        if 'Domestic_Tourism_Expenditure' in self.table4.columns:
            domestic_expenditure = self.table4['Domestic_Tourism_Expenditure'].sum()
        
        # Supply-side aggregates
        if 'GVA_Tourism_Share' in self.table7.columns:
            tourism_direct_gva = self.table7['GVA_Tourism_Share'].sum()
        else:
            tourism_ratios = self.table6['Tourism_Ratio_Percent'] / 100
            domestic_supply = self.table6['Domestic_Supply']
            estimated_gva_ratio = 0.4
            tourism_direct_gva = (tourism_ratios * domestic_supply * estimated_gva_ratio).sum()
        
        if 'Taxes_less_Subsidies' in self.table6.columns:
            tourism_taxes = (self.table6['Taxes_less_Subsidies'] * 
                            self.table6['Tourism_Ratio_Percent'] / 100).sum()
        else:
            tourism_taxes = tourism_direct_gva * 0.15
            
        tourism_direct_gdp = tourism_direct_gva + tourism_taxes
        
        # Employment aggregates
        total_tourism_fte = self.table7['Full_Time_Equivalent_Jobs'].sum()
        
        # Calculate ratios
        tourism_gdp_share = (tourism_direct_gdp / self.total_gdp) * 100
        tourism_employment_share = (total_tourism_fte / self.total_employment) * 100
        tourism_consumption_per_capita = internal_tourism_consumption / self.population
        
        self.core_aggregates = {
            'internal_tourism_consumption': internal_tourism_consumption,
            'inbound_expenditure': inbound_expenditure,
            'domestic_expenditure': domestic_expenditure,
            'tourism_direct_gva': tourism_direct_gva,
            'tourism_direct_gdp': tourism_direct_gdp,
            'tourism_taxes': tourism_taxes,
            'total_tourism_fte': total_tourism_fte,
            'tourism_gdp_share': tourism_gdp_share,
            'tourism_employment_share': tourism_employment_share,
            'tourism_consumption_per_capita': tourism_consumption_per_capita
        }
        
        return self.core_aggregates
    
    def analyze_tourism_ratios(self):
        """Analyze tourism ratios by product"""
        
        self.tourism_ratios = pd.DataFrame({
            'Product': self.table6['Products'],
            'Tourism_Ratio': self.table6['Tourism_Ratio_Percent'],
            'Internal_Tourism_Consumption': self.table6['Internal_Tourism_Consumption'],
            'Domestic_Supply': self.table6['Domestic_Supply']
        })
        
        # Categorize by tourism intensity
        self.tourism_ratios['Tourism_Intensity'] = pd.cut(
            self.tourism_ratios['Tourism_Ratio'], 
            bins=[0, 10, 30, 50, 100, 200],
            labels=['Very Low (<10%)', 'Low (10-30%)', 'Medium (30-50%)', 
                   'High (50-100%)', 'Very High (>100%)']
        )
        
        self.tourism_ratios = self.tourism_ratios.sort_values('Tourism_Ratio', ascending=False)
        return self.tourism_ratios
    
    def analyze_employment_structure(self):
        """Analyze employment structure by industry"""
        
        self.employment_analysis = self.table7.copy()
        
        self.employment_analysis['Employment_Share'] = (
            self.employment_analysis['Full_Time_Equivalent_Jobs'] / 
            self.employment_analysis['Full_Time_Equivalent_Jobs'].sum() * 100
        )
        
        if 'GVA_Tourism_Share' in self.employment_analysis.columns:
            self.employment_analysis['Labor_Productivity'] = (
                self.employment_analysis['GVA_Tourism_Share'] / 
                self.employment_analysis['Full_Time_Equivalent_Jobs'] * 1000
            )
        
        self.employment_analysis = self.employment_analysis.sort_values(
            'Employment_Share', ascending=False
        )
        
        return self.employment_analysis
    
    def validate_supply_demand_balance(self):
        """Validate supply-demand balance"""
        
        validation_score = 100
        issues = []
        
        # Tourism consumption consistency
        table4_total = self.table4['Internal_Tourism_Consumption'].sum()
        table6_total = self.table6['Internal_Tourism_Consumption'].sum()
        consumption_discrepancy = abs(table4_total - table6_total)
        consumption_pct_error = (consumption_discrepancy / table4_total * 100) if table4_total > 0 else 0
        
        if consumption_pct_error > 1:
            validation_score -= 25
            issues.append(f"Tourism consumption inconsistency: {consumption_pct_error:.2f}%")
        
        # Tourism ratios reasonableness
        extreme_ratios = self.table6[self.table6['Tourism_Ratio_Percent'] > 150]
        if len(extreme_ratios) > 0:
            validation_score -= 30
            issues.append(f"{len(extreme_ratios)} products have extreme ratios (>150%)")
        
        # Data completeness
        table4_missing = self.table4['Internal_Tourism_Consumption'].isna().sum()
        table6_missing = self.table6['Tourism_Ratio_Percent'].isna().sum()
        table7_missing = self.table7['Full_Time_Equivalent_Jobs'].isna().sum()
        total_missing = table4_missing + table6_missing + table7_missing
        
        if total_missing > 0:
            validation_score -= min(20, total_missing * 2)
            issues.append(f"{total_missing} missing values found")
        
        return validation_score, issues

# =============================================================================
# SCENARIO ANALYSIS (Streamlit Adapted)
# =============================================================================

class StreamlitScenarioAnalyzer:
    """Scenario analyzer adapted for Streamlit"""
    
    def __init__(self, base_analyzer):
        self.base_analyzer = base_analyzer
        self.base_aggregates = base_analyzer.core_aggregates
        self.scenarios = {}
    
    def create_growth_scenarios(self, years_ahead=5):
        """Create growth scenarios"""
        
        scenarios = {
            'pessimistic': {'annual_growth_rate': 0.01, 'employment_elasticity': 0.8},
            'realistic': {'annual_growth_rate': 0.04, 'employment_elasticity': 0.9},
            'optimistic': {'annual_growth_rate': 0.07, 'employment_elasticity': 1.1}
        }
        
        base_consumption = self.base_aggregates['internal_tourism_consumption']
        base_employment = self.base_aggregates['total_tourism_fte']
        base_gdp = self.base_aggregates['tourism_direct_gdp']
        
        growth_results = {}
        
        for scenario_name, params in scenarios.items():
            yearly_projections = []
            
            for year in range(1, years_ahead + 1):
                projected_consumption = base_consumption * ((1 + params['annual_growth_rate']) ** year)
                employment_growth_rate = params['annual_growth_rate'] * params['employment_elasticity']
                projected_employment = base_employment * ((1 + employment_growth_rate) ** year)
                projected_gdp = base_gdp * ((1 + params['annual_growth_rate']) ** year)
                
                yearly_projections.append({
                    'year': 2024 + year,
                    'tourism_consumption': projected_consumption,
                    'tourism_employment': projected_employment,
                    'tourism_gdp': projected_gdp
                })
            
            growth_results[scenario_name] = yearly_projections
        
        self.scenarios['growth_scenarios'] = growth_results
        return growth_results
    
    def analyze_policy_interventions(self):
        """Analyze policy intervention impacts"""
        
        policy_scenarios = {
            'marketing_boost': {
                'gdp_impact': 0.15,
                'employment_impact': 0.10,
                'investment_cost': 50,
                'description': 'Intensive international marketing campaign'
            },
            'infrastructure_investment': {
                'gdp_impact': 0.25,
                'employment_impact': 0.20,
                'investment_cost': 500,
                'description': 'Major tourism infrastructure development'
            },
            'skills_development': {
                'gdp_impact': 0.20,
                'employment_impact': 0.05,
                'investment_cost': 200,
                'description': 'Comprehensive workforce training program'
            },
            'digital_transformation': {
                'gdp_impact': 0.18,
                'employment_impact': -0.05,
                'investment_cost': 150,
                'description': 'Tourism sector digitalization initiative'
            }
        }
        
        base_gdp = self.base_aggregates['tourism_direct_gdp']
        
        policy_results = {}
        for policy_name, params in policy_scenarios.items():
            new_gdp = base_gdp * (1 + params['gdp_impact'])
            gdp_increase = new_gdp - base_gdp
            roi = (gdp_increase * 1000) / params['investment_cost']
            
            policy_results[policy_name] = {
                'description': params['description'],
                'gdp_change': params['gdp_impact'] * 100,
                'employment_change': params['employment_impact'] * 100,
                'investment_cost': params['investment_cost'],
                'roi': roi,
                'gdp_increase': gdp_increase
            }
        
        self.scenarios['policy_interventions'] = policy_results
        return policy_results

# =============================================================================
# STREAMLIT APP MAIN INTERFACE
# =============================================================================

def main():
    """Main Streamlit application"""
    
    # Sidebar navigation
    st.sidebar.title("🏛️ TSA Analysis Dashboard")
    st.sidebar.markdown("---")
    
    # Initialize session state
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = None
    if 'tables' not in st.session_state:
        st.session_state.tables = None
    if 'scenario_analyzer' not in st.session_state:
        st.session_state.scenario_analyzer = None
    if 'params' not in st.session_state:
        st.session_state.params = {
            'country_name': 'Country',
            'total_gdp': 200000,
            'total_employment': 4000000,
            'population': 10000000
        }
    
    # Navigation
    pages = {
        "🏠 Home & Data Upload": "home",
        "📊 Core Analysis": "core_analysis", 
        "🎯 Tourism Ratios": "tourism_ratios",
        "👥 Employment Analysis": "employment",
        "🔮 Scenario Analysis": "scenarios",
        "📋 Executive Summary": "summary",
        "✅ Data Validation": "validation"
    }
    
    selected_page = st.sidebar.selectbox("Navigate to:", list(pages.keys()))
    page_key = pages[selected_page]
    
    # Main content area
    if page_key == "home":
        show_home_page()
    elif page_key == "core_analysis":
        show_core_analysis()
    elif page_key == "tourism_ratios":
        show_tourism_ratios()
    elif page_key == "employment":
        show_employment_analysis()
    elif page_key == "scenarios":
        show_scenario_analysis()
    elif page_key == "summary":
        show_executive_summary()
    elif page_key == "validation":
        show_data_validation()

def show_home_page():
    """Home page with data upload"""
    
    st.markdown('<h1 class="main-header">🏛️ Tourism Satellite Account Analysis Dashboard</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    ### Welcome to the TSA Analysis System
    This dashboard provides comprehensive analysis of Tourism Satellite Account data based on the UN TSA Framework 2008.
    
    **Key Features:**
    - 📊 Core economic aggregates analysis
    - 🎯 Tourism ratios and intensity analysis  
    - 👥 Employment structure analysis
    - 🔮 Scenario modeling and forecasting
    - ✅ Data validation and quality assessment
    - 📋 Executive summary generation
    """)
    
    st.markdown("---")
    
    # Data upload section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📁 Upload TSA Data")
        
        uploaded_file = st.file_uploader(
            "Upload Excel file with TSA tables",
            type=['xlsx', 'xls'],
            help="Excel file should contain TSA tables as separate sheets"
        )
        
        if uploaded_file is not None:
            with st.spinner("Loading TSA tables..."):
                tables, missing_tables = load_tsa_from_excel(uploaded_file)
                
                if tables:
                    st.session_state.tables = tables
                    
                    st.success(f"✅ Successfully loaded {len(tables)} TSA tables!")
                    
                    # Show loaded tables
                    st.subheader("Loaded Tables:")
                    for table_name in tables.keys():
                        rows = len(tables[table_name])
                        st.write(f"✅ {table_name}: {rows} rows")
                    
                    if missing_tables:
                        st.warning(f"Missing tables: {', '.join(missing_tables)}")
                    
                    # Validate table structure
                    validation_results = validate_table_structure(tables)
                    
                    st.subheader("Table Structure Validation:")
                    for table, result in validation_results.items():
                        st.write(f"{table}: {result}")
                else:
                    st.error("Failed to load tables. Please check your file format.")
    
    with col2:
        st.subheader("🌍 Country Parameters")
        
        # Initialize default parameters if not set
        if 'params' not in st.session_state:
            st.session_state.params = {
                'country_name': 'Country',
                'total_gdp': 200000,
                'total_employment': 4000000,
                'population': 10000000
            }
        
        with st.form("country_params_form"):
            country_name = st.text_input("Country Name", value=st.session_state.params['country_name'])
            total_gdp = st.number_input("Total GDP (€ millions)", value=st.session_state.params['total_gdp'], min_value=1000)
            total_employment = st.number_input("Total Employment (FTE)", value=st.session_state.params['total_employment'], min_value=100000)
            population = st.number_input("Population", value=st.session_state.params['population'], min_value=100000)
            
            submitted = st.form_submit_button("Set Parameters")
            
            if submitted:
                st.session_state.params = {
                    'country_name': country_name,
                    'total_gdp': total_gdp,
                    'total_employment': total_employment,
                    'population': population
                }
                st.success("✅ Country parameters set!")
    
    # Initialize analyzer
    if st.session_state.tables is not None and 'params' in st.session_state:
        if st.button("🚀 Initialize TSA Analyzer", type="primary"):
            with st.spinner("Initializing analyzer..."):
                analyzer = StreamlitTSAAnalyzer(
                    st.session_state.tables, 
                    st.session_state.params
                )
                
                # Run core calculations
                analyzer.calculate_core_aggregates()
                analyzer.analyze_tourism_ratios()
                analyzer.analyze_employment_structure()
                
                st.session_state.analyzer = analyzer
                st.success("✅ TSA Analyzer initialized! Navigate to other pages for analysis.")

def show_core_analysis():
    """Core aggregates analysis page"""
    
    if st.session_state.analyzer is None:
        st.warning("Please upload data and initialize the analyzer first.")
        return
    
    analyzer = st.session_state.analyzer
    aggregates = analyzer.core_aggregates
    
    st.title("📊 Core TSA Aggregates Analysis")
    st.subheader(f"Country: {analyzer.country_name}")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Tourism GDP Share",
            f"{aggregates['tourism_gdp_share']:.1f}%",
            help="Tourism's contribution to total GDP"
        )
    
    with col2:
        st.metric(
            "Tourism Employment Share", 
            f"{aggregates['tourism_employment_share']:.1f}%",
            help="Tourism's share of total employment"
        )
    
    with col3:
        st.metric(
            "Tourism GDP",
            f"€{aggregates['tourism_direct_gdp']:,.0f}M",
            help="Tourism direct contribution to GDP"
        )
    
    with col4:
        st.metric(
            "Tourism Employment",
            f"{aggregates['total_tourism_fte']:,.0f}",
            help="Full-time equivalent tourism jobs"
        )
    
    st.markdown("---")
    
    # Detailed breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Demand Side Analysis")
        
        demand_data = {
            'Component': ['Internal Tourism Consumption', 'Inbound Expenditure', 'Domestic Expenditure'],
            'Value (€M)': [
                aggregates['internal_tourism_consumption'],
                aggregates['inbound_expenditure'], 
                aggregates['domestic_expenditure']
            ]
        }
        
        if demand_data['Value (€M)'][1] > 0 or demand_data['Value (€M)'][2] > 0:
            fig = px.pie(
                values=demand_data['Value (€M)'][1:],
                names=demand_data['Component'][1:],
                title="Tourism Expenditure Breakdown"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(pd.DataFrame(demand_data), hide_index=True)
    
    with col2:
        st.subheader("Supply Side Analysis")
        
        supply_data = {
            'Component': ['Tourism Direct GVA', 'Tourism Taxes', 'Tourism Direct GDP'],
            'Value (€M)': [
                aggregates['tourism_direct_gva'],
                aggregates['tourism_taxes'],
                aggregates['tourism_direct_gdp']
            ]
        }
        
        fig = px.bar(
            x=supply_data['Component'],
            y=supply_data['Value (€M)'],
            title="Tourism GDP Components"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(pd.DataFrame(supply_data), hide_index=True)
    
    # Tourism consumption per capita
    st.subheader("Additional Indicators")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Tourism Consumption per Capita",
            f"€{aggregates['tourism_consumption_per_capita']:,.0f}",
            help="Annual tourism consumption per resident"
        )
    
    with col2:
        gdp_intensity = aggregates['tourism_direct_gdp'] / aggregates['total_tourism_fte'] * 1000
        st.metric(
            "GDP per Tourism Job",
            f"€{gdp_intensity:,.0f}",
            help="Tourism GDP per FTE job"
        )
    
    with col3:
        tourism_multiplier = aggregates['internal_tourism_consumption'] / aggregates['tourism_direct_gdp']
        st.metric(
            "Tourism Multiplier",
            f"{tourism_multiplier:.2f}",
            help="Consumption to GDP ratio"
        )

def show_tourism_ratios():
    """Tourism ratios analysis page"""
    
    if st.session_state.analyzer is None:
        st.warning("Please upload data and initialize the analyzer first.")
        return
    
    analyzer = st.session_state.analyzer
    ratios_df = analyzer.tourism_ratios
    
    st.title("🎯 Tourism Ratios Analysis")
    st.subheader(f"Country: {analyzer.country_name}")
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Products Analyzed", len(ratios_df))
    
    with col2:
        avg_ratio = ratios_df['Tourism_Ratio'].mean()
        st.metric("Average Tourism Ratio", f"{avg_ratio:.1f}%")
    
    with col3:
        high_ratio_products = (ratios_df['Tourism_Ratio'] > 50).sum()
        st.metric("High Intensity Products (>50%)", high_ratio_products)
    
    with col4:
        max_ratio = ratios_df['Tourism_Ratio'].max()
        st.metric("Highest Tourism Ratio", f"{max_ratio:.1f}%")
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 10 Products by Tourism Ratio")
        
        top_ratios = ratios_df.head(10)
        
        fig = px.bar(
            top_ratios,
            x='Tourism_Ratio',
            y='Product',
            orientation='h',
            color='Tourism_Ratio',
            color_continuous_scale='RdYlGn_r',
            title="Tourism Intensity by Product"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Tourism Intensity Distribution")
        
        intensity_counts = ratios_df['Tourism_Intensity'].value_counts()
        
        fig = px.pie(
            values=intensity_counts.values,
            names=intensity_counts.index,
            title="Distribution of Tourism Intensity Levels"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed table
    st.subheader("Detailed Tourism Ratios")
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        min_ratio = st.slider("Minimum Tourism Ratio (%)", 0, 200, 0)
    
    with col2:
        intensity_filter = st.selectbox(
            "Filter by Intensity", 
            ['All'] + list(ratios_df['Tourism_Intensity'].cat.categories)
        )
    
    # Apply filters
    filtered_df = ratios_df[ratios_df['Tourism_Ratio'] >= min_ratio]
    
    if intensity_filter != 'All':
        filtered_df = filtered_df[filtered_df['Tourism_Intensity'] == intensity_filter]
    
    st.dataframe(
        filtered_df[['Product', 'Tourism_Ratio', 'Internal_Tourism_Consumption', 'Tourism_Intensity']],
        use_container_width=True
    )
    
    # Supply vs Tourism Consumption
    st.subheader("Supply vs Tourism Consumption")
    
    top_products = ratios_df.head(8)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Domestic Supply',
        x=top_products['Product'],
        y=top_products['Domestic_Supply'],
        opacity=0.7
    ))
    
    fig.add_trace(go.Bar(
        name='Tourism Consumption',
        x=top_products['Product'],
        y=top_products['Internal_Tourism_Consumption'],
        opacity=0.7
    ))
    
    fig.update_layout(
        title="Supply vs Tourism Consumption (Top 8 Products)",
        xaxis_title="Products",
        yaxis_title="Value (€ millions)",
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_employment_analysis():
    """Employment analysis page"""
    
    if st.session_state.analyzer is None:
        st.warning("Please upload data and initialize the analyzer first.")
        return
    
    analyzer = st.session_state.analyzer
    emp_df = analyzer.employment_analysis
    
    st.title("👥 Tourism Employment Analysis")
    st.subheader(f"Country: {analyzer.country_name}")
    
    # Key employment metrics
    total_fte = emp_df['Full_Time_Equivalent_Jobs'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Tourism Industries", len(emp_df))
    
    with col2:
        st.metric("Total FTE Employment", f"{total_fte:,.0f}")
    
    with col3:
        top_industry_share = emp_df.iloc[0]['Employment_Share']
        st.metric("Largest Industry Share", f"{top_industry_share:.1f}%")
    
    with col4:
        if 'Labor_Productivity' in emp_df.columns:
            avg_productivity = emp_df['Labor_Productivity'].mean()
            st.metric("Avg Labor Productivity", f"€{avg_productivity:,.0f}")
    
    st.markdown("---")
    
    # Employment by industry
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Employment by Tourism Industry")
        
        top_industries = emp_df.head(8)
        
        fig = px.bar(
            top_industries,
            x='Employment_Share',
            y='Tourism_Industries',
            orientation='h',
            color='Employment_Share',
            color_continuous_scale='Blues',
            title="Employment Share by Industry"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Employment Concentration")
        
        # Calculate concentration metrics
        top_3_share = emp_df.head(3)['Employment_Share'].sum()
        top_5_share = emp_df.head(5)['Employment_Share'].sum()
        
        concentration_data = {
            'Metric': ['Top 3 Industries', 'Top 5 Industries', 'Remaining Industries'],
            'Share': [top_3_share, top_5_share - top_3_share, 100 - top_5_share]
        }
        
        fig = px.pie(
            values=concentration_data['Share'],
            names=concentration_data['Metric'],
            title="Employment Concentration"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed employment table
    st.subheader("Detailed Employment Analysis")
    
    # Display columns based on available data
    display_columns = ['Tourism_Industries', 'Full_Time_Equivalent_Jobs', 'Employment_Share']
    
    if 'Labor_Productivity' in emp_df.columns:
        display_columns.append('Labor_Productivity')
    if 'Number_of_Establishments' in emp_df.columns:
        display_columns.append('Number_of_Establishments')
    
    st.dataframe(
        emp_df[display_columns].round(2),
        use_container_width=True
    )
    
    # Employment vs GDP relationship
    if 'Labor_Productivity' in emp_df.columns:
        st.subheader("Employment vs Productivity Analysis")
        
        fig = px.scatter(
            emp_df,
            x='Full_Time_Equivalent_Jobs',
            y='Labor_Productivity',
            size='Employment_Share',
            hover_name='Tourism_Industries',
            title="Employment vs Labor Productivity",
            labels={
                'Full_Time_Equivalent_Jobs': 'FTE Jobs',
                'Labor_Productivity': 'Labor Productivity (€000/FTE)'
            }
        )
        st.plotly_chart(fig, use_container_width=True)

def show_scenario_analysis():
    """Scenario analysis page"""
    
    if st.session_state.analyzer is None:
        st.warning("Please upload data and initialize the analyzer first.")
        return
    
    analyzer = st.session_state.analyzer
    
    st.title("🔮 Scenario Analysis & Forecasting")
    st.subheader(f"Country: {analyzer.country_name}")
    
    # Initialize scenario analyzer
    if st.session_state.scenario_analyzer is None:
        st.session_state.scenario_analyzer = StreamlitScenarioAnalyzer(analyzer)
    
    scenario_analyzer = st.session_state.scenario_analyzer
    
    # Tabs for different scenario types
    tab1, tab2, tab3 = st.tabs(["📈 Growth Scenarios", "🏛️ Policy Interventions", "📊 Sensitivity Analysis"])
    
    with tab1:
        st.subheader("Tourism Growth Scenarios")
        
        years_ahead = st.slider("Forecast Period (years)", 3, 10, 5)
        
        if st.button("Generate Growth Scenarios"):
            with st.spinner("Creating growth scenarios..."):
                growth_results = scenario_analyzer.create_growth_scenarios(years_ahead)
                
                # Visualize growth scenarios
                scenario_data = []
                
                for scenario_name, projections in growth_results.items():
                    for proj in projections:
                        scenario_data.append({
                            'Year': proj['year'],
                            'Scenario': scenario_name.title(),
                            'Tourism_GDP': proj['tourism_gdp'],
                            'Tourism_Employment': proj['tourism_employment'],
                            'Tourism_Consumption': proj['tourism_consumption']
                        })
                
                scenario_df = pd.DataFrame(scenario_data)
                
                # GDP projection chart
                fig = px.line(
                    scenario_df,
                    x='Year',
                    y='Tourism_GDP',
                    color='Scenario',
                    title="Tourism GDP Growth Projections",
                    labels={'Tourism_GDP': 'Tourism GDP (€ millions)'}
                )
                
                # Add current year baseline
                current_gdp = analyzer.core_aggregates['tourism_direct_gdp']
                fig.add_hline(y=current_gdp, line_dash="dash", 
                             annotation_text="Current GDP", annotation_position="bottom right")
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Employment projection chart
                fig = px.line(
                    scenario_df,
                    x='Year',
                    y='Tourism_Employment',
                    color='Scenario',
                    title="Tourism Employment Growth Projections",
                    labels={'Tourism_Employment': 'Tourism Employment (FTE)'}
                )
                
                current_employment = analyzer.core_aggregates['total_tourism_fte']
                fig.add_hline(y=current_employment, line_dash="dash",
                             annotation_text="Current Employment", annotation_position="bottom right")
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Summary table
                st.subheader("Growth Scenario Summary")
                
                summary_data = []
                for scenario_name, projections in growth_results.items():
                    final_year = projections[-1]
                    gdp_growth = ((final_year['tourism_gdp'] / current_gdp) - 1) * 100
                    emp_growth = ((final_year['tourism_employment'] / current_employment) - 1) * 100
                    
                    summary_data.append({
                        'Scenario': scenario_name.title(),
                        f'{years_ahead}-Year GDP Growth (%)': f"{gdp_growth:.1f}%",
                        f'{years_ahead}-Year Employment Growth (%)': f"{emp_growth:.1f}%",
                        f'Final GDP (€M)': f"{final_year['tourism_gdp']:,.0f}",
                        f'Final Employment': f"{final_year['tourism_employment']:,.0f}"
                    })
                
                st.dataframe(pd.DataFrame(summary_data), hide_index=True)
    
    with tab2:
        st.subheader("Policy Intervention Analysis")
        
        if st.button("Analyze Policy Interventions"):
            with st.spinner("Analyzing policy impacts..."):
                policy_results = scenario_analyzer.analyze_policy_interventions()
                
                # Policy comparison chart
                policies = list(policy_results.keys())
                roi_values = [policy_results[p]['roi'] for p in policies]
                gdp_changes = [policy_results[p]['gdp_change'] for p in policies]
                investment_costs = [policy_results[p]['investment_cost'] for p in policies]
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='ROI',
                    x=[p.replace('_', ' ').title() for p in policies],
                    y=roi_values,
                    yaxis='y',
                    marker_color='lightblue'
                ))
                
                fig.add_trace(go.Scatter(
                    name='GDP Change (%)',
                    x=[p.replace('_', ' ').title() for p in policies],
                    y=gdp_changes,
                    yaxis='y2',
                    mode='markers+lines',
                    marker_color='red',
                    marker_size=10
                ))
                
                fig.update_layout(
                    title="Policy Intervention Analysis",
                    xaxis_title="Policy Intervention",
                    yaxis=dict(title="Return on Investment (x)", side="left"),
                    yaxis2=dict(title="GDP Change (%)", side="right", overlaying="y"),
                    hovermode='x'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Policy details table
                st.subheader("Policy Intervention Details")
                
                policy_table_data = []
                for policy_name, data in policy_results.items():
                    policy_table_data.append({
                        'Policy': policy_name.replace('_', ' ').title(),
                        'Description': data['description'],
                        'GDP Change (%)': f"{data['gdp_change']:+.1f}%",
                        'Employment Change (%)': f"{data['employment_change']:+.1f}%",
                        'Investment Cost (€M)': f"{data['investment_cost']:.0f}",
                        'ROI': f"{data['roi']:.1f}x"
                    })
                
                st.dataframe(pd.DataFrame(policy_table_data), hide_index=True)
                
                # Recommendations
                st.subheader("Policy Recommendations")
                
                best_roi_policy = max(policy_results.items(), key=lambda x: x[1]['roi'])
                best_gdp_policy = max(policy_results.items(), key=lambda x: x[1]['gdp_change'])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.success(f"**Highest ROI**: {best_roi_policy[0].replace('_', ' ').title()}")
                    st.write(f"ROI: {best_roi_policy[1]['roi']:.1f}x")
                    st.write(f"GDP Impact: {best_roi_policy[1]['gdp_change']:+.1f}%")
                
                with col2:
                    st.info(f"**Highest GDP Impact**: {best_gdp_policy[0].replace('_', ' ').title()}")
                    st.write(f"GDP Impact: {best_gdp_policy[1]['gdp_change']:+.1f}%")
                    st.write(f"ROI: {best_gdp_policy[1]['roi']:.1f}x")
    
    with tab3:
        st.subheader("Sensitivity Analysis")
        st.write("Analyze how changes in key parameters affect tourism outcomes.")
        
        # Parameter selection
        col1, col2 = st.columns(2)
        
        with col1:
            param_change = st.slider("Parameter Change (%)", -30, 30, 10)
        
        with col2:
            parameter = st.selectbox(
                "Select Parameter",
                ["Tourism Ratios", "Labor Productivity", "Inbound Share", "Exchange Rate"]
            )
        
        if st.button("Run Sensitivity Analysis"):
            base_gdp = analyzer.core_aggregates['tourism_direct_gdp']
            base_employment = analyzer.core_aggregates['total_tourism_fte']
            
            # Simple sensitivity calculation
            if parameter == "Tourism Ratios":
                new_gdp = base_gdp * (1 + param_change / 100)
                new_employment = base_employment
            elif parameter == "Labor Productivity":
                new_gdp = base_gdp * (1 + param_change / 100)
                new_employment = base_employment
            elif parameter == "Inbound Share":
                new_gdp = base_gdp * (1 + param_change / 200)  # 50% effect
                new_employment = base_employment * (1 + param_change / 300)  # 33% effect
            else:  # Exchange Rate
                new_gdp = base_gdp * (1 + param_change / 150)  # 67% effect
                new_employment = base_employment * (1 + param_change / 400)  # 25% effect
            
            gdp_change = ((new_gdp - base_gdp) / base_gdp) * 100
            emp_change = ((new_employment - base_employment) / base_employment) * 100
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Parameter Change", f"{param_change:+.0f}%")
            
            with col2:
                st.metric("GDP Impact", f"{gdp_change:+.1f}%")
            
            with col3:
                st.metric("Employment Impact", f"{emp_change:+.1f}%")
            
            st.write(f"**Interpretation**: A {param_change:+.0f}% change in {parameter.lower()} "
                    f"results in a {gdp_change:+.1f}% change in tourism GDP and "
                    f"a {emp_change:+.1f}% change in employment.")

def show_executive_summary():
    """Executive summary page"""
    
    if st.session_state.analyzer is None:
        st.warning("Please upload data and initialize the analyzer first.")
        return
    
    analyzer = st.session_state.analyzer
    aggregates = analyzer.core_aggregates
    
    st.title("📋 Executive Summary")
    st.subheader(f"Tourism Satellite Account Analysis - {analyzer.country_name}")
    
    # Key performance indicators
    st.subheader("🎯 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Tourism GDP Contribution",
            f"€{aggregates['tourism_direct_gdp']:,.0f}M",
            f"{aggregates['tourism_gdp_share']:.1f}% of total GDP"
        )
    
    with col2:
        st.metric(
            "Tourism Employment",
            f"{aggregates['total_tourism_fte']:,.0f} jobs",
            f"{aggregates['tourism_employment_share']:.1f}% of total employment"
        )
    
    with col3:
        st.metric(
            "Tourism Consumption",
            f"€{aggregates['internal_tourism_consumption']:,.0f}M",
            f"€{aggregates['tourism_consumption_per_capita']:,.0f} per capita"
        )
    
    with col4:
        avg_ratio = analyzer.tourism_ratios['Tourism_Ratio'].mean()
        st.metric(
            "Average Tourism Ratio",
            f"{avg_ratio:.1f}%",
            "Across all products"
        )
    
    st.markdown("---")
    
    # Executive insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Economic Significance")
        
        gdp_share = aggregates['tourism_gdp_share']
        emp_share = aggregates['tourism_employment_share']
        
        if gdp_share > 10:
            significance = "High"
            color = "🔴"
        elif gdp_share > 5:
            significance = "Moderate"
            color = "🟡"
        else:
            significance = "Low"
            color = "🟢"
        
        st.write(f"{color} **Economic Importance**: {significance}")
        st.write(f"Tourism contributes {gdp_share:.1f}% to GDP and supports {emp_share:.1f}% of employment.")
        
        if gdp_share > 15:
            st.warning("⚠️ High tourism dependency - consider diversification strategies")
        elif gdp_share < 3:
            st.info("ℹ️ Tourism sector has growth potential")
        else:
            st.success("✅ Balanced tourism development")
    
    with col2:
        st.subheader("🏗️ Industry Structure")
        
        top_industry = analyzer.employment_analysis.iloc[0]
        top_product = analyzer.tourism_ratios.iloc[0]
        
        st.write(f"**Leading employment industry**: {top_industry['Tourism_Industries']}")
        st.write(f"Share: {top_industry['Employment_Share']:.1f}% of tourism jobs")
        
        st.write(f"**Highest tourism intensity**: {top_product['Product']}")
        st.write(f"Tourism ratio: {top_product['Tourism_Ratio']:.1f}%")
        
        # Industry concentration
        top_3_share = analyzer.employment_analysis.head(3)['Employment_Share'].sum()
        if top_3_share > 70:
            st.warning(f"⚠️ High concentration: Top 3 industries = {top_3_share:.1f}%")
        else:
            st.success(f"✅ Diversified structure: Top 3 industries = {top_3_share:.1f}%")
    
    # Key findings
    st.subheader("💡 Key Findings & Recommendations")
    
    findings = []
    
    # Economic impact finding
    if aggregates['tourism_gdp_share'] > 10:
        findings.append("🔍 **High Economic Impact**: Tourism is a major economic driver with significant GDP and employment contributions.")
    elif aggregates['tourism_gdp_share'] < 3:
        findings.append("🔍 **Growth Opportunity**: Tourism sector shows potential for expansion and development.")
    else:
        findings.append("🔍 **Balanced Development**: Tourism maintains a healthy contribution to the economy.")
    
    # Employment finding
    productivity = aggregates['tourism_direct_gdp'] / aggregates['total_tourism_fte'] * 1000
    if productivity > 80:
        findings.append("💼 **High Productivity**: Tourism sector demonstrates strong labor productivity.")
    else:
        findings.append("💼 **Productivity Focus**: Opportunities exist to improve tourism labor productivity.")
    
    # Tourism ratios finding
    high_ratio_products = (analyzer.tourism_ratios['Tourism_Ratio'] > 100).sum()
    if high_ratio_products > 5:
        findings.append("📈 **High Tourism Intensity**: Multiple products show very high tourism dependency.")
    elif high_ratio_products == 0:
        findings.append("📈 **Balanced Tourism Ratios**: No products show extreme tourism dependency.")
    else:
        findings.append("📈 **Moderate Intensity**: Some products show high tourism specialization.")
    
    for finding in findings:
        st.write(finding)
    
    # Recommendations
    st.subheader("🎯 Strategic Recommendations")
    
    recommendations = []
    
    # Based on GDP share
    if aggregates['tourism_gdp_share'] > 15:
        recommendations.append("🛡️ **Diversification Strategy**: Reduce tourism dependency through economic diversification")
        recommendations.append("💾 **Crisis Preparedness**: Develop robust crisis response and recovery plans")
    elif aggregates['tourism_gdp_share'] < 5:
        recommendations.append("🚀 **Growth Strategy**: Invest in tourism infrastructure and marketing to capture potential")
        recommendations.append("📊 **Market Development**: Focus on developing new tourism products and markets")
    
    # Based on employment concentration
    top_3_employment = analyzer.employment_analysis.head(3)['Employment_Share'].sum()
    if top_3_employment > 70:
        recommendations.append("🌐 **Industry Diversification**: Develop broader range of tourism industries")
    
    # Based on productivity
    if productivity < 60:
        recommendations.append("🎓 **Skills Development**: Invest in workforce training and capacity building")
        recommendations.append("💻 **Technology Adoption**: Implement digital solutions to improve efficiency")
    
    # Universal recommendations
    recommendations.extend([
        "📈 **Continuous Monitoring**: Implement regular TSA updates for policy guidance",
        "🌱 **Sustainable Development**: Balance tourism growth with environmental protection"
    ])
    
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")
    
    # Download report
    st.markdown("---")
    
    if st.button("📄 Generate Detailed Report"):
        # Create a comprehensive text report
        report_content = f"""
TOURISM SATELLITE ACCOUNT EXECUTIVE SUMMARY
Country: {analyzer.country_name}
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}

KEY PERFORMANCE INDICATORS
==========================
Tourism GDP Contribution: €{aggregates['tourism_direct_gdp']:,.0f} million ({aggregates['tourism_gdp_share']:.1f}% of total GDP)
Tourism Employment: {aggregates['total_tourism_fte']:,.0f} FTE jobs ({aggregates['tourism_employment_share']:.1f}% of total employment)
Tourism Consumption: €{aggregates['internal_tourism_consumption']:,.0f} million (€{aggregates['tourism_consumption_per_capita']:,.0f} per capita)
Average Tourism Ratio: {avg_ratio:.1f}%

ECONOMIC STRUCTURE
==================
Products Analyzed: {len(analyzer.tourism_ratios)}
Tourism Industries: {len(analyzer.employment_analysis)}
Top Employment Industry: {analyzer.employment_analysis.iloc[0]['Tourism_Industries']} ({analyzer.employment_analysis.iloc[0]['Employment_Share']:.1f}%)
Highest Tourism Intensity: {analyzer.tourism_ratios.iloc[0]['Product']} ({analyzer.tourism_ratios.iloc[0]['Tourism_Ratio']:.1f}%)

KEY FINDINGS
============
{chr(10).join(['- ' + finding.replace('🔍 ', '').replace('💼 ', '').replace('📈 ', '') for finding in findings])}

STRATEGIC RECOMMENDATIONS
=========================
{chr(10).join([f"{i}. {rec.split(' ', 1)[1] if ' ' in rec else rec}" for i, rec in enumerate(recommendations, 1)])}
"""
        
        st.download_button(
            label="📥 Download Executive Summary",
            data=report_content,
            file_name=f"TSA_Executive_Summary_{analyzer.country_name}_{pd.Timestamp.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

def show_data_validation():
    """Data validation page"""
    
    if st.session_state.analyzer is None:
        st.warning("Please upload data and initialize the analyzer first.")
        return
    
    analyzer = st.session_state.analyzer
    
    st.title("✅ Data Validation & Quality Assessment")
    st.subheader(f"Country: {analyzer.country_name}")
    
    # Run validation
    validation_score, issues = analyzer.validate_supply_demand_balance()
    
    # Validation score display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if validation_score >= 90:
            st.success(f"**Validation Score**: {validation_score}/100")
            quality_rating = "EXCELLENT"
        elif validation_score >= 75:
            st.warning(f"**Validation Score**: {validation_score}/100")
            quality_rating = "GOOD"
        elif validation_score >= 60:
            st.info(f"**Validation Score**: {validation_score}/100")
            quality_rating = "ACCEPTABLE"
        else:
            st.error(f"**Validation Score**: {validation_score}/100")
            quality_rating = "NEEDS IMPROVEMENT"
    
    with col2:
        st.metric("Quality Rating", quality_rating)
    
    with col3:
        st.metric("Issues Found", len(issues))
    
    st.markdown("---")
    
    # Validation checks
    st.subheader("🔍 Validation Checks")
    
    # Data completeness
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Data Completeness Check**")
        
        table4_missing = analyzer.table4['Internal_Tourism_Consumption'].isna().sum()
        table6_missing = analyzer.table6['Tourism_Ratio_Percent'].isna().sum()
        table7_missing = analyzer.table7['Full_Time_Equivalent_Jobs'].isna().sum()
        
        completeness_data = {
            'Table': ['Table 4 (Consumption)', 'Table 6 (Supply-Demand)', 'Table 7 (Employment)'],
            'Missing Values': [table4_missing, table6_missing, table7_missing],
            'Total Records': [len(analyzer.table4), len(analyzer.table6), len(analyzer.table7)]
        }
        
        completeness_df = pd.DataFrame(completeness_data)
        completeness_df['Completeness %'] = ((completeness_df['Total Records'] - completeness_df['Missing Values']) / 
                                             completeness_df['Total Records'] * 100).round(1)
        
        st.dataframe(completeness_df, hide_index=True)
        
        if table4_missing + table6_missing + table7_missing == 0:
            st.success("✅ No missing values found")
        else:
            st.warning(f"⚠️ {table4_missing + table6_missing + table7_missing} missing values found")
    
    with col2:
        st.write("**Tourism Ratios Validation**")
        
        extreme_ratios = analyzer.table6[analyzer.table6['Tourism_Ratio_Percent'] > 150]
        high_ratios = analyzer.table6[analyzer.table6['Tourism_Ratio_Percent'] > 100]
        reasonable_ratios = analyzer.table6[analyzer.table6['Tourism_Ratio_Percent'] <= 100]
        
        ratio_validation = {
            'Ratio Category': ['Reasonable (≤100%)', 'High (100-150%)', 'Extreme (>150%)'],
            'Count': [len(reasonable_ratios), len(high_ratios) - len(extreme_ratios), len(extreme_ratios)],
            'Percentage': [
                len(reasonable_ratios) / len(analyzer.table6) * 100,
                (len(high_ratios) - len(extreme_ratios)) / len(analyzer.table6) * 100,
                len(extreme_ratios) / len(analyzer.table6) * 100
            ]
        }
        
        ratio_df = pd.DataFrame(ratio_validation)
        ratio_df['Percentage'] = ratio_df['Percentage'].round(1)
        
        st.dataframe(ratio_df, hide_index=True)
        
        if len(extreme_ratios) == 0:
            st.success("✅ All tourism ratios are reasonable")
        else:
            st.warning(f"⚠️ {len(extreme_ratios)} products have extreme ratios")
    
    # Consistency checks
    st.subheader("🔄 Consistency Checks")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Tourism Consumption Consistency**")
        
        table4_total = analyzer.table4['Internal_Tourism_Consumption'].sum()
        table6_total = analyzer.table6['Internal_Tourism_Consumption'].sum()
        discrepancy = abs(table4_total - table6_total)
        discrepancy_pct = (discrepancy / table4_total * 100) if table4_total > 0 else 0
        
        consistency_data = {
            'Source': ['Table 4 (Internal Consumption)', 'Table 6 (Supply-Demand)', 'Discrepancy'],
            'Value (€M)': [table4_total, table6_total, discrepancy],
            'Percentage': [100.0, (table6_total/table4_total*100) if table4_total > 0 else 0, discrepancy_pct]
        }
        
        st.dataframe(pd.DataFrame(consistency_data).round(2), hide_index=True)
        
        if discrepancy_pct < 1:
            st.success(f"✅ Consumption consistency: {discrepancy_pct:.2f}% difference")
        else:
            st.warning(f"⚠️ Consumption inconsistency: {discrepancy_pct:.2f}% difference")
    
    with col2:
        st.write("**Table Structure Validation**")
        
        validation_results = validate_table_structure(analyzer.tables)
        
        structure_data = []
        for table, result in validation_results.items():
            status = "✅ Valid" if "✅" in result else "❌ Invalid"
            structure_data.append({
                'Table': table,
                'Status': status,
                'Details': result
            })
        
        st.dataframe(pd.DataFrame(structure_data), hide_index=True)
    
    # Issues summary
    if issues:
        st.subheader("⚠️ Validation Issues")
        
        for i, issue in enumerate(issues, 1):
            st.write(f"{i}. {issue}")
    else:
        st.success("🎉 No validation issues found! Data quality is excellent.")
    
    # Recommendations for data improvement
    st.subheader("💡 Data Quality Recommendations")
    
    recommendations = []
    
    if validation_score < 100:
        if table4_missing + table6_missing + table7_missing > 0:
            recommendations.append("📝 Address missing values in core tables")
        
        if len(extreme_ratios) > 0:
            recommendations.append("🔍 Review products with extreme tourism ratios (>150%)")
        
        if discrepancy_pct > 1:
            recommendations.append("🔄 Reconcile tourism consumption figures between tables")
        
        recommendations.extend([
            "📊 Implement regular data validation procedures",
            "🎯 Establish data quality standards and monitoring",
            "📋 Document data collection and processing methods"
        ])
    else:
        recommendations.append("🌟 Maintain current high data quality standards")
        recommendations.append("📈 Consider expanding data collection for optional tables")
    
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")

if __name__ == "__main__":
    main()