"""
F1 Strategy Optimizer - Interactive Dashboard
Streamlit app for visualizing AI pit stop decisions
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
import sys 
# Import our modules
from data_processor import F1DataProcessor
from tire_model import TireDegradationModel
from pit_optimizer import PitStopOptimizer, RaceState

# Page config
st.set_page_config(
    page_title="F1 Strategy Optimizer",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #E10600;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stButton>button {
        background-color: #E10600;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_tire_model(year: int, race_name: str):
    """Load and train tire model (cached)"""
    with st.spinner(f"Loading {year} {race_name} GP data..."):
        processor = F1DataProcessor(year, race_name)
        processor.load_race_data()
        lap_data = processor.extract_lap_features()

        tire_model = TireDegradationModel(model_type='gradient_boost')
        metrics = tire_model.train(lap_data)

        optimizer = PitStopOptimizer(tire_model, pit_loss_time=24.0)

        return processor, tire_model, optimizer, lap_data, metrics


@st.cache_data
def get_race_summary(_processor):
    """Get race summary (cached)"""
    return _processor.get_race_summary()


def plot_track_map_with_pits(processor, driver, ai_pit_laps, actual_pit_laps):
    """Create 2D track map showing pit stop locations"""

    # Get driver's lap data with GPS
    driver_laps = processor.laps[processor.laps['Driver'] == driver].copy()

    # Get telemetry for track outline (use first lap)
    try:
        first_lap = driver_laps[driver_laps['LapNumber'] == 1].iloc[0]
        telemetry = first_lap.get_telemetry()

        if telemetry is not None and 'X' in telemetry.columns and 'Y' in telemetry.columns:
            # Create track outline
            fig = go.Figure()

            # Track layout
            fig.add_trace(go.Scatter(
                x=telemetry['X'],
                y=telemetry['Y'],
                mode='lines',
                line=dict(color='gray', width=3),
                name='Track',
                hoverinfo='skip'
            ))

            # Mark pit stop locations on track
            for lap_num in actual_pit_laps:
                lap_data = driver_laps[driver_laps['LapNumber'] == lap_num]
                if len(lap_data) > 0:
                    try:
                        lap_telemetry = lap_data.iloc[0].get_telemetry()
                        if lap_telemetry is not None and len(lap_telemetry) > 0:
                            # Use pit entry point (approximate)
                            x_pos = lap_telemetry['X'].iloc[0]
                            y_pos = lap_telemetry['Y'].iloc[0]

                            fig.add_trace(go.Scatter(
                                x=[x_pos],
                                y=[y_pos],
                                mode='markers',
                                marker=dict(size=15, color='red', symbol='x'),
                                name=f'Actual Pit Lap {lap_num}',
                                hovertext=f'Actual pit stop: Lap {lap_num}'
                            ))
                    except:
                        pass

            for decision in ai_pit_laps:
                lap_num = decision['lap']
                lap_data = driver_laps[driver_laps['LapNumber'] == lap_num]
                if len(lap_data) > 0:
                    try:
                        lap_telemetry = lap_data.iloc[0].get_telemetry()
                        if lap_telemetry is not None and len(lap_telemetry) > 0:
                            x_pos = lap_telemetry['X'].iloc[0]
                            y_pos = lap_telemetry['Y'].iloc[0]

                            fig.add_trace(go.Scatter(
                                x=[x_pos],
                                y=[y_pos],
                                mode='markers',
                                marker=dict(size=15, color='lime', symbol='diamond'),
                                name=f'AI Rec. Lap {lap_num}',
                                hovertext=f'AI recommendation: Lap {lap_num}<br>{decision["reasoning"]}'
                            ))
                    except:
                        pass

            fig.update_layout(
                title=f"{processor.race_name} - {driver} Pit Strategy",
                showlegend=True,
                height=500,
                xaxis=dict(showgrid=False, showticklabels=False, title=''),
                yaxis=dict(showgrid=False, showticklabels=False, title='', scaleanchor="x", scaleratio=1),
                plot_bgcolor='#0E1117',
                paper_bgcolor='#0E1117',
                font=dict(color='white')
            )

            return fig
    except Exception as e:
        st.warning(f"Could not generate track map: {str(e)}")

    # Fallback: simple lap number visualization
    fig = go.Figure()

    # Draw laps as a linear timeline
    total_laps = driver_laps['LapNumber'].max()

    fig.add_trace(go.Scatter(
        x=list(range(1, int(total_laps) + 1)),
        y=[1] * int(total_laps),
        mode='lines',
        line=dict(color='gray', width=10),
        name='Race',
        hoverinfo='skip'
    ))

    # Actual pits
    fig.add_trace(go.Scatter(
        x=actual_pit_laps,
        y=[1] * len(actual_pit_laps),
        mode='markers',
        marker=dict(size=20, color='red', symbol='x'),
        name='Actual Pit Stops',
        text=[f'Lap {lap}' for lap in actual_pit_laps],
        hoverinfo='text'
    ))

    # AI recommendations
    ai_laps = [d['lap'] for d in ai_pit_laps]
    fig.add_trace(go.Scatter(
        x=ai_laps,
        y=[1] * len(ai_laps),
        mode='markers',
        marker=dict(size=20, color='lime', symbol='diamond'),
        name='AI Recommendations',
        text=[f"Lap {d['lap']}: {d['compound']}" for d in ai_pit_laps],
        hoverinfo='text'
    ))

    fig.update_layout(
        title=f"{driver} - Pit Stop Strategy Timeline",
        xaxis_title="Lap Number",
        yaxis=dict(showticklabels=False),
        height=300,
        showlegend=True,
        plot_bgcolor='#0E1117',
        paper_bgcolor='#0E1117',
        font=dict(color='white')
    )

    return fig


def plot_tire_degradation_comparison(tire_model):
    """Plot tire degradation curves"""

    compounds = ['SOFT', 'MEDIUM', 'HARD']
    colors = {'SOFT': 'red', 'MEDIUM': 'yellow', 'HARD': 'white'}

    fig = go.Figure()

    for compound in compounds:
        stint_pred = tire_model.predict_stint_degradation(
            compound=compound,
            max_laps=40,
            lap_number=20,
            position=5
        )

        fig.add_trace(go.Scatter(
            x=stint_pred['TyreLife'],
            y=stint_pred['PredictedLapTime'],
            mode='lines+markers',
            name=compound,
            line=dict(color=colors[compound], width=3),
            marker=dict(size=6)
        ))

    fig.update_layout(
        title="Tire Degradation Prediction",
        xaxis_title="Tire Life (laps)",
        yaxis_title="Predicted Lap Time (seconds)",
        height=400,
        legend=dict(x=0.02, y=0.98),
        plot_bgcolor='#0E1117',
        paper_bgcolor='#0E1117',
        font=dict(color='white'),
        hovermode='x unified'
    )

    return fig


def plot_lap_time_comparison(driver_laps, ai_pit_laps, actual_pit_laps):
    """Plot lap times with pit stops marked"""

    fig = go.Figure()

    # Lap times
    valid_laps = driver_laps[driver_laps['LapTimeSeconds'].notna()].copy()

    fig.add_trace(go.Scatter(
        x=valid_laps['LapNumber'],
        y=valid_laps['LapTimeSeconds'],
        mode='lines+markers',
        name='Lap Time',
        line=dict(color='cyan', width=2),
        marker=dict(size=4)
    ))

    # Mark actual pit stops
    for lap in actual_pit_laps:
        fig.add_vline(
            x=lap,
            line=dict(color='red', width=2, dash='dash'),
            annotation_text=f"Pit {lap}",
            annotation_position="top"
        )

    # Mark AI recommendations
    for decision in ai_pit_laps:
        fig.add_vline(
            x=decision['lap'],
            line=dict(color='lime', width=2, dash='dot'),
            annotation_text=f"AI {decision['lap']}",
            annotation_position="bottom"
        )

    fig.update_layout(
        title="Lap Time Analysis",
        xaxis_title="Lap Number",
        yaxis_title="Lap Time (seconds)",
        height=400,
        plot_bgcolor='#0E1117',
        paper_bgcolor='#0E1117',
        font=dict(color='white'),
        showlegend=True
    )

    return fig


def plot_position_changes(driver_laps):
    """Plot position throughout race"""

    fig = go.Figure()

    valid_positions = driver_laps[driver_laps['Position'].notna()].copy()

    fig.add_trace(go.Scatter(
        x=valid_positions['LapNumber'],
        y=valid_positions['Position'],
        mode='lines+markers',
        name='Position',
        line=dict(color='gold', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(255, 215, 0, 0.2)'
    ))

    fig.update_layout(
        title="Race Position",
        xaxis_title="Lap Number",
        yaxis_title="Position",
        yaxis=dict(autorange='reversed'),  # P1 at top
        height=300,
        plot_bgcolor='#0E1117',
        paper_bgcolor='#0E1117',
        font=dict(color='white')
    )

    return fig


# Main App
def main():
    # Header
    st.markdown('<h1 class="main-header">🏎️ F1 Strategy Optimizer AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #888;">Real-time pit stop decision engine powered by Machine Learning</p>', unsafe_allow_html=True)

    # Sidebar
    st.sidebar.title("⚙️ Configuration")

    year = st.sidebar.selectbox("Season", [2024, 2023], index=0)

    # Race selection
    races_2024 = ['Bahrain', 'Saudi Arabia', 'Australia', 'Japan', 'China',
                  'Miami', 'Emilia Romagna', 'Monaco', 'Canada', 'Spain',
                  'Austria', 'Great Britain', 'Hungary', 'Belgium', 'Netherlands',
                  'Italy', 'Azerbaijan', 'Singapore', 'United States', 'Mexico',
                  'Brazil', 'Las Vegas', 'Qatar', 'Abu Dhabi']

    race = st.sidebar.selectbox("Grand Prix", races_2024, index=races_2024.index('Monaco'))

    # Load data
    try:
        processor, tire_model, optimizer, lap_data, model_metrics = load_tire_model(year, race)
        race_summary = get_race_summary(processor)
    except Exception as e:
        st.error(f"Error loading race data: {str(e)}")
        st.stop()

    # Driver selection
    drivers = sorted(lap_data['Driver'].unique().tolist())
    selected_driver = st.sidebar.selectbox("Driver", drivers, index=0)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 Model Performance")
    st.sidebar.metric("Test MAE", f"{model_metrics['test_mae']:.3f}s")
    st.sidebar.metric("Test R²", f"{model_metrics['test_r2']:.3f}")
    st.sidebar.metric("Training Samples", f"{model_metrics['train_samples']:,}")

    # Main dashboard
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🏁 Race", race_summary['race'])
    with col2:
        st.metric("🏆 Winner", race_summary['winner'])
    with col3:
        st.metric("📊 Total Laps", race_summary['total_laps'])
    with col4:
        st.metric("🔧 Total Pit Stops", race_summary['total_pit_stops'])

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📍 Strategy Analysis", "📈 Tire Model", "🔮 Live Simulator", "📊 Backtest Results"])

    with tab1:
        st.subheader(f"Strategy Analysis: {selected_driver}")

        # Run backtest
        backtest_result = optimizer.backtest_race(lap_data, selected_driver)

        if 'error' in backtest_result:
            st.error(backtest_result['error'])
        else:
            actual_pits = backtest_result['actual_pit_laps']
            ai_pits = backtest_result['ai_pit_recommendations']

            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Actual Pit Stops", len(actual_pits))
            with col2:
                st.metric("AI Recommendations", len(ai_pits))
            with col3:
                agreement = backtest_result['agreement_rate'] * 100
                st.metric("Agreement Rate", f"{agreement:.0f}%")

            # Track map
            st.plotly_chart(
                plot_track_map_with_pits(processor, selected_driver, ai_pits, actual_pits),
                use_container_width=True
            )

            # Lap times
            driver_laps = lap_data[lap_data['Driver'] == selected_driver].copy()
            driver_laps['LapTimeSeconds'] = driver_laps['LapTimeSeconds']

            col1, col2 = st.columns(2)

            with col1:
                st.plotly_chart(
                    plot_lap_time_comparison(driver_laps, ai_pits, actual_pits),
                    use_container_width=True
                )

            with col2:
                st.plotly_chart(
                    plot_position_changes(driver_laps),
                    use_container_width=True
                )

            # Detailed recommendations
            st.subheader("🤖 AI Recommendations Details")

            for i, rec in enumerate(ai_pits, 1):
                with st.expander(f"Recommendation {i}: Lap {rec['lap']} - {rec['compound']} ({rec['confidence']*100:.0f}% confidence)"):
                    st.write(f"**Reasoning:** {rec['reasoning']}")

            # Actual strategy
            st.subheader("🏁 Actual Strategy")
            pit_stops_df = processor.extract_pit_stop_data()
            driver_pits = pit_stops_df[pit_stops_df['Driver'] == selected_driver]

            if len(driver_pits) > 0:
                st.dataframe(
                    driver_pits[['LapPitted', 'TireBefore', 'TireAfter', 'LapsOnTire', 'PositionBefore', 'PositionAfter']],
                    use_container_width=True
                )

    with tab2:
        st.subheader("Tire Degradation Model")

        st.plotly_chart(
            plot_tire_degradation_comparison(tire_model),
            use_container_width=True
        )

        # Optimal stint lengths
        st.subheader("⏱️ Optimal Stint Lengths")

        col1, col2, col3 = st.columns(3)

        for compound, col in zip(['SOFT', 'MEDIUM', 'HARD'], [col1, col2, col3]):
            optimal_laps = tire_model.get_optimal_stint_length(
                compound=compound,
                threshold_seconds=1.5,
                lap_number=20
            )

            with col:
                st.metric(
                    f"🔴 {compound}" if compound == 'SOFT' else f"🟡 {compound}" if compound == 'MEDIUM' else f"⚪ {compound}",
                    f"{optimal_laps} laps"
                )

    with tab3:
        st.subheader("🔮 Live Decision Simulator")

        st.write("Simulate real-time pit stop decisions")

        col1, col2 = st.columns(2)

        with col1:
            sim_lap = st.slider("Current Lap", 1, race_summary['total_laps'], 25)
            sim_position = st.slider("Current Position", 1, 20, 5)
            sim_tire = st.selectbox("Current Tire", ['SOFT', 'MEDIUM', 'HARD'], index=1)
            sim_tire_life = st.slider("Tire Age (laps)", 1, 40, 15)

        with col2:
            sim_gap_ahead = st.number_input("Gap to car ahead (s)", 0.0, 30.0, 2.1, 0.1)
            sim_gap_behind = st.number_input("Gap to car behind (s)", 0.0, 30.0, 3.5, 0.1)
            sim_track_status = st.selectbox("Track Status",
                                           ['🟢 Green Flag', '🟡 Yellow Flag', '🔶 Safety Car'],
                                           index=0)

        # Convert track status
        status_map = {'🟢 Green Flag': '1', '🟡 Yellow Flag': '2', '🔶 Safety Car': '4'}

        if st.button("🎯 Get AI Decision", type="primary"):
            race_state = RaceState(
                current_lap=sim_lap,
                total_laps=race_summary['total_laps'],
                current_position=sim_position,
                tire_compound=sim_tire,
                tire_life=sim_tire_life,
                gap_ahead=sim_gap_ahead,
                gap_behind=sim_gap_behind,
                fuel_load=race_summary['total_laps'] - sim_lap,
                track_status=status_map[sim_track_status]
            )

            decision = optimizer.make_decision(race_state)

            # Display decision
            st.markdown("---")

            if decision.should_pit:
                st.success(f"## 🔧 PIT NOW!")
                st.metric("Confidence", f"{decision.confidence*100:.0f}%")
                st.metric("Recommended Compound", decision.recommended_compound)

                if decision.expected_position_change != 0:
                    st.metric("Expected Position Change", f"{decision.expected_position_change:+d}")

                if decision.expected_time_delta != 0:
                    st.metric("Expected Time Delta", f"{decision.expected_time_delta:+.2f}s")
            else:
                st.info(f"## 🏁 STAY OUT")

                if decision.alternative_lap:
                    st.metric("Optimal Pit Window", f"Lap {decision.alternative_lap}")

            st.subheader("💭 Reasoning")
            for reason in decision.reasoning:
                st.write(f"- {reason}")

    with tab4:
        st.subheader("📊 Multi-Driver Backtest")

        # Backtest all drivers
        backtest_results = []

        progress_bar = st.progress(0)

        for i, driver in enumerate(drivers[:10]):  # Top 10 drivers
            result = optimizer.backtest_race(lap_data, driver)
            if 'error' not in result:
                backtest_results.append({
                    'Driver': driver,
                    'Actual Pits': len(result['actual_pit_laps']),
                    'AI Recommendations': len(result['ai_pit_recommendations']),
                    'Agreement Rate': f"{result['agreement_rate']*100:.0f}%"
                })
            progress_bar.progress((i + 1) / min(10, len(drivers)))

        if backtest_results:
            results_df = pd.DataFrame(backtest_results)
            st.dataframe(results_df, use_container_width=True)

            # Chart
            fig = px.bar(
                results_df,
                x='Driver',
                y=['Actual Pits', 'AI Recommendations'],
                title='Pit Stop Strategy Comparison',
                barmode='group',
                color_discrete_map={'Actual Pits': '#E10600', 'AI Recommendations': '#00FF00'}
            )

            fig.update_layout(
                plot_bgcolor='#0E1117',
                paper_bgcolor='#0E1117',
                font=dict(color='white')
            )

            st.plotly_chart(fig, use_container_width=True)

    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666;">Built for HackTX 2025 | Powered by FastF1, Scikit-learn, and Streamlit</p>',
        unsafe_allow_html=True
    )


if __name__ == '__main__':
    main()
