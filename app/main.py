import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="GitHub Peru Analytics",
    page_icon="🇵🇪",
    layout="wide"
)

USERS_CSV = "data/processed/users_metrics.csv"
REPOS_CSV = "data/processed/repos_metrics.csv"

# Check if data exists
if not os.path.exists(USERS_CSV) or not os.path.exists(REPOS_CSV):
    st.error("Processed data not found. Please run the data extraction and processing pipeline first. (`python scripts/extract_data.py` -> `python scripts/classify_data.py` -> `python scripts/process_metrics.py`)")
    st.info("Since we are currently extracting the data, this message will disappear once you run `process_metrics.py`.")
    st.stop()

@st.cache_data
def load_data():
    df_users = pd.read_csv(USERS_CSV)
    df_repos = pd.read_csv(REPOS_CSV)
    # Fill NaN values for cleaner displays
    df_repos['language'] = df_repos['language'].fillna('Unknown')
    df_repos['industry_name'] = df_repos['industry_name'].fillna('Unclassified')
    return df_users, df_repos

df_users, df_repos = load_data()

# -----------------
# NAVIGATION / TABS
# -----------------
st.title("🇵🇪 GitHub Peru Analytics Dashboard")
st.markdown("Explore the developer ecosystem of Peru based on GitHub data.")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Overview Dashboard", 
    "👨‍💻 Developer Explorer", 
    "📁 Repository Browser", 
    "🏢 Industry Analysis", 
    "💻 Language Analytics"
])

# ==========================================
# PAGE 1: Overview Dashboard
# ==========================================
with tab1:
    st.header("Overview Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Developers", f"{len(df_users):,}")
    col2.metric("Total Repositories", f"{len(df_repos):,}")
    col3.metric("Total Stars Received", f"{int(df_users['total_stars_received'].sum()):,}")
    top_lang = df_repos['language'].mode()[0] if not df_repos['language'].empty else "N/A"
    col4.metric("Most Popular Language", top_lang)

    st.divider()
    
    col_dev, col_repo = st.columns(2)
    with col_dev:
        st.subheader("Top 10 Developers by Impact Score")
        top_impact = df_users.sort_values(by="impact_score", ascending=False).head(10)
        fig_impact = px.bar(top_impact, x="username", y="impact_score", color="total_stars_received", title="Impact Score")
        st.plotly_chart(fig_impact, use_container_width=True)

    with col_repo:
        st.subheader("Top 10 Repositories by Stars")
        top_stars = df_repos.sort_values(by="stars", ascending=False).head(10)
        fig_stars = px.bar(top_stars, x="name", y="stars", color="language", title="Most Starred Repos", hover_data=["owner"])
        st.plotly_chart(fig_stars, use_container_width=True)


# ==========================================
# PAGE 2: Developer Explorer
# ==========================================
with tab2:
    st.header("Developer Explorer")
    st.markdown("Search and filter all developers and download the results.")
    
    # Optional filtering
    min_stars = st.slider("Minimum Stars Received", int(df_users['total_stars_received'].min()), int(df_users['total_stars_received'].max()), 0)
    filtered_users = df_users[df_users['total_stars_received'] >= min_stars]
    
    display_cols = ["username", "name", "total_repos", "total_stars_received", "h_index", "impact_score", "primary_languages"]
    st.dataframe(filtered_users[display_cols], use_container_width=True, hide_index=True)
    
    # Export to CSV
    csv_devs = filtered_users.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Developers CSV",
        data=csv_devs,
        file_name='peru_developers.csv',
        mime='text/csv',
    )


# ==========================================
# PAGE 3: Repository Browser
# ==========================================
with tab3:
    st.header("Repository Browser")
    
    col_filt1, col_filt2 = st.columns(2)
    with col_filt1:
        lang_filter = st.selectbox("Filter by Language", ["All"] + list(df_repos["language"].unique()))
    with col_filt2:
        ind_filter = st.selectbox("Filter by Industry", ["All"] + list(df_repos["industry_name"].unique()))
    
    view_repos = df_repos.copy()
    if lang_filter != "All":
        view_repos = view_repos[view_repos["language"] == lang_filter]
    if ind_filter != "All":
        view_repos = view_repos[view_repos["industry_name"] == ind_filter]
        
    st.dataframe(
        view_repos[["name", "owner", "language", "stars", "industry_name", "description"]],
        use_container_width=True,
        hide_index=True
    )

# ==========================================
# PAGE 4: Industry Analysis
# ==========================================
with tab4:
    st.header("Industry Analysis")
    st.markdown("How GitHub repositories are distributed across different economic industries (CIIU).")
    
    industry_counts = df_repos["industry_name"].value_counts().reset_index()
    industry_counts.columns = ["Industry", "Count"]
    
    # Filter out Unclassified for the pie chart to see actual industries better
    valid_industries = industry_counts[industry_counts["Industry"] != "Unclassified"]
    
    if len(valid_industries) > 0:
        col_ind1, col_ind2 = st.columns(2)
        with col_ind1:
            fig_ind_pie = px.pie(valid_industries, names="Industry", values="Count", title="Distribution of Industries", hole=0.3)
            st.plotly_chart(fig_ind_pie, use_container_width=True)
            
        with col_ind2:
            fig_ind_bar = px.bar(
                valid_industries.head(10), 
                x="Count", 
                y="Industry", 
                orientation='h', 
                title="Top 10 Industries by Repository Applied Use"
            )
            fig_ind_bar.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_ind_bar, use_container_width=True)
    else:
        st.info("No classified industry data available yet.")


# ==========================================
# PAGE 5: Language Analytics
# ==========================================
with tab5:
    st.header("Language Analytics")
    
    lang_counts = df_repos["language"].value_counts().reset_index()
    lang_counts.columns = ["Language", "Count"]
    # Filter out Unknown
    lang_counts = lang_counts[lang_counts["Language"] != "Unknown"]
    
    col_l1, col_l2 = st.columns([2, 1])
    with col_l1:
        fig_lang = px.bar(
            lang_counts.head(15), 
            x="Language", 
            y="Count", 
            title="Top 15 Programming Languages Used",
            color="Count"
        )
        st.plotly_chart(fig_lang, use_container_width=True)
    with col_l2:
        st.dataframe(lang_counts.head(15), hide_index=True, use_container_width=True)


# ==========================================
# AI Insights Agent (Sidebar Chat)
# ==========================================
st.sidebar.divider()
st.sidebar.header("🤖 Antigravity AI Agent")
st.sidebar.markdown("Ask the AI about this dataset!")

# Initialize agent connection once data is loaded
try:
    from src.agents.insights_agent import InsightsAgent
    agent = InsightsAgent(USERS_CSV, REPOS_CSV)
    
    user_query = st.sidebar.text_input("Ask a question:", placeholder="e.g. What is the most popular language?")
    if st.sidebar.button("Ask AI"):
        if user_query:
            with st.sidebar.spinner("Thinking..."):
                answer = agent.ask(user_query)
            st.sidebar.info(answer)
        else:
            st.sidebar.warning("Please enter a question.")
except Exception as e:
    st.sidebar.error("AI Agent currently unavailable. Check your OpenAI Key configuration.")
