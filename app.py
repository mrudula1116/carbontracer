# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import os
from datetime import datetime

# Import calculations and recommendations modules
import calculations
import recommendations

# Set page configuration
st.set_page_config(
    page_title="CarbonTracer - Track & Reduce Your Carbon Footprint",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Premium CSS utilizing CSS Variables for adaptive dark/light styling
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Elegant Title and Header styling */
    .app-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #2e7d32, #4caf50, #81c784);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .app-subtitle {
        font-size: 1.15rem;
        color: #757575;
        margin-bottom: 1.8rem;
        font-weight: 400;
    }
    
    /* Adaptable Premium Card Design */
    .premium-card {
        background-color: var(--secondary-background-color);
        border-radius: 16px;
        padding: 24px;
        border-left: 6px solid #2e7d32;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .premium-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.08);
    }
    .premium-card h3 {
        margin-top: 0;
        color: #2e7d32;
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    .premium-card p {
        margin: 0;
        font-size: 1rem;
        line-height: 1.5;
    }
    
    /* Stats & Badge Indicators */
    .badge-easy {
        background-color: rgba(76, 175, 80, 0.15);
        color: #2e7d32;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-medium {
        background-color: rgba(255, 152, 0, 0.15);
        color: #f57c00;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-hard {
        background-color: rgba(244, 67, 54, 0.15);
        color: #d32f2f;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Hero Info Box */
    .hero-info {
        background: linear-gradient(135deg, rgba(46, 125, 50, 0.05), rgba(76, 175, 80, 0.1));
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(46, 125, 50, 0.15);
        margin-bottom: 24px;
    }
    
    /* Metrics override */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2e7d32;
    }
</style>
""", unsafe_allow_html=True)

# File system persistence for footprint tracking
HISTORY_FILE = "footprint_history.csv"
@st.cache_data
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame(columns=[
            "Date", "Label", "Home_t", "Transport_t", "Diet_t", "Waste_t", "Total_t"
        ])
    try:
        return pd.read_csv(HISTORY_FILE)
    except Exception:
        return pd.DataFrame(columns=[
            "Date", "Label", "Home_t", "Transport_t", "Diet_t", "Waste_t", "Total_t"
        ])

def save_record(label, home_t, transport_t, diet_t, waste_t, total_t):
    df = load_history()
    new_record = pd.DataFrame([{
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Label": label,
        "Home_t": round(home_t, 2),
        "Transport_t": round(transport_t, 2),
        "Diet_t": round(diet_t, 2),
        "Waste_t": round(waste_t, 2),
        "Total_t": round(total_t, 2)
    }])
    df = pd.concat([df, new_record], ignore_index=True)
    try:
     df.to_csv(HISTORY_FILE, index=False)
     load_history.clear()
    except Exception as e:
      st.error(f"Error saving history: {e}")

def delete_record(index):
    df = load_history()
    if 0 <= index < len(df):
        df = df.drop(index).reset_index(drop=True)
        try:
         df.to_csv(HISTORY_FILE, index=False)
         load_history.clear()
        except Exception as e:
         st.error(f"Error deleting record: {e}")
        return True
    return False

# Initialize Session States for multi-step computations and values
if "calc_done" not in st.session_state:
    st.session_state.calc_done = False
if "user_inputs" not in st.session_state:
    st.session_state.user_inputs = {
        "electricity_kwh": 300.0,
        "gas_m3": 50.0,
        "clean_energy_pct": 0.0,
        "vehicle_type": "Petrol (Gasoline)",
        "weekly_car_km": 150.0,
        "weekly_transit_km": 50.0,
        "short_flights": 2,
        "long_flights": 0,
        "diet_type": "Average Meat Eater",
        "household_size": 2,
        "recycles_paper": True,
        "recycles_plastic": True,
        "recycles_glass": False,
        "recycles_metal": False,
        "composts": False,
    }
if "footprint_results" not in st.session_state:
    st.session_state.footprint_results = None

# Sidebar layout
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #2e7d32; font-weight: 800;'>🍃 CarbonTracer</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.9rem; color: #757575;'>Track & Tame Your Personal Emissions</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["Dashboard & Calculator", "Emission Reduction Guide", "Progress Tracker", "Carbon 101"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### Regional Emission Benchmarks")
    st.markdown("""
    - **India Average**: 1.9 t CO₂e/yr
    - **US Average**: 16.0 t CO₂e/yr
    - **UK Average**: 6.5 t CO₂e/yr
    - **EU Average**: 7.0 t CO₂e/yr
    - **Global Average**: 4.7 t CO₂e/yr
    - **Climate Target**: 2.0 t CO₂e/yr
    """)
    st.caption("Target is set to cap global warming below 1.5°C.")

# App Header
st.markdown("""
<div style="
background: linear-gradient(135deg,#1b5e20,#2e7d32,#4caf50);
padding:35px;
border-radius:20px;
text-align:center;
margin-bottom:20px;
box-shadow:0 10px 30px rgba(0,0,0,0.15);
">

<h1 style="
color:white;
font-size:3rem;
margin-bottom:5px;
">
🌍 CarbonTracer
</h1>

<p style="
color:#f1f8e9;
font-size:1.2rem;
">
Track • Understand • Reduce Your Carbon Footprint
</p>

</div>
""", unsafe_allow_html=True)

# ----------------- PAGE 1: CALCULATOR & DASHBOARD -----------------
if page == "Dashboard & Calculator":
    st.markdown("### 🧮 Personal Footprint Calculator")
    st.write("Complete the sections below to calculate your personalized carbon footprint.")

    # Input tabs
    tab_energy, tab_travel, tab_diet, tab_waste = st.tabs([
        "🏠 Home Energy", "🚗 Travel & Transport", "🥗 Food & Diet", "🗑️ Waste & Recycling"
    ])

    inputs = st.session_state.user_inputs

    # 1. Energy inputs
    with tab_energy:
        st.subheader("Home Utility Bill Estimations")
        col1, col2 = st.columns(2)
        with col1:
            inputs["electricity_kwh"] = st.slider(
                "Monthly Electricity Consumption (kWh)",
                min_value=0.0, max_value=2000.0,
                value=float(inputs["electricity_kwh"]),
                step=10.0,
                help="Check your recent utility bill. Average household uses ~300-900 kWh/month."
            )
            inputs["clean_energy_pct"] = st.slider(
                "Clean/Renewable Energy Share (%)",
                min_value=0.0, max_value=100.0,
                value=float(inputs["clean_energy_pct"]),
                step=5.0,
                help="Specify if your energy provider uses clean sources or if you have solar panels."
            )
        with col2:
            inputs["gas_m3"] = st.slider(
                "Monthly Natural Gas Consumption (m³)",
                min_value=0.0, max_value=500.0,
                value=float(inputs["gas_m3"]),
                step=5.0,
                help="Average household uses natural gas for cooking and space/water heating."
            )

    # 2. Transport inputs
    with tab_travel:
        st.subheader("Weekly Commuting & Annual Flights")
        col1, col2 = st.columns(2)
        with col1:
            inputs["vehicle_type"] = st.selectbox(
                "Primary Vehicle Type",
                ["None", "Petrol (Gasoline)", "Diesel", "Hybrid", "Electric"],
                index=["None", "Petrol (Gasoline)", "Diesel", "Hybrid", "Electric"].index(inputs["vehicle_type"])
            )
            inputs["weekly_car_km"] = st.slider(
                "Weekly Driving Distance (km)",
                min_value=0.0, max_value=1500.0,
                value=float(inputs["weekly_car_km"]),
                step=10.0,
                disabled=(inputs["vehicle_type"] == "None")
            )
        with col2:
            inputs["weekly_transit_km"] = st.slider(
                "Weekly Public Transit Distance (km)",
                min_value=0.0, max_value=500.0,
                value=float(inputs["weekly_transit_km"]),
                step=5.0,
                help="Distance traveled by train, bus, subway, or streetcar."
            )
            subcol1, subcol2 = st.columns(2)
            with subcol1:
                inputs["short_flights"] = st.number_input(
                    "Short-Haul Flights / year (< 3 hours)",
                    min_value=0, max_value=50,
                    value=int(inputs["short_flights"]),
                    step=1
                )
            with subcol2:
                inputs["long_flights"] = st.number_input(
                    "Long-Haul Flights / year (> 3 hours)",
                    min_value=0, max_value=50,
                    value=int(inputs["long_flights"]),
                    step=1
                )

    # 3. Diet inputs
    with tab_diet:
        st.subheader("Dietary Profile")
        inputs["diet_type"] = st.selectbox(
            "Which best describes your daily diet?",
            ["Meat Heavy", "Average Meat Eater", "Vegetarian", "Vegan"],
            index=["Meat Heavy", "Average Meat Eater", "Vegetarian", "Vegan"].index(inputs["diet_type"]),
            help="Meat Heavy: Meat with almost every meal. Average: Meat some days/meals. Veg: No meat/fish. Vegan: Plant-based only."
        )
        st.markdown("""
        > **Did you know?** Food production accounts for over a quarter of global greenhouse gas emissions. 
        > Switching from meat-heavy to plant-based diets can reduce your meal emissions by up to 50%!
        """)

    # 4. Waste inputs
    with tab_waste:
        st.subheader("Household Waste & Recycling Actions")
        col1, col2 = st.columns(2)
        with col1:
            inputs["household_size"] = st.number_input(
                "Number of Household Members",
                min_value=1, max_value=20,
                value=int(inputs["household_size"]),
                step=1,
                help="Waste calculations are divided by household size to reflect your personal share."
            )
            inputs["composts"] = st.checkbox(
                "Compost organic/food waste",
                value=bool(inputs["composts"])
            )
        with col2:
            st.write("Do you recycle the following materials?")
            inputs["recycles_paper"] = st.checkbox("Paper & Cardboard", value=bool(inputs["recycles_paper"]))
            inputs["recycles_plastic"] = st.checkbox("Plastics", value=bool(inputs["recycles_plastic"]))
            inputs["recycles_glass"] = st.checkbox("Glass", value=bool(inputs["recycles_glass"]))
            inputs["recycles_metal"] = st.checkbox("Metals", value=bool(inputs["recycles_metal"]))

    # Save inputs back to session state
    st.session_state.user_inputs = inputs

    # Calculation action
    st.markdown("---")
    if st.button("🚀 Calculate Footprint", type="primary"):
        # Perform calculations
        home_e = calculations.calculate_home_emissions(
            inputs["electricity_kwh"], inputs["gas_m3"], inputs["clean_energy_pct"]
        )
        transport_e = calculations.calculate_transport_emissions(
            inputs["vehicle_type"], inputs["weekly_car_km"], inputs["weekly_transit_km"],
            inputs["short_flights"], inputs["long_flights"]
        )
        diet_e = calculations.calculate_diet_emissions(inputs["diet_type"])
        waste_e = calculations.calculate_waste_emissions(
            inputs["household_size"], inputs["recycles_paper"], inputs["recycles_plastic"],
            inputs["recycles_glass"], inputs["recycles_metal"], inputs["composts"]
        )
        
        results = calculations.calculate_total_footprint(home_e, transport_e, diet_e, waste_e)
        st.session_state.footprint_results = results
        st.session_state.calc_done = True
        st.toast("Calculations updated successfully!", icon="✅")

    # Display Dashboard Results
    if st.session_state.calc_done and st.session_state.footprint_results:
        res = st.session_state.footprint_results
        # Eco Score Calculation
        eco_score = max(
    0,
    min(
        100,
        round((1 - (res["total_t"] / 16)) * 100)
    )
)
        st.markdown("### 📊 Your Emission Dashboard")
        
        # Primary KPI metrics
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        with metric_col1:
            st.metric(
                label="Your Annual Footprint",
                value=f"{res['total_t']:.2f} t CO₂e",
                delta=f"{res['total_t'] - calculations.BENCHMARKS['Global Average']:.2f} t CO₂e vs Global Avg",
                delta_color="inverse"
            )
        with metric_col2:
            # Calculate reduction target percentage
            target = calculations.BENCHMARKS["Target (to combat warming)"]
            diff_pct = ((res["total_t"] - target) / target) * 100
            st.metric(
                label="Distance to 1.5°C Climate Target",
                value=f"{target:.1f} t CO₂e",
                delta=f"+{diff_pct:.0f}%" if res["total_t"] > target else f"{diff_pct:.0f}%",
                delta_color="inverse"
            )
        with metric_col3:
            # Highlight largest category
            cats = {
                "Home Energy": res["home_t"],
                "Transport": res["transport_t"],
                "Food & Diet": res["diet_t"],
                "Waste": res["waste_t"]
            }
            largest_cat = max(cats, key=cats.get)
            largest_val = cats[largest_cat]
            pct = (largest_val / res["total_t"] * 100) if res["total_t"] > 0 else 0
            st.metric(
                label="Largest Emission Driver",
                value=largest_cat,
                delta=f"{pct:.0f}% of total emissions"
            )
        with metric_col4:
           st.metric(
        "Eco Score",
        f"{eco_score}/100"
    )
    if eco_score >= 90:
        badge = "🌟 Climate Champion"
    elif eco_score >= 75:
        badge = "🌱 Eco Conscious"
    elif eco_score >= 50:
        badge = "♻️ Sustainability Learner"
    else:
        badge = "⚠️ High Impact User"

    st.success(badge)
    # Charts Section
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
            st.markdown("#### Emissions by Source Category")
            # Donut chart
            df_pie = pd.DataFrame({
                "Category": ["Home Energy", "Transport", "Food & Diet", "Waste & Recycling"],
                "Emissions (t CO₂e)": [res["home_t"], res["transport_t"], res["diet_t"], res["waste_t"]]
            })
            fig_pie = px.pie(
                df_pie, 
                values="Emissions (t CO₂e)", 
                names="Category",
                hole=0.4,
                color_discrete_sequence=["#2e7d32", "#4caf50", "#81c784", "#a5d6a7"]
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Outfit", size=12),
                margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(orientation="h", y=-0.1)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown("### 🤖 AI Carbon Insights")

            largest_category = max(
    {
        "Home Energy": res["home_t"],
        "Transport": res["transport_t"],
        "Food & Diet": res["diet_t"],
        "Waste": res["waste_t"]
    },
    key=lambda x: {
        "Home Energy": res["home_t"],
        "Transport": res["transport_t"],
        "Food & Diet": res["diet_t"],
        "Waste": res["waste_t"]
    }[x]
)

            st.info(
                f"""
                Your largest emission source is **{largest_category}**.

                Annual footprint: **{res['total_t']:.2f} t CO₂e**

                Compared to the global average (4.7 t), you are
                {'above' if res['total_t'] > 4.7 else 'below'} average.

                Focus on reducing {largest_category.lower()} emissions first for maximum impact.
                """
            )
        
    with col_chart2:
            st.markdown("#### How You Compare Globally")
            # Horizontal Bar Chart comparing benchmarks
            bench_names = list(calculations.BENCHMARKS.keys())
            bench_vals = list(calculations.BENCHMARKS.values())
            
            # Insert user record
            bench_names.insert(0, "YOU")
            bench_vals.insert(0, res["total_t"])
            
            df_bar = pd.DataFrame({
                "Entity": bench_names,
                "Annual Emissions (t CO₂e)": bench_vals
            })
            # Define colors
            colors = ["#2e7d32" if x == "YOU" else "#757575" for x in bench_names]
            # Climate target custom color
            if "Target (to combat warming)" in bench_names:
                colors[bench_names.index("Target (to combat warming)")] = "#2196f3"
                
            fig_bar = px.bar(
                df_bar,
                x="Annual Emissions (t CO₂e)",
                y="Entity",
                orientation="h",
                text="Annual Emissions (t CO₂e)",
                color="Entity",
                color_discrete_map={name: color for name, color in zip(bench_names, colors)}
            )
            fig_bar.update_layout(
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Outfit", size=12),
                margin=dict(t=10, b=10, l=10, r=10),
                xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.2)"),
                yaxis=dict(autorange="reversed")
            )
            fig_bar.update_traces(
                texttemplate='%{text:.2f} t', 
                textposition='outside',
                cliponaxis=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            # Persistence: Log Progress panel
            st.markdown("---")
            st.markdown("#### 📁 Log This Footprint to Progress History")
            log_col1, log_col2 = st.columns([3, 1])
            with log_col1:
              log_label = st.text_input(
                "Label for this footprint", 
                value=f"Baseline - {datetime.now().strftime('%b %Y')}",
                help="Examples: 'My Baseline', 'Post EV Upgrade', 'Eco-friendly Challenge'"
            )
            with log_col2:
               st.write("")
            st.write("")
            if st.button("💾 Save to History", type="secondary", use_container_width=True):
                save_record(
                    log_label, 
                    res["home_t"], 
                    res["transport_t"], 
                    res["diet_t"], 
                    res["waste_t"], 
                    res["total_t"]
                )
                st.toast("Footprint logged successfully! Check the 'Progress Tracker' tab.", icon="💾")
            else:
        # Initial call-to-action details
              st.info("💡 Fill in the details above and click 'Calculate Footprint' to inspect your personalized breakdown dashboard.")

# ----------------- PAGE 2: EMISSION REDUCTION GUIDE -----------------
elif page == "Emission Reduction Guide":
    st.markdown("### 📉 Personalized Emission Reduction Plan")
    st.markdown("Commit to simple household actions and see your potential emissions drop in real-time. We have structured this plan to help you prioritize your efforts.")

    # Check if calculation exists to build dynamic action list
    if st.session_state.footprint_results is None:
        st.warning("⚠️ Please complete the 'Dashboard & Calculator' first to unlock personalized suggestions.")
    else:
        res = st.session_state.footprint_results
        user_inputs = st.session_state.user_inputs
        
        # Load customized actions
        actions = recommendations.get_reduction_actions(user_inputs)
        
        # Categorize Actions
        quick_wins = [a for a in actions if a["difficulty"] == "Easy"]
        high_impact = [a for a in actions if a["difficulty"] == "Medium"]
        long_term = [a for a in actions if a["difficulty"] == "Hard"]
        
        # Dynamic target panel at the top
        st.markdown("<div class='hero-info'>", unsafe_allow_html=True)
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.markdown(f"**Current Carbon Footprint:**  \n### {res['total_t']:.2f} t CO₂e")
        with col_p2:
            # We will calculate saved value in session state based on checked actions
            st.markdown("**Projected Annual Savings:**")
            savings_placeholder = st.empty()
        with col_p3:
            st.markdown("**New Projected Footprint:**")
            projected_placeholder = st.empty()
        st.markdown("</div>", unsafe_allow_html=True)
        
        selected_savings_kg = 0.0

        def display_action_group(group_actions, group_title, icon):
            if not group_actions:
                return 0.0
                
            st.markdown(f"#### {icon} {group_title}")
            local_savings = 0.0
            
            for action in group_actions:
                # Create interactive card with checkbox
                card_col1, card_col2 = st.columns([1, 12])
                
                with card_col1:
                    # Add unique key
                    is_selected = st.checkbox("", key=f"act_{action['id']}")
                    if is_selected:
                        local_savings += action["potential_savings_kg"]
                        
                with card_col2:
                    # Select difficulty badge
                    dif = action["difficulty"]
                    badge_class = "badge-easy" if dif == "Easy" else "badge-medium" if dif == "Medium" else "badge-hard"
                    
                    st.markdown(f"""
                    <div class="premium-card">
                        <div style="float: right; margin-left: 10px;">
                            <span class="{badge_class}">{action['category']}</span>
                            <span style="font-size: 1.1rem; font-weight: 700; color: #2e7d32; margin-left: 10px;">-{action['potential_savings_kg']} kg CO₂e/yr</span>
                        </div>
                        <h3>{action['title']}</h3>
                        <p style="color: #616161; font-size: 0.95rem;">{action['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            return local_savings

        st.markdown("---")
        
        # Display each group and accumulate savings
        savings_quick = display_action_group(quick_wins, "Quick Wins (Low Effort, Immediate Impact)", "⚡")
        savings_high = display_action_group(high_impact, "High-Impact Actions (Medium Effort, Large Savings)", "🚀")
        savings_long = display_action_group(long_term, "Long-Term Goals (Significant Lifestyle/Investment Changes)", "🎯")
        
        selected_savings_kg = savings_quick + savings_high + savings_long
                
        # Update dynamic values
        projected_savings_t = selected_savings_kg / 1000.0
        new_projected_t = max(0.0, res["total_t"] - projected_savings_t)
        
        savings_placeholder.markdown(f"### {projected_savings_t:.2f} t CO₂e")
        projected_placeholder.markdown(f"### {new_projected_t:.2f} t CO₂e")
        
        # Visual climate goal tracker
        st.markdown("#### Progress Toward 1.5°C Goal (2.0 t CO₂e/capita)")
        
        progress_val = 1.0 - (new_projected_t / max(2.0, res["total_t"]))
        progress_val = max(0.0, min(1.0, progress_val)) # clamp
        
        st.progress(progress_val)
        if new_projected_t <= 2.0:
            st.success("🎉 Outstanding! Your projected actions bring you below the 2.0 ton carbon budget limit!")
        else:
            st.info(f"💡 You need to reduce by another {new_projected_t - 2.0:.2f} tons to meet the climate target. Try adopting more actions!")

# ----------------- PAGE 3: PROGRESS TRACKER -----------------
elif page == "Progress Tracker":
    st.markdown("### 📈 Your Carbon History & Progress Log")
    st.write("Analyze and review your carbon emissions reduction journey over time.")
    
    df = load_history()
    
    if df.empty:
        st.info("💡 You have not logged any footprint records yet. Calculate your footprint on the Dashboard and click 'Save to History'.")
    else:
        # Overview stats
        tot_entries = len(df)
        first_total = df.iloc[0]["Total_t"]
        current_total = df.iloc[-1]["Total_t"]
        net_diff = current_total - first_total
        pct_diff = (net_diff / first_total * 100) if first_total > 0 else 0
        avg_fp = df["Total_t"].mean()
        best_fp = df["Total_t"].min()
        col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
        with col_s1:
            st.metric("Logged Submissions", f"{tot_entries} Records")
        with col_s2:
            st.metric(
                "Current Active Footprint", 
                f"{current_total:.2f} t CO₂e"
            )
        with col_s3:
            st.metric(
                "Net Lifetime Reduction",
                f"{-net_diff:.2f} t CO₂e" if net_diff <= 0 else f"+{net_diff:.2f} t CO₂e",
                delta=f"{pct_diff:.1f}% change since startup",
                delta_color="inverse"
            )
        with col_s4:
            st.metric(
                "Average Footprint",
                f"{avg_fp:.2f} t"
            )

        with col_s5:
            st.metric(
                "Best Footprint",
                f"{best_fp:.2f} t"
            )

        # Line chart of progress
        st.markdown("#### Emission Trend Over Time")
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=df["Date"], 
            y=df["Total_t"], 
            mode='lines+markers',
            name='Total Footprint',
            line=dict(color='#2e7d32', width=3),
            marker=dict(size=8, color='#1b5e20')
        ))
        # Add target line
        fig_trend.add_hline(
            y=2.0, 
            line_dash="dash", 
            line_color="#2196f3", 
            annotation_text="Global 1.5°C Target (2.0 t)", 
            annotation_position="bottom right"
        )
        
        fig_trend.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Outfit", size=12),
            margin=dict(t=30, b=30, l=10, r=10),
            xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.1)"),
            yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.1)", title="Emissions (t CO₂e/year)"),
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        if len(df) >= 2:
            best = df["Total_t"].min()
            worst = df["Total_t"].max()

            col_a, col_b = st.columns(2)

            with col_a:
                st.metric(
                    "Best Recorded Footprint",
                    f"{best:.2f} t CO₂e"
                )

            with col_b:
                st.metric(
                    "Highest Recorded Footprint",
                    f"{worst:.2f} t CO₂e"
                )
        if len(df) >= 3:
            X = np.arange(len(df)).reshape(-1, 1)
            y = df["Total_t"]

            model = LinearRegression()
            model.fit(X, y)

            future_prediction = model.predict(
                [[len(df) + 3]]
            )[0]

            st.success(
                f"📈 Predicted footprint after next 3 records: "
                f"{future_prediction:.2f} t CO₂e"
            )
        # Detailed Records Table
        st.markdown("#### Saved Records Database")
        
        # Columns formatting
        df_display = df.copy()
        df_display.columns = ["Date Added", "Label", "Home Energy (t)", "Transport (t)", "Food & Diet (t)", "Waste (t)", "Total Footprint (t)"]
        
        st.dataframe(df_display, use_container_width=True)
        csv = df.to_csv(index=False)

        st.download_button(
    label="📥 Download History CSV",
    data=csv,
    file_name="carbon_history.csv",
    mime="text/csv"
)
        # Deleting records option
        st.markdown("---")
        st.markdown("##### 🗑️ Manage Records")
        del_col1, del_col2 = st.columns([3, 1])
        with del_col1:
            record_to_del = st.selectbox(
                "Select a record to remove",
                options=range(len(df)),
                format_func=lambda idx: f"[{df.iloc[idx]['Date']}] {df.iloc[idx]['Label']} ({df.iloc[idx]['Total_t']} t CO₂e)"
            )
        with del_col2:
            st.write("")
            st.write("")
            if st.button("Delete Selected Record", type="secondary", use_container_width=True):
                if delete_record(record_to_del):
                    st.toast("Record successfully deleted!", icon="🗑️")
                    st.rerun()

