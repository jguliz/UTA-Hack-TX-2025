"""
AI Racing Dashboard - Watch AI compete live against F1 drivers
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import json

from data_processor import F1DataProcessor
from tire_model import TireDegradationModel
from pit_optimizer import PitStopOptimizer
from racing_agent import RacingAI
from race_simulator import RaceSimulator, train_ai_multiple_races

# Page config
st.set_page_config(
    page_title="AI F1 Racer",
    page_icon="🏎️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(135deg, #E10600 0%, #FF6B00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .position-badge {
        font-size: 2rem;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        display: inline-block;
    }
    .ai-row {
        background-color: #00FF00 !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_race_and_models(year: int, race_name: str):
    """Load race data and train models"""
    processor = F1DataProcessor(year, race_name)
    processor.load_race_data()
    lap_data = processor.extract_lap_features()

    tire_model = TireDegradationModel()
    tire_model.train(lap_data)

    optimizer = PitStopOptimizer(tire_model, pit_loss_time=24.0)

    return processor, tire_model, optimizer, lap_data


def plot_live_standings(standings_df: pd.DataFrame, current_lap: int):
    """Plot current race standings"""
    current_standings = standings_df[standings_df['Lap'] == current_lap].sort_values('Position')

    # Create horizontal bar chart
    fig = go.Figure()

    for _, row in current_standings.iterrows():
        color = 'lime' if row['IsAI'] else 'lightblue'

        fig.add_trace(go.Bar(
            y=[row['Driver']],
            x=[row['TotalTime']],
            orientation='h',
            name=row['Driver'],
            marker=dict(color=color),
            text=f"P{row['Position']} - {row['TotalTime']:.1f}s",
            textposition='inside',
            showlegend=False
        ))

    fig.update_layout(
        title=f"Live Standings - Lap {current_lap}",
        xaxis_title="Cumulative Time (seconds)",
        yaxis_title="",
        height=600,
        plot_bgcolor='#0E1117',
        paper_bgcolor='#0E1117',
        font=dict(color='white'),
        yaxis=dict(categoryorder='total ascending')
    )

    return fig


def plot_position_chart(standings_df: pd.DataFrame, highlight_drivers: list = None):
    """Plot position changes over race"""
    fig = go.Figure()

    # Get all drivers
    drivers = standings_df['Driver'].unique()

    if highlight_drivers is None:
        highlight_drivers = []

    for driver in drivers:
        driver_data = standings_df[standings_df['Driver'] == driver].sort_values('Lap')

        is_ai = driver_data['IsAI'].iloc[0] if len(driver_data) > 0 else False
        is_highlighted = driver in highlight_drivers

        line_width = 4 if is_ai else 2
        line_color = 'lime' if is_ai else None
        opacity = 1.0 if (is_ai or is_highlighted) else 0.3

        fig.add_trace(go.Scatter(
            x=driver_data['Lap'],
            y=driver_data['Position'],
            mode='lines',
            name=driver,
            line=dict(width=line_width, color=line_color),
            opacity=opacity,
            hovertemplate=f'<b>{driver}</b><br>Lap: %{{x}}<br>Position: P%{{y}}<extra></extra>'
        ))

    fig.update_layout(
        title="Position Throughout Race",
        xaxis_title="Lap",
        yaxis_title="Position",
        yaxis=dict(autorange='reversed'),
        height=500,
        plot_bgcolor='#0E1117',
        paper_bgcolor='#0E1117',
        font=dict(color='white'),
        hovermode='x unified',
        showlegend=True,
        legend=dict(x=1.05, y=1)
    )

    return fig


def plot_decision_timeline(ai_agent: RacingAI):
    """Plot AI decision timeline"""
    pit_events = [e for e in ai_agent.race_events if e.event_type == 'pit_decision']

    if not pit_events:
        return None

    laps = [e.lap for e in pit_events]
    decisions = [e.data['decision'] for e in pit_events]
    confidences = [e.data['confidence'] * 100 for e in pit_events]

    colors = ['green' if d == 'PIT' else 'gray' for d in decisions]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=laps,
        y=confidences,
        mode='markers+text',
        marker=dict(
            size=[20 if d == 'PIT' else 10 for d in decisions],
            color=colors,
            line=dict(width=2, color='white')
        ),
        text=decisions,
        textposition='top center',
        hovertemplate='Lap %{x}<br>Confidence: %{y:.0f}%<extra></extra>'
    ))

    fig.update_layout(
        title="AI Decision Timeline",
        xaxis_title="Lap",
        yaxis_title="Confidence (%)",
        height=300,
        plot_bgcolor='#0E1117',
        paper_bgcolor='#0E1117',
        font=dict(color='white')
    )

    return fig


def main():
    st.markdown('<h1 class="main-header">🏎️ AI F1 Racing Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.3rem;">Watch AI compete live against real F1 drivers</p>', unsafe_allow_html=True)

    # Sidebar
    st.sidebar.title("🎮 Race Configuration")

    mode = st.sidebar.radio("Mode", ["Single Race", "Training Mode"])

    year = 2024
    races_2024 = ['Bahrain', 'Saudi Arabia', 'Australia', 'Monaco', 'Spain',
                  'Austria', 'Great Britain', 'Belgium', 'Netherlands', 'Italy']

    if mode == "Single Race":
        race = st.sidebar.selectbox("Race", races_2024, index=races_2024.index('Monaco'))

        st.sidebar.markdown("### 🤖 AI Configuration")
        starting_pos = st.sidebar.slider("Starting Position", 1, 20, 15)
        aggression = st.sidebar.slider("Aggression", 0.0, 1.0, 0.75, 0.05)
        risk_tolerance = st.sidebar.slider("Risk Tolerance", 0.0, 1.0, 0.6, 0.05)
        starting_tire = st.sidebar.selectbox("Starting Tire", ['SOFT', 'MEDIUM', 'HARD'], index=1)

        # Load data
        try:
            processor, tire_model, optimizer, lap_data = load_race_and_models(year, race)

            # Create AI
            ai = RacingAI(tire_model, optimizer, strategy_params={
                'aggression': aggression,
                'risk_tolerance': risk_tolerance,
                'tire_preference': starting_tire
            })

            # Simulate button
            if st.sidebar.button("🏁 START RACE", type="primary"):
                with st.spinner("Simulating race..."):
                    simulator = RaceSimulator(processor, ai)
                    standings = simulator.simulate_full_race(starting_pos, starting_tire)

                    # Store in session state
                    st.session_state['standings'] = standings
                    st.session_state['simulator'] = simulator
                    st.session_state['ai'] = ai

            # Display results if available
            if 'standings' in st.session_state:
                standings = st.session_state['standings']
                simulator = st.session_state['simulator']
                ai = st.session_state['ai']

                # Race summary
                summary = ai.get_race_summary()

                st.markdown("---")

                # Top metrics
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    position_color = "green" if summary['positions_gained'] > 0 else "red"
                    st.metric(
                        "Final Position",
                        f"P{summary['final_position']}",
                        f"{summary['positions_gained']:+d} positions"
                    )

                with col2:
                    st.metric("Pit Stops", summary['total_pit_stops'])

                with col3:
                    st.metric("Avg Lap Time", f"{summary['average_lap_time']:.3f}s")

                with col4:
                    st.metric("Best Lap", f"{summary['best_lap_time']:.3f}s")

                # Tabs
                tab1, tab2, tab3, tab4 = st.tabs([
                    "🏁 Live Replay",
                    "📊 Final Classification",
                    "🧠 AI Decisions",
                    "📈 Analysis"
                ])

                with tab1:
                    st.subheader("Race Replay")

                    total_laps = int(standings['Lap'].max())

                    # Lap selector
                    replay_lap = st.slider("Lap", 1, total_laps, total_laps)

                    # Live standings
                    st.plotly_chart(
                        plot_live_standings(standings, replay_lap),
                        use_container_width=True
                    )

                    # Current lap info
                    current = standings[
                        (standings['Lap'] == replay_lap) &
                        (standings['Driver'] == ai.ai_state.driver_name)
                    ]

                    if len(current) > 0:
                        current = current.iloc[0]
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("Position", f"P{int(current['Position'])}")
                        with col2:
                            st.metric("Tire", current['Compound'])
                        with col3:
                            st.metric("Tire Life", f"{int(current['TyreLife'])} laps")
                        with col4:
                            st.metric("Stint", int(current['Stint']))

                with tab2:
                    st.subheader("Final Classification")

                    final_classification = simulator.get_final_classification(standings)

                    # Highlight AI row
                    def highlight_ai(row):
                        if row['IsAI']:
                            return ['background-color: #00FF00; font-weight: bold'] * len(row)
                        return [''] * len(row)

                    styled_df = final_classification[
                        ['Position', 'Driver', 'Team', 'TimeDeltaStr', 'Stint']
                    ].style.apply(highlight_ai, axis=1)

                    st.dataframe(styled_df, use_container_width=True, height=600)

                    # Overtakes
                    overtakes = simulator.get_ai_overtakes(standings)

                    if overtakes:
                        st.subheader(f"🎯 AI Overtakes: {len(overtakes)}")

                        for overtake in overtakes:
                            st.write(
                                f"**Lap {overtake['lap']}:** "
                                f"P{overtake['from_position']} → P{overtake['to_position']} "
                                f"(Overtook: {', '.join(overtake['overtaken'])})"
                            )

                with tab3:
                    st.subheader("AI Decision Log")

                    # Decision timeline
                    decision_chart = plot_decision_timeline(ai)
                    if decision_chart:
                        st.plotly_chart(decision_chart, use_container_width=True)

                    # Detailed decisions
                    decision_log = ai.get_decision_log()

                    if len(decision_log) > 0:
                        st.dataframe(decision_log, use_container_width=True)

                    # Pit stops
                    if ai.ai_state.pit_stops:
                        st.subheader("Pit Stop Details")

                        for i, pit in enumerate(ai.ai_state.pit_stops, 1):
                            with st.expander(f"Pit Stop {i} - Lap {pit['lap']}"):
                                col1, col2, col3 = st.columns(3)

                                with col1:
                                    st.write(f"**Old Tire:** {pit['old_compound']}")
                                    st.write(f"**Tire Age:** {pit['old_tire_life']} laps")

                                with col2:
                                    st.write(f"**New Tire:** {pit['new_compound']}")
                                    st.write(f"**Time Loss:** {pit['time_loss']:.2f}s")

                with tab4:
                    st.subheader("Race Analysis")

                    # Position chart
                    st.plotly_chart(
                        plot_position_chart(standings, highlight_drivers=['AI_RACER']),
                        use_container_width=True
                    )

                    # Performance comparison
                    final_standings = standings[standings['Lap'] == total_laps].sort_values('Position')
                    winner = final_standings.iloc[0]
                    ai_final = final_standings[final_standings['IsAI'] == True].iloc[0]

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric("Winner", winner['Driver'])
                        st.metric("Winner Time", f"{winner['TotalTime']:.2f}s")

                    with col2:
                        st.metric("AI Time", f"{ai_final['TotalTime']:.2f}s")
                        time_delta = ai_final['TotalTime'] - winner['TotalTime']
                        st.metric("Time Delta", f"+{time_delta:.2f}s")

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.exception(e)

    else:  # Training Mode
        st.sidebar.markdown("### 🎓 Training Configuration")

        training_races = st.sidebar.multiselect(
            "Select Races",
            races_2024,
            default=['Monaco', 'Spain', 'Austria']
        )

        epochs = st.sidebar.slider("Training Epochs", 1, 5, 2)

        if st.sidebar.button("🚀 Start Training", type="primary"):
            if len(training_races) == 0:
                st.warning("Please select at least one race")
            else:
                with st.spinner(f"Training AI on {len(training_races)} races for {epochs} epochs..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    # This would need to be adapted to show progress
                    # For now, just run training
                    trained_ai = train_ai_multiple_races(training_races, year, epochs)

                    st.success(f"✅ Training complete!")

                    # Show results
                    if trained_ai.race_results_history:
                        results_df = pd.DataFrame(trained_ai.race_results_history)

                        st.subheader("Training Results")
                        st.dataframe(results_df)

                        # Plot improvement
                        fig = px.line(
                            results_df,
                            x=results_df.index,
                            y='position',
                            title='AI Performance Over Training',
                            labels={'x': 'Race Number', 'position': 'Final Position'}
                        )

                        fig.update_layout(
                            yaxis=dict(autorange='reversed'),
                            plot_bgcolor='#0E1117',
                            paper_bgcolor='#0E1117',
                            font=dict(color='white')
                        )

                        st.plotly_chart(fig, use_container_width=True)


if __name__ == '__main__':
    main()
