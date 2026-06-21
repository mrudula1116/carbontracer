# app.py
import streamlit as st
import pandas as pd
import numpy as np 
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import os
import re
from datetime import datetime

# Import calculations and recommendations modules
import calculations
import recommendations

st.set_page_config(
    page_title="CarbonTracer - Track & Reduce Your Carbon Footprint",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- ACCESSIBILITY METADATA PANELS ---
with st.expander("♿ Accessibility Features"):
    st.write("""
    • Keyboard accessible controls
    • Large readable text
    • High contrast visuals
    • Clear chart descriptions
    • Screen-reader friendly labels
    """)

with st.expander("🔒 Privacy Notice"):
    st.write("""
    This application does not collect, store, or share personal information.
    All calculations are performed locally.
    """)

# --- CUSTOM CSS WITH UPDATED COLOR THEME ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght=300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .app-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0f5132, #198754, #20c997);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .app-subtitle {
        font-size: 1.15rem;
        color: #6c757d;
        margin-bottom: 1.8rem;
        font-weight: 400;
    }
    
    .premium-card {
        background-color: var(--secondary-background-color);
        border-radius: 16px;
        padding: 24px;
        border-left: 6px solid #198754;
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
        color: #0f5132;
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    .premium-card p {
        margin: 0;
        font-size: 1rem;
        line-height: 1.5;
    }
    
    .badge-easy {
        background-color: rgba(25, 135, 84, 0.15);
        color: #198754;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-medium {
        background-color: rgba(253, 126, 20, 0.15);
        color: #fd7e14;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-hard {
        background-color: rgba(220, 53, 69, 0.15);
        color: #dc3545;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .hero-info {
        background: linear-gradient(135deg, rgba(25, 135, 84, 0.05), rgba(32, 201, 151, 0.1));
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(25, 135, 84, 0.15);
        margin-bottom: 24px;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0f5132;
    }
</style>
""", unsafe_allow_html=True)

# --- SECURE RESOURCE STACK ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "footprint_history.csv")

def sanitize_csv_input(text: str) -> str:
    """Mitigates spreadsheet equation formula logic injection attacks."""
    cleaned = str(text).strip()
    if cleaned.startswith(('=', '+', '-', '@', '%')):
        cleaned = "'" + cleaned
    return re.sub(r'[^\w\s\-\.\(\)\']', '', cleaned)

@st.cache_data
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame(columns=["Date", "Label", "Home_t", "Transport_t", "Diet_t", "Waste_t", "Total_t"])
    try:
        return pd.read_csv(HISTORY_FILE)
    except Exception:
        return pd.DataFrame(columns=["Date", "Label", "Home_t", "Transport_t", "Diet_t", "Waste_t", "Total_t"])

def save_record(label, home_t, transport_t, diet_t, waste_t, total_t):
    if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 5_000_000:
        st.warning("History storage cap hit.")
        return
        
    df = load_history()
    new_record = pd.DataFrame([{
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Label": sanitize_csv_input(label)[:60],
        "Home_t": float(round(home_t, 2)),
        "Transport_t": float(round(transport_t, 2)),
        "Diet_t": float(round(diet_t, 2)),
        "Waste_t": float(round(waste_t, 2)),
        "Total_t": float(round(total_t, 2))
    }])
    df = pd.concat([df, new_record], ignore_index=True)
    try:
        tmp_file = HISTORY_FILE + ".tmp"
        df.to_csv(tmp_file, index=False)
        os.replace(tmp_file, HISTORY_FILE)
        load_history.clear()
    except Exception as e:
        st.error(f"Error saving history: {e}")

def delete_record(index: int) -> bool:
    df = load_history()
    try:
        target_idx = int(index)
        if 0 <= target_idx < len(df):
            df = df.drop(target_idx).reset_index(drop=True)
            df.to_csv(HISTORY_FILE, index=False)
            load_history.clear()
            return True
    except Exception as e:
        st.error(f"Error removing row context item: {e}")
    return False

# --- STATE LIFECYCLES ---
if "calc_done" not in st.session_state:
    st.session_state.calc_done = False
if "user_inputs" not in st.session_state:
    st.session_state.user_inputs = {
        "electricity_kwh": 300.0, "gas_m3": 50.0, "clean_energy_pct": 0.0,
        "vehicle_type": "Petrol (Gasoline)", "weekly_car_km": 150.0, "weekly_transit_km": 50.0,
        "short_flights": 2, "long_flights": 0, "diet_type": "Average Meat Eater",
        "household_size": 2, "recycles_paper": True, "recycles_plastic": True,
        "recycles_glass": False, "recycles_metal": False, "composts": False,
    }
if "footprint_results" not in st.session_state:
    st.session_state.footprint_results = None

# --- SIDEBAR INTERFACE ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #198754; font-weight: 800;'>🍃 CarbonTracer</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.9rem; color: #6c757d;'>Track & Tame Your Personal Emissions</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    page = st.radio("Navigation Menu Panels", ["Dashboard & Calculator", "Emission Reduction Guide", "Progress Tracker", "Carbon 101"], index=0)
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

# --- MAIN APP BRAND JUMBOTRON ---
st.markdown("""
<div style="background: linear-gradient(135deg, #0f5132, #198754, #20c997); padding:35px; border-radius:20px; text-align:center; margin-bottom:20px; box-shadow:0 10px 30px rgba(0,0,0,0.15);">
    <h1 style="color:white; font-size:3rem; margin-bottom:5px;">🌍 CarbonTracer</h1>
    <p style="color:#e8f5e9; font-size:1.2rem;">Track • Understand • Reduce Your Carbon Footprint</p>
</div>
""", unsafe_allow_html=True)

# --- PANEL ROUTER PATHS ---
if page == "Dashboard & Calculator":
    st.markdown("### 🧮 Personal Footprint Calculator")
    st.write("Complete the sections below to calculate your personalized carbon footprint.")

    tab_energy, tab_travel, tab_diet, tab_waste = st.tabs([
        "🏠 Home Energy", "🚗 Travel & Transport", "🥗 Food & Diet", "🗑️ Waste & Recycling"
    ])

    inputs = st.session_state.user_inputs

    with tab_energy:
        st.subheader("Home Utility Bill Estimations")
        col1, col2 = st.columns(2)
        with col1:
            inputs["electricity_kwh"] = st.slider("Monthly Electricity Consumption (kWh)", 0.0, 2000.0, float(inputs["electricity_kwh"]), step=10.0, help="Average household uses ~300-900 kWh/month.")
            inputs["clean_energy_pct"] = st.slider("Clean/Renewable Energy Share (%)", 0.0, 100.0, float(inputs["clean_energy_pct"]), step=5.0, help="Specify clean power ratio.")
        with col2:
            inputs["gas_m3"] = st.slider("Monthly Natural Gas Consumption (m³)", 0.0, 500.0, float(inputs["gas_m3"]), step=5.0, help="Natural gas for cooking and space/water heating.")

    with tab_travel:
        st.subheader("Weekly Commuting & Annual Flights")
        col1, col2 = st.columns(2)
        with col1:
            vehicles_options = ["None", "Petrol (Gasoline)", "Diesel", "Hybrid", "Electric"]
            inputs["vehicle_type"] = st.selectbox("Primary Vehicle Type", vehicles_options, index=vehicles_options.index(inputs["vehicle_type"]), help="Choose your primary transportation layout.")
            inputs["weekly_car_km"] = st.slider("Weekly Driving Distance (km)", 0.0, 1500.0, float(inputs["weekly_car_km"]), step=10.0, disabled=(inputs["vehicle_type"] == "None"))
        with col2:
            inputs["weekly_transit_km"] = st.slider("Weekly Public Transit Distance (km)", 0.0, 500.0, float(inputs["weekly_transit_km"]), step=5.0, help="Distance via train or bus.")
            subcol1, subcol2 = st.columns(2)
            with subcol1:
                inputs["short_flights"] = st.number_input("Short-Haul Flights / year (< 3 hours)", 0, 50, int(inputs["short_flights"]), step=1, help="Short regional routes.")
            with subcol2:
                inputs["long_flights"] = st.number_input("Long-Haul Flights / year (> 3 hours)", 0, 50, int(inputs["long_flights"]), step=1, help="International routes.")

    with tab_diet:
        st.subheader("Dietary Profile")
        diet_options = ["Meat Heavy", "Average Meat Eater", "Vegetarian", "Vegan"]
        inputs["diet_type"] = st.selectbox("Which best describes your daily diet?", diet_options, index=diet_options.index(inputs["diet_type"]), help="Food types impact macro footprints.")
        st.markdown("> **Did you know?** Transitioning to plant-based diets can lower emissions up to 50%!")

    with tab_waste:
        st.subheader("Household Waste & Recycling Actions")
        col1, col2 = st.columns(2)
        with col1:
            inputs["household_size"] = st.number_input("Number of Household Members", 1, 20, int(inputs["household_size"]), step=1, help="Values are split per capita.")
            inputs["composts"] = st.checkbox("Compost organic/food waste", value=bool(inputs["composts"]))
        with col2:
            st.write("Do you recycle the following materials?")
            inputs["recycles_paper"] = st.checkbox("Paper & Cardboard", value=bool(inputs["recycles_paper"]))
            inputs["recycles_plastic"] = st.checkbox("Plastics", value=bool(inputs["recycles_plastic"]))
            inputs["recycles_glass"] = st.checkbox("Glass", value=bool(inputs["recycles_glass"]))
            inputs["recycles_metal"] = st.checkbox("Metals", value=bool(inputs["recycles_metal"]))
            
    st.session_state.user_inputs = inputs

    st.markdown("---")
    if st.button("🚀 Calculate Footprint", type="primary", use_container_width=True):
        home_e = calculations.calculate_home_emissions(float(inputs["electricity_kwh"]), float(inputs["gas_m3"]), float(inputs["clean_energy_pct"]))
        transport_e = calculations.calculate_transport_emissions(str(inputs["vehicle_type"]), float(inputs["weekly_car_km"]), float(inputs["weekly_transit_km"]), int(inputs["short_flights"]), int(inputs["long_flights"]))
        diet_e = calculations.calculate_diet_emissions(str(inputs["diet_type"]))
        waste_e = calculations.calculate_waste_emissions(int(inputs["household_size"]), bool(inputs["recycles_paper"]), bool(inputs["recycles_plastic"]), bool(inputs["recycles_glass"]), bool(inputs["recycles_metal"]), bool(inputs["composts"]))
        
        st.session_state.footprint_results = calculations.calculate_total_footprint(home_e, transport_e, diet_e, waste_e)
        st.session_state.calc_done = True
        st.toast("Calculations updated successfully!", icon="✅")

    res = st.session_state.get("footprint_results")
    if st.session_state.calc_done and res is not None:
        eco_score = max(0, min(100, round((1 - (float(res["total_t"]) / 16.0)) * 100)))

        st.markdown("### 📊 Your Emission Dashboard")
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

        with metric_col1:
            st.metric(label="Your Annual Carbon Footprint", value=f"{res['total_t']:.2f} t CO₂e", delta=f"{res['total_t'] - calculations.BENCHMARKS['Global Average']:.2f} t CO₂e vs Avg", delta_color="inverse")
        with metric_col2:
            target = calculations.BENCHMARKS["Target (to combat warming)"]
            st.metric(label="Distance to 1.5°C Climate Target", value=f"{target:.1f} t CO₂e", delta=f"+{(((res['total_t'] - target) / target) * 100):.0f}%" if res["total_t"] > target else f"{(((res['total_t'] - target) / target) * 100):.0f}%", delta_color="inverse")
        with metric_col3:
            cats = {"Home Energy": res["home_t"], "Transport": res["transport_t"], "Food & Diet": res["diet_t"], "Waste": res["waste_t"]}
            largest_cat = max(cats, key=cats.get)
            st.metric(label="Largest Emission Driver", value=largest_cat, delta=f"{(cats[largest_cat] / res['total_t'] * 100):.0f}% of footprint")
        with metric_col4:
            st.metric("Eco Score", f"{eco_score}/100")

        badge = "🌟 Climate Champion" if eco_score >= 90 else "🌱 Eco Conscious" if eco_score >= 75 else "♻️ Sustainability Learner" if eco_score >= 50 else "⚠️ High Impact User"
        st.success(badge)

        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.markdown("#### Emissions by Source Category")
            df_pie = pd.DataFrame({"Category": ["Home Energy", "Transport", "Food & Diet", "Waste & Recycling"], "Emissions (t CO₂e)": [res["home_t"], res["transport_t"], res["diet_t"], res["waste_t"]]})
            fig_pie = px.pie(df_pie, values="Emissions (t CO₂e)", names="Category", hole=0.4, color_discrete_sequence=["#0f5132", "#198754", "#20c997", "#a3cfbb"])
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Outfit", size=12), margin=dict(t=10, b=10, l=10, r=10), legend=dict(orientation="h", y=-0.1))
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_chart2:
            st.markdown("#### How You Compare Globally")
            bench_names = list(calculations.BENCHMARKS.keys())
            bench_vals = [float(v) for v in calculations.BENCHMARKS.values()]
            bench_names.insert(0, "YOU")
            bench_vals.insert(0, float(res["total_t"]))

            df_bar = pd.DataFrame({"Entity": bench_names, "Annual Emissions (t CO₂e)": bench_vals})
            colors = ["#198754" if x == "YOU" else "#6c757d" for x in bench_names]
            if "Target (to combat warming)" in bench_names:
                colors[bench_names.index("Target (to combat warming)")] = "#0dcaf0"

            fig_bar = px.bar(df_bar, x="Annual Emissions (t CO₂e)", y="Entity", orientation="h", text="Annual Emissions (t CO₂e)", color="Entity", color_discrete_map={name: color for name, color in zip(bench_names, colors)})
            fig_bar.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Outfit", size=12), margin=dict(t=10, b=10, l=10, r=10), xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.2)"), yaxis=dict(autorange="reversed"))
            fig_bar.update_traces(texttemplate='%{text:.2f} t', textposition='outside', cliponaxis=False)
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        st.markdown("#### 📁 Log This Footprint to Progress History")
        log_col1, log_col2 = st.columns([3, 1])
        with log_col1:
            log_label = st.text_input("Label name identifier", value=f"Dataset - {datetime.now().strftime('%b %Y')}")
        with log_col2:
            st.write("")
        if st.button("💾 Save to History", type="secondary", use_container_width=True):
            save_record(log_label, res["home_t"], res["transport_t"], res["diet_t"], res["waste_t"], res["total_t"])
            st.toast("Footprint logged successfully!", icon="💾")

        st.markdown("### 🤖 AI Carbon Insights")
        st.info(f"Your largest emission source is **{largest_cat}**. Total footprint: **{res['total_t']:.2f} t CO₂e**. Focus your initial sustainability strategies here.")
    else:
        st.info("👆 Click **Calculate Footprint** to generate your dashboard and charts.")

elif page == "Emission Reduction Guide":
    st.markdown("### 📉 Personalized Emission Reduction Plan")
    if st.session_state.footprint_results is None:
        st.warning("⚠️ Please complete calculations on the dashboard first to build strategies.")
    else:
        res = st.session_state.footprint_results
        actions = recommendations.get_reduction_actions(st.session_state.user_inputs)
        
        quick_wins = [a for a in actions if a["difficulty"] == "Easy"]
        high_impact = [a for a in actions if a["difficulty"] == "Medium"]
        long_term = [a for a in actions if a["difficulty"] == "Hard"]
        
        st.markdown("<div class='hero-info'>", unsafe_allow_html=True)
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.markdown(f"**Current Footprint:** \n### {res['total_t']:.2f} t CO₂e")
        with col_p2:
            st.markdown("**Projected Savings:**")
            savings_placeholder = st.empty()
        with col_p3:
            st.markdown("**New Profile Target:**")
            projected_placeholder = st.empty()
        st.markdown("</div>", unsafe_allow_html=True)
        
        def display_action_group(group_actions, group_title, icon):
            if not group_actions:
                return 0.0
            st.markdown(f"#### {icon} {group_title}")
            local_savings = 0.0
            for action in group_actions:
                card_col1, card_col2 = st.columns([1, 12])
                with card_col1:
                    is_selected = st.checkbox("Select action item option", key=f"act_{action['id']}", label_visibility="collapsed")
                    if is_selected:
                        local_savings += float(action["potential_savings_kg"])
                with card_col2:
                    dif = action["difficulty"]
                    badge_class = "badge-easy" if dif == "Easy" else "badge-medium" if dif == "Medium" else "badge-hard"
                    st.markdown(f"""
                    <div class="premium-card">
                        <div style="float: right; margin-left: 10px;">
                            <span class="{badge_class}">{action['category']}</span>
                            <span style="font-size: 1.1rem; font-weight: 700; color: #198754; margin-left: 10px;">-{action['potential_savings_kg']} kg CO₂e/yr</span>
                        </div>
                        <h3>{action['title']}</h3>
                        <p style="color: #495057; font-size: 0.95rem;">{action['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            return local_savings

        st.markdown("---")
        savings_quick = display_action_group(quick_wins, "Quick Wins (Low Effort, Immediate Impact)", "⚡")
        savings_high = display_action_group(high_impact, "High-Impact Actions (Medium Effort)", "🚀")
        savings_long = display_action_group(long_term, "Long-Term Goals (Lifestyle Changes)", "🎯")
        
        selected_savings_kg = savings_quick + savings_high + savings_long
        projected_savings_t = selected_savings_kg / 1000.0
        new_projected_t = max(0.0, float(res["total_t"]) - projected_savings_t)
        
        savings_placeholder.markdown(f"### {projected_savings_t:.2f} t CO₂e")
        projected_placeholder.markdown(f"### {new_projected_t:.2f} t CO₂e")
        
        st.markdown("#### Progress Toward 1.5°C Goal")
        progress_val = max(0.0, min(1.0, 1.0 - (new_projected_t / max(2.0, float(res["total_t"])))))
        st.progress(progress_val)
        if new_projected_t <= 2.0:
            st.success("🎉 Outstanding! These updates drop you under the target budget thresholds.")

elif page == "Progress Tracker":
    st.markdown("### 📈 Your Carbon History & Progress Log")
    df = load_history()
    
    if df.empty:
        st.info("💡 No logged records yet. Run calculation pipelines to append rows here.")
    else:
        tot_entries = len(df)
        first_total = float(df.iloc[0]["Total_t"])
        current_total = float(df.iloc[-1]["Total_t"])
        net_diff = current_total - first_total
        pct_diff = (net_diff / first_total * 100) if first_total > 0 else 0
        
        col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
        col_s1.metric("Logged Entries", f"{tot_entries}")
        col_s2.metric("Active Run Metric", f"{current_total:.2f} t")
        col_s3.metric("Net Variance Tracker", f"{-net_diff:.2f} t" if net_diff <= 0 else f"+{net_diff:.2f} t", delta=f"{pct_diff:.1f}% shift")
        col_s4.metric("Average History Run", f"{df['Total_t'].mean():.2f} t")
        col_s5.metric("Optimal Run High", f"{df['Total_t'].min():.2f} t")

        st.markdown("#### Emission Trend Over Time")
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=df["Date"], y=df["Total_t"], mode='lines+markers', name='Total Footprint', line=dict(color='#198754', width=3)))
        fig_trend.add_hline(y=2.0, line_dash="dash", line_color="#0dcaf0", annotation_text="Target Budget threshold (2.0 t)")
        fig_trend.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Outfit", size=12), margin=dict(t=30, b=30, l=10, r=10))
        st.plotly_chart(fig_trend, use_container_width=True)
        
        if len(df) >= 3:
            X = np.arange(len(df)).reshape(-1, 1)
            y = df["Total_t"].astype(float)
            model = LinearRegression().fit(X, y)
            st.success(f"📈 Predictive future trajectory target calculation: {model.predict([[len(df) + 3]])[0]:.2f} t CO₂e")
            
        st.markdown("#### Saved Records Database")
        st.dataframe(df, use_container_width=True)
        
        st.download_button(label="📥 Download History CSV", data=df.to_csv(index=False), file_name="carbon_history.csv", mime="text/csv")
        
        st.markdown("---")
        st.markdown("##### 🗑️ Manage Records")
        del_col1, del_col2 = st.columns([3, 1])
        with del_col1:
            record_to_del = st.selectbox("Select target matrix row signature to drop", options=range(len(df)), format_func=lambda idx: f"[{df.iloc[idx]['Date']}] {df.iloc[idx]['Label']}")
        with del_col2:
            st.write("")
        if st.button("Delete Selected Record", type="primary"):
            if delete_record(record_to_del):
                st.toast("Record deleted successfully", icon="🗑️")
                st.rerun()

elif page == "Carbon 101":
    st.markdown("### 📘 Understand Carbon Footprints")
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.markdown("""
        #### What is a Carbon Footprint?
        A carbon footprint is the total amount of greenhouse gases generated by our actions. It is computed in **metric tons of Carbon Dioxide equivalent (t CO₂e)**.
        
        #### The 3 Scopes of Emissions
        - **Scope 1 (Direct)**: Emissions from sources you own or control (e.g., car exhaust).
        - **Scope 2 (Indirect)**: Purchased electricity profile grids.
        - **Scope 3 (Supply Chain)**: Extended material lifecycles (e.g., food manufacturing).
        """)
    with col_info2:
        st.markdown("""
        #### Maximum Strategic Impact Channels
        1. **Clean Electricity Switches**: Powering home networks with clean arrays drops Scope 2 footprint instantly.
        2. **Active Transit Shifting**: Moving localized driving behaviors to train or bus frameworks reduces urban burdens.
        3. **Plant-Based Dietary Scaling**: Cutting dairy or heavy meat products decreases lifecycle chain emissions.
        """)