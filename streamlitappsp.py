import streamlit as st
import pandas as pd
import plotly.express as px
import io
import requests
import json

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Interactive Media Intelligence Dashboard",
    page_icon="📊",
    layout="wide", # Use wide layout for better chart visibility
    initial_sidebar_state="expanded"
)

# --- Custom CSS for a Modern, Futuristic Look ---
# This CSS attempts to mimic the dark theme and rounded styles from the React/HTML app
st.markdown("""
<style>
    /* Main container background */
    .stApp {
        background-color: #0F172A; /* bg-gray-900 */
        color: #D1D5DB; /* text-gray-300 */
        font-family: 'Inter', sans-serif;
    }

    /* Overall block container padding */
    .st-emotion-cache-1pxazr7 { /* Target the main block container */
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #A78BFA; /* purple-400 */
        font-family: 'Inter', sans-serif;
        margin-bottom: 1rem;
    }
    h1 {
        font-size: 3.5rem; /* text-5xl */
        font-weight: 700; /* font-bold */
        text-align: center;
        margin-bottom: 3rem; /* mb-12 */
        color: #C084FC; /* Brighter purple for main title */
    }
    h2 {
        font-size: 2.25rem; /* text-3xl */
        font-weight: 600; /* font-semibold */
        margin-bottom: 1.5rem; /* mb-6 */
        color: #2DD4BF; /* teal-400 */
    }
    h3 {
        font-size: 1.25rem; /* text-xl */
        font-weight: 600; /* font-semibold */
        margin-top: 1.5rem; /* mt-6 */
        margin-bottom: 0.75rem; /* mb-3 */
        color: #BF80FF; /* purple-300 - adjusted for better contrast */
    }

    /* Paragraphs and list items */
    p, li, code {
        color: #D1D5DB; /* gray-300 */
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
    }
    code {
        background-color: #374151; /* gray-700 */
        border-radius: 0.25rem;
        padding: 0.2rem 0.4rem;
        color: #E879F9; /* purple-300 - adjusted for better contrast */
    }

    /* File Uploader styling */
    .stFileUploader {
        background-color: #1F2937; /* Darker gray */
        border-radius: 0.75rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 2px dashed #4B5563; /* border-gray-600 */
        text-align: center;
        margin-bottom: 3rem; /* mb-12 */
        transition: all 0.3s ease-in-out;
    }
    .stFileUploader:hover {
        box-shadow: 0 0 15px rgba(129, 140, 248, 0.6); /* Tailwind indigo-300 with blur */
        transform: translateY(-2px);
    }
    /* Specific styling for the 'Choose File' button within the uploader */
    .st-emotion-cache-1wmy99l, .st-emotion-cache-1wmy99l:hover { /* This targets the actual button */
        background-color: #8B5CF6; /* purple-600 */
        color: white;
        font-weight: bold;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        transition: all 0.3s ease-in-out;
        border: none;
    }
    .st-emotion-cache-1wmy99l:hover {
        background-color: #7C3AED; /* purple-700 */
        box-shadow: 0 0 10px rgba(129, 140, 248, 0.4);
    }

    /* Chart container styling (similar to chart-container in HTML) */
    .chart-container {
        background-color: #1F2937; /* Darker gray */
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease-in-out;
        margin-bottom: 2.5rem; /* mb-10 */
        border: none; /* Remove default Streamlit border */
    }
    .chart-container:hover {
        box-shadow: 0 0 15px rgba(129, 140, 248, 0.6);
        transform: translateY(-2px);
    }

    /* Plotly chart specific styling */
    .stPlotlyChart {
        border-radius: 0.5rem; /* Apply some rounding to charts too */
        background-color: #1F2937; /* Ensure plotly background matches container */
    }

    /* Spinner color */
    .stSpinner > div > span {
        color: #A78BFA;
    }

    /* Success/Error/Info messages */
    .stAlert {
        border-radius: 0.5rem;
        background-color: #1F2937;
        color: #D1D5DB;
    }
    .stAlert.success {
        border-left: 5px solid #2ECC71;
    }
    .stAlert.error {
        border-left: 5px solid #E74C3C;
    }
    .stAlert.warning {
        border-left: 5px solid #F1C40F;
    }

    /* List styling for data cleaning section */
    ul {
        list-style-type: disc;
        padding-left: 1.5rem;
        color: #9CA3AF; /* gray-400 */
        margin-top: 0.5rem;
    }
    li {
        margin-bottom: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# --- API Key for Gemini (Placeholder for Canvas Environment) ---
# In a real Streamlit deployment, you'd securely manage this using st.secrets.
# For this Canvas environment, the API key will be automatically provided by the backend for the fetch call.
GEMINI_API_KEY = "" # Leave as empty string for Canvas auto-injection

# --- Helper Function for Gemini API Call ---
@st.cache_data(show_spinner=False) # Cache API responses to avoid re-calling on rerun
def call_gemini_api(prompt):
    """
    Makes a request to the Gemini API to generate insights.
    Uses the 'gemini-2.0-flash' model.
    """
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": prompt}]}
            ]
        }

        # Make the request
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        result = response.json()

        # Parse the response
        if result.get('candidates') and result['candidates'][0].get('content') and result['candidates'][0]['content'].get('parts'):
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            # Log the full unexpected response for debugging
            st.error(f"Unexpected API response structure or empty content: {result}")
            return "Could not generate insights due to an unexpected API response. Please check console for details."
    except requests.exceptions.RequestException as e:
        # Catch network errors, HTTP errors, etc.
        st.error(f"Failed to generate insights: {e}. Please check your network connection or API key.")
        return "Failed to generate insights due to a network or API error."
    except json.JSONDecodeError:
        st.error("Failed to decode JSON response from API. Invalid response format.")
        return "Failed to generate insights due to invalid API response format."
    except Exception as e:
        st.error(f"An unexpected error occurred during API call: {e}")
        return "An unknown error occurred while generating insights."


# --- 1. Data Cleaning Function ---
def clean_data(df):
    """
    Cleans and normalizes the input DataFrame based on specified requirements.
    - Converts 'Date' to datetime.
    - Fills missing 'Engagements' with 0.
    - Normalizes column names (lowercase, replace spaces with underscores).
    - Filters out rows with invalid dates after conversion.
    """
    # Normalize column names first to ensure consistency for subsequent operations
    df.columns = [col.lower().replace(' ', '_').strip() for col in df.columns]

    # Define expected columns for validation
    expected_columns = ['date', 'platform', 'sentiment', 'location', 'engagements', 'media_type']

    # Check if all expected columns are present
    if not all(col in df.columns for col in expected_columns):
        missing_cols = [col for col in expected_columns if col not in df.columns]
        st.error(f"Error: Missing one or more required columns in the CSV. "
                 f"Please ensure your file contains: {', '.join(expected_columns)}. "
                 f"Missing: {', '.join(missing_cols)}")
        return None

    # Convert 'date' to datetime objects, coercing errors to NaT (Not a Time)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    # Filter out rows where 'date' could not be converted (is NaT)
    initial_rows = len(df)
    df.dropna(subset=['date'], inplace=True)
    if len(df) < initial_rows:
        st.warning(f"Removed {initial_rows - len(df)} rows due to invalid 'Date' values.")


    # Fill missing 'engagements' with 0 and convert to integer type
    # Using to_numeric first handles non-numeric strings by converting them to NaN
    df['engagements'] = pd.to_numeric(df['engagements'], errors='coerce').fillna(0).astype(int)

    # Normalize 'sentiment' to lowercase to ensure consistent grouping
    df['sentiment'] = df['sentiment'].astype(str).str.lower()

    # Sort data by date for chronological trend analysis
    df = df.sort_values('date').reset_index(drop=True)

    return df

# --- 2. Chart Generation Functions ---

def create_sentiment_chart(df):
    """Creates a Plotly pie chart for Sentiment Breakdown."""
    sentiment_counts = df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count'] # Rename for clarity in chart
    fig = px.pie(
        sentiment_counts,
        names='Sentiment',
        values='Count',
        title='Sentiment Breakdown',
        hole=0.4, # For a donut chart effect
        color_discrete_map={ # Custom colors for consistent theme
            'positive': '#2ECC71', # Green
            'negative': '#E74C3C', # Red
            'neutral': '#F1C40F',  # Yellow
            'unknown': '#7F8C8D'   # Grey
        }
    )
    # Update layout for dark theme
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', # Transparent background for the plot area
        plot_bgcolor='rgba(0,0,0,0)', # Transparent background for the chart itself
        font_color='#E0E0E0', # Light font color
        title_font_color='#A78BFA', # Purple title
        legend_font_color='#E0E0E0',
        hoverlabel_font_color='#E0E0E0'
    )
    # Update traces for text info and hover info
    fig.update_traces(textinfo="percent+label", hoverinfo="label+percent+value", showlegend=True)
    return fig

def create_engagement_trend_chart(df):
    """Creates a Plotly line chart for Engagement Trend over time."""
    # Group by date (extracting only the date part) and sum engagements
    engagement_by_date = df.groupby(df['date'].dt.date)['engagements'].sum().reset_index()
    engagement_by_date.columns = ['Date', 'Total Engagements']
    fig = px.line(
        engagement_by_date,
        x='Date',
        y='Total Engagements',
        title='Engagement Trend Over Time',
        markers=True, # Show markers at each data point
        line_shape='spline', # Smooth the line for better visual appeal
        color_discrete_sequence=['#3498DB'] # Blue line color
    )
    # Update layout for dark theme
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#E0E0E0',
        title_font_color='#A78BFA',
        xaxis_title_font_color='#E0E0E0',
        yaxis_title_font_color='#E0E0E0',
        xaxis=dict(gridcolor='#444'), # Darker grid lines
        yaxis=dict(gridcolor='#444')
    )
    return fig

def create_platform_engagements_chart(df):
    """Creates a Plotly bar chart for Platform Engagements."""
    # Group by platform, sum engagements, and sort in descending order
    platform_engagements = df.groupby('platform')['engagements'].sum().sort_values(ascending=False).reset_index()
    platform_engagements.columns = ['Platform', 'Total Engagements']
    fig = px.bar(
        platform_engagements,
        x='Platform',
        y='Total Engagements',
        title='Platform Engagements',
        color='Total Engagements', # Color bars based on engagement value
        color_continuous_scale=px.colors.sequential.Plasma # Use a purple-ish color scale
    )
    # Update layout for dark theme
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#E0E0E0',
        title_font_color='#A78BFA',
        xaxis_title_font_color='#E0E0E0',
        yaxis_title_font_color='#E0E0E0',
        xaxis=dict(gridcolor='#444'),
        yaxis=dict(gridcolor='#444')
    )
    return fig

def create_media_type_mix_chart(df):
    """Creates a Plotly pie chart for Media Type Mix."""
    media_type_counts = df['media_type'].value_counts().reset_index()
    media_type_counts.columns = ['Media Type', 'Count']
    fig = px.pie(
        media_type_counts,
        names='Media Type',
        values='Count',
        title='Media Type Mix',
        hole=0.4,
        color_discrete_map={ # Custom colors
            'image': '#1ABC9C', # Teal
            'video': '#F39C12', # Orange
            'text': '#95A5A6',  # Grey
            'other': '#D35400'  # Dark Orange (for unlisted or 'other' types)
        }
    )
    # Update layout for dark theme
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#E0E0E0',
        title_font_color='#A78BFA',
        legend_font_color='#E0E0E0'
    )
    fig.update_traces(textinfo="percent+label", hoverinfo="label+percent+value", showlegend=True)
    return fig

def create_top_locations_chart(df):
    """Creates a Plotly bar chart for Top 5 Locations by Engagements."""
    # Group by location, sum engagements, sort, and get top 5
    location_engagements = df.groupby('location')['engagements'].sum().sort_values(ascending=False).head(5).reset_index()
    location_engagements.columns = ['Location', 'Total Engagements']
    fig = px.bar(
        location_engagements,
        x='Location',
        y='Total Engagements',
        title='Top 5 Locations by Engagements',
        color='Total Engagements',
        color_continuous_scale=px.colors.sequential.Greens # Green color scale
    )
    # Update layout for dark theme
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#E0E0E0',
        title_font_color='#A78BFA',
        xaxis_title_font_color='#E0E0E0',
        yaxis_title_font_color='#E0E0E0',
        xaxis=dict(gridcolor='#444'),
        yaxis=dict(gridcolor='#444')
    )
    return fig

# --- Main Streamlit App Logic ---

# Main application title
st.title("Interactive Media Intelligence Dashboard")

# --- Step 1: Upload CSV File ---
st.markdown("---")
st.header("1. Upload Your CSV File")
uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type="csv",
    help="Expected columns: Date, Platform, Sentiment, Location, Engagements, Media Type"
)

# Process the file if uploaded
if uploaded_file is not None:
    st.success("File uploaded successfully! Processing data...")
    try:
        # Read the CSV into a pandas DataFrame
        data_io = io.BytesIO(uploaded_file.getvalue())
        raw_df = pd.read_csv(data_io)

        # --- Step 2: Data Cleaning & Normalization ---
        # Call the cleaning function
        cleaned_df = clean_data(raw_df.copy()) # Pass a copy to avoid modifying raw_df

        if cleaned_df is not None and not cleaned_df.empty:
            st.markdown("---")
            st.header("2. Data Cleaning & Normalization")
            st.markdown("""
                Your data has been successfully cleaned:
                * 'Date' column converted to datetime objects, invalid dates removed.
                * Missing 'Engagements' values filled with 0.
                * Column names normalized (e.g., `'Media Type'` to `'media_type'`).
            """)
            st.info(f"Successfully processed {len(cleaned_df)} rows of data.")

            # --- Step 3 & 4: Interactive Charts and Top Insights ---
            st.markdown("---")
            st.header("3. Interactive Charts & 4. Top Insights")

            # --- Chart 1: Sentiment Breakdown ---
            st.subheader("Sentiment Breakdown")
            # Create a dedicated container for the chart and its insights
            with st.container():
                st.plotly_chart(create_sentiment_chart(cleaned_df), use_container_width=True)
                sentiment_counts = cleaned_df['sentiment'].value_counts().to_dict()
                sentiment_prompt = f"Based on the following sentiment counts from media data: {json.dumps(sentiment_counts)}. Provide top 3 concise insights."
                with st.spinner("Generating insights for Sentiment Breakdown..."):
                    sentiment_insights = call_gemini_api(sentiment_prompt)
                st.markdown(f"**Top 3 Insights:**\n{sentiment_insights}")
            st.markdown("---") # Visual separator

            # --- Chart 2: Engagement Trend over time ---
            st.subheader("Engagement Trend Over Time")
            with st.container():
                st.plotly_chart(create_engagement_trend_chart(cleaned_df), use_container_width=True)
                # Prepare data for prompt: start, end date engagements
                engagement_by_date = cleaned_df.groupby(cleaned_df['date'].dt.date)['engagements'].sum().reset_index()
                if not engagement_by_date.empty:
                    first_date = engagement_by_date.iloc[0]['date'].strftime('%Y-%m-%d')
                    last_date = engagement_by_date.iloc[-1]['date'].strftime('%Y-%m-%d')
                    initial_engagements = engagement_by_date.iloc[0]['Total Engagements']
                    final_engagements = engagement_by_date.iloc[-1]['Total Engagements']
                    trend_prompt = (f"Based on engagement data from {first_date} to {last_date}, "
                                    f"with initial engagements of {initial_engagements} and final engagements of {final_engagements}. "
                                    "Provide top 3 concise insights about the engagement trend.")
                else:
                    trend_prompt = "No engagement data available. Provide top 3 general insights about engagement trends in media analysis."

                with st.spinner("Generating insights for Engagement Trend..."):
                    engagement_insights = call_gemini_api(trend_prompt)
                st.markdown(f"**Top 3 Insights:**\n{engagement_insights}")
            st.markdown("---")

            # --- Chart 3: Platform Engagements ---
            st.subheader("Platform Engagements")
            with st.container():
                st.plotly_chart(create_platform_engagements_chart(cleaned_df), use_container_width=True)
                # Get top 5 platforms by engagement for insight generation
                platform_engagements_for_prompt = cleaned_df.groupby('platform')['engagements'].sum().sort_values(ascending=False).head(5).to_dict()
                platform_prompt = f"Based on platform engagements: {json.dumps(platform_engagements_for_prompt)}. Provide top 3 concise insights."
                with st.spinner("Generating insights for Platform Engagements..."):
                    platform_insights = call_gemini_api(platform_prompt)
                st.markdown(f"**Top 3 Insights:**\n{platform_insights}")
            st.markdown("---")

            # --- Chart 4: Media Type Mix ---
            st.subheader("Media Type Mix")
            with st.container():
                st.plotly_chart(create_media_type_mix_chart(cleaned_df), use_container_width=True)
                media_type_counts = cleaned_df['media_type'].value_counts().to_dict()
                media_type_prompt = f"Based on media type counts: {json.dumps(media_type_counts)}. Provide top 3 concise insights."
                with st.spinner("Generating insights for Media Type Mix..."):
                    media_type_insights = call_gemini_api(media_type_prompt)
                st.markdown(f"**Top 3 Insights:**\n{media_type_insights}")
            st.markdown("---")

            # --- Chart 5: Top 5 Locations ---
            st.subheader("Top 5 Locations by Engagements")
            with st.container():
                st.plotly_chart(create_top_locations_chart(cleaned_df), use_container_width=True)
                # Get top 5 locations by engagement for insight generation
                top_locations_for_prompt = cleaned_df.groupby('location')['engagements'].sum().sort_values(ascending=False).head(5).to_dict()
                location_prompt = f"Based on top 5 locations by engagement: {json.dumps(top_locations_for_prompt)}. Provide top 3 concise insights."
                with st.spinner("Generating insights for Top 5 Locations..."):
                    location_insights = call_gemini_api(location_prompt)
                st.markdown(f"**Top 3 Insights:**\n{location_insights}")

        elif cleaned_df is not None and cleaned_df.empty:
            st.warning("The uploaded CSV file is empty or all rows were removed after cleaning due to invalid data.")
        else:
            # Error message already displayed by clean_data if columns are missing
            pass # No additional message needed here.

    except pd.errors.EmptyDataError:
        st.error("The uploaded file is empty. Please upload a CSV with data.")
    except Exception as e:
        st.error(f"An unexpected error occurred while processing the file: {e}")
        st.info("Please ensure your CSV file is correctly formatted and contains the expected columns: 'Date', 'Platform', 'Sentiment', 'Location', 'Engagements', 'Media Type'.")