# ----------------- PAGE 4: CARBON 101 -----------------
elif page == "Carbon 101":
    st.markdown("### 📘 Understand Carbon Footprints")
    st.markdown("""
    Reducing emissions begins with awareness. Here is a brief guide on the science of carbon tracking 
    and how you can influence change.
    """)
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.markdown("""
        #### What is a Carbon Footprint?
        A carbon footprint is the total amount of greenhouse gases (including carbon dioxide and methane) 
        that are generated by our actions. 
        
        It is typically calculated in **metric tons of Carbon Dioxide equivalent (t CO₂e)** to simplify and standardize the impact of different gases (like methane from food waste, which has a higher heat-trapping capacity than CO₂).
        
        #### The 3 Scopes of Emissions
        Emissions are generally categorized into three scopes:
        - **Scope 1 (Direct)**: Emissions from sources that you own or control directly (e.g., burning gas in your furnace or fuel in your car).
        - **Scope 2 (Indirect)**: Emissions from the generation of electricity, heating, or cooling that you purchase and consume.
        - **Scope 3 (Supply Chain)**: All other indirect emissions in your value chain (e.g., the emissions created to grow your food, produce your clothes, or manufacture your electronics).
        """)
    with col_info2:
        st.markdown("""
        #### Where Can You Have the Largest Impact?
        
        1. **Power Your Home Cleanly** 🔌  
           Transitioning to renewable electricity cuts your home's Scope 2 emissions to absolute zero. If solar is not available, ask your utility provider about clean energy tariffs.
           
        2. **Rethink Commuting** 🚲  
           Short car journeys of under 3 km account for over 50% of urban car trips. Switching these to cycling, walking, or public transit has an outsized benefit on reducing congestion and local air pollution.
           
        3. **Shift Your Diet** 🥦  
           Producing beef requires 20x more land and emits 20x more greenhouse gases per gram of protein than plant proteins like beans or tofu. You don't have to go 100% vegan immediately—shifting away from beef and lamb yields the quickest benefits.
           
        4. **Reduce and Recycle** ♻️  
           Methane emissions from rotting organic waste in landfill sites is a massive global warming contributor. Setting up backyard or city compost bins prevents methane release and builds rich soils.
        """)
        
    st.markdown("---")
    st.markdown("#### 🌟 Sustainable Resources and Further Reading")
    st.markdown("""
    * **[IPCC Reports](https://www.ipcc.ch/):** The authoritative source on climate change science and projections.
    * **[EPA Carbon Calculator](https://www.epa.gov/carbon-footprint-calculator/):** The US Environmental Protection Agency's tracking tool.
    * **[Drawdown Project](https://drawdown.org/):** A comprehensive catalog of actionable solutions to reverse global warming.
    """)
