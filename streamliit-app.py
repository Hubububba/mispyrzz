# app.py - Interactive Media Intelligence Dashboard

import pandas as pd
import plotly.express as px
from flask import Flask, request, render_template_string
import io

app = Flask(__name__)

# HTML Template for the web application
# This template includes the upload form and placeholders for charts and insights.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Media Intelligence Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f3f4f6; /* Light gray background */
        }
        .container {
            max-width: 1200px;
            margin: auto;
            padding: 2rem;
        }
        .card {
            background-color: #ffffff;
            border-radius: 1rem; /* Rounded corners */
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            margin-bottom: 2rem;
        }
        .plotly-chart {
            width: 100%;
            height: 500px; /* Standard height for charts */
            margin-bottom: 1.5rem;
        }
        .insights ul {
            list-style-type: disc;
            margin-left: 1.5rem;
            color: #4b5563; /* Gray text for insights */
        }
        .insights li {
            margin-bottom: 0.5rem;
        }
    </style>
</head>
<body class="bg-gray-100 text-gray-800">
    <div class="container mx-auto p-8">
        <h1 class="text-4xl font-bold text-center text-blue-700 mb-8 rounded-lg p-4 bg-white shadow-md">
            Interactive Media Intelligence Dashboard
        </h1>

        <div class="card">
            <h2 class="text-2xl font-semibold text-gray-700 mb-4">1. Upload Your CSV File</h2>
            <p class="text-gray-600 mb-4">Please upload a CSV file with the following columns: <code class="font-mono bg-gray-200 px-2 py-1 rounded-md">Date</code>, <code class="font-mono bg-gray-200 px-2 py-1 rounded-md">Platform</code>, <code class="font-mono bg-gray-200 px-2 py-1 rounded-md">Sentiment</code>, <code class="font-mono bg-gray-200 px-2 py-1 rounded-md">Location</code>, <code class="font-mono bg-gray-200 px-2 py-1 rounded-md">Engagements</code>, <code class="font-mono bg-gray-200 px-2 py-1 rounded-md">Media Type</code>.</p>
            <form action="/analyze" method="post" enctype="multipart/form-data" class="flex flex-col items-center">
                <label for="csvFile" class="sr-only">Upload CSV</label>
                <input type="file" name="csvFile" id="csvFile" accept=".csv" required
                       class="block w-full text-sm text-gray-500
                              file:mr-4 file:py-2 file:px-4
                              file:rounded-full file:border-0
                              file:text-sm file:font-semibold
                              file:bg-blue-50 file:text-blue-700
                              hover:file:bg-blue-100 cursor-pointer mb-6">
                <button type="submit"
                        class="px-6 py-3 bg-blue-600 text-white font-semibold rounded-full
                               hover:bg-blue-700 focus:outline-none focus:ring-2
                               focus:ring-blue-500 focus:ring-opacity-75 transition duration-300 ease-in-out shadow-lg">
                    Analyze Data
                </button>
            </form>
        </div>

        {% if chart_htmls %}
        <div class="card">
            <h2 class="text-2xl font-semibold text-gray-700 mb-4">2. Data Cleaning & Visualization</h2>
            <p class="text-gray-600 mb-6">Your data has been cleaned (Date to datetime, missing Engagements to 0, and column names normalized) and visualized below.</p>

            <h3 class="text-xl font-semibold text-gray-700 mb-4">Sentiment Breakdown</h3>
            <div class="plotly-chart">
                {{ chart_htmls['sentiment'] | safe }}
            </div>
            <div class="insights card p-4 mb-6">
                <h4 class="text-lg font-semibold text-gray-700 mb-2">Key Insights:</h4>
                <ul class="insights">
                    {% for insight in insights['sentiment'] %}
                        <li>{{ insight }}</li>
                    {% endfor %}
                </ul>
            </div>

            <h3 class="text-xl font-semibold text-gray-700 mb-4">Engagement Trend over Time</h3>
            <div class="plotly-chart">
                {{ chart_htmls['engagement_time'] | safe }}
            </div>
            <div class="insights card p-4 mb-6">
                <h4 class="text-lg font-semibold text-gray-700 mb-2">Key Insights:</h4>
                <ul class="insights">
                    {% for insight in insights['engagement_time'] %}
                        <li>{{ insight }}</li>
                    {% endfor %}
                </ul>
            </div>

            <h3 class="text-xl font-semibold text-gray-700 mb-4">Platform Engagements</h3>
            <div class="plotly-chart">
                {{ chart_htmls['platform'] | safe }}
            </div>
            <div class="insights card p-4 mb-6">
                <h4 class="text-lg font-semibold text-gray-700 mb-2">Key Insights:</h4>
                <ul class="insights">
                    {% for insight in insights['platform'] %}
                        <li>{{ insight }}</li>
                    {% endfor %}
                </ul>
            </div>

            <h3 class="text-xl font-semibold text-gray-700 mb-4">Media Type Mix</h3>
            <div class="plotly-chart">
                {{ chart_htmls['media_type'] | safe }}
            </div>
            <div class="insights card p-4 mb-6">
                <h4 class="text-lg font-semibold text-gray-700 mb-2">Key Insights:</h4>
                <ul class="insights">
                    {% for insight in insights['media_type'] %}
                        <li>{{ insight }}</li>
                    {% endfor %}
                </ul>
            </div>

            <h3 class="text-xl font-semibold text-gray-700 mb-4">Top 5 Locations</h3>
            <div class="plotly-chart">
                {{ chart_htmls['location'] | safe }}
            </div>
            <div class="insights card p-4 mb-6">
                <h4 class="text-lg font-semibold text-gray-700 mb-2">Key Insights:</h4>
                <ul class="insights">
                    {% for insight in insights['location'] %}
                        <li>{{ insight }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
        {% elif error %}
        <div class="card bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <strong class="font-bold">Error!</strong>
            <span class="block sm:inline">{{ error }}</span>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """
    Renders the main page with the CSV upload form.
    """
    return render_template_string(HTML_TEMPLATE, chart_htmls=None, error=None)

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Handles CSV file upload, data cleaning, chart generation, and displays results.
    """
    if 'csvFile' not in request.files:
        return render_template_string(HTML_TEMPLATE, error="No file part in the request.")
    file = request.files['csvFile']
    if file.filename == '':
        return render_template_string(HTML_TEMPLATE, error="No selected file.")
    if file:
        try:
            # Read CSV into DataFrame
            df = pd.read_csv(io.StringIO(file.read().decode('utf-8')))

            # 2. Clean the data
            # Normalize column names
            df.columns = df.columns.str.lower().str.replace(' ', '_')

            # Convert 'date' to datetime
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            else:
                return render_template_string(HTML_TEMPLATE, error="Column 'Date' not found in CSV. Please ensure correct column names.")

            # Fill missing 'engagements' with 0
            if 'engagements' in df.columns:
                df['engagements'] = df['engagements'].fillna(0)
            else:
                return render_template_string(HTML_TEMPLATE, error="Column 'Engagements' not found in CSV. Please ensure correct column names.")

            # Check for other required columns
            required_columns = ['platform', 'sentiment', 'location', 'media_type']
            for col in required_columns:
                if col not in df.columns:
                    return render_template_string(HTML_TEMPLATE, error=f"Required column '{col.replace('_', ' ').title()}' not found in CSV. Please ensure correct column names.")

            chart_htmls = {}
            insights = {}

            # 3. Build 5 interactive charts using Plotly
            # 3.1. Pie chart: Sentiment Breakdown
            sentiment_counts = df['sentiment'].value_counts().reset_index()
            sentiment_counts.columns = ['Sentiment', 'Count']
            fig_sentiment = px.pie(
                sentiment_counts,
                values='Count',
                names='Sentiment',
                title='<span style="font-size: 1.5em; font-weight: bold;">Sentiment Breakdown</span>',
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            chart_htmls['sentiment'] = fig_sentiment.to_html(full_html=False, include_plotlyjs='cdn')
            # 4. Insights for Sentiment Breakdown
            total_sentiment = sentiment_counts['Count'].sum()
            positive_sentiment = sentiment_counts[sentiment_counts['Sentiment'] == 'Positive']['Count'].sum() if 'Positive' in sentiment_counts['Sentiment'].values else 0
            negative_sentiment = sentiment_counts[sentiment_counts['Sentiment'] == 'Negative']['Count'].sum() if 'Negative' in sentiment_counts['Sentiment'].values else 0
            neutral_sentiment = sentiment_counts[sentiment_counts['Sentiment'] == 'Neutral']['Count'].sum() if 'Neutral' in sentiment_counts['Sentiment'].values else 0

            max_sentiment = sentiment_counts.loc[sentiment_counts['Count'].idxmax()]
            min_sentiment = sentiment_counts.loc[sentiment_counts['Count'].idxmin()]

            insights['sentiment'] = [
                f"Majority sentiment towards the brand/campaign is **{max_sentiment['Sentiment']}** ({max_sentiment['Count']} instances), indicating overall public perception.",
                f"**{min_sentiment['Sentiment']}** sentiment is the smallest portion ({min_sentiment['Count']} instances), which might warrant further investigation to understand its reasons.",
                f"The ratio of positive to negative sentiment is {positive_sentiment}:{negative_sentiment}, providing insight into the effectiveness of current communication campaigns."
            ]

            # 3.2. Line chart: Engagement Trend over time
            engagement_over_time = df.groupby('date')['engagements'].sum().reset_index()
            fig_engagement_time = px.line(
                engagement_over_time,
                x='date',
                y='engagements',
                title='<span style="font-size: 1.5em; font-weight: bold;">Engagement Trend over Time</span>',
                labels={'date': 'Date', 'engagements': 'Total Engagements'}
            )
            fig_engagement_time.update_xaxes(rangeslider_visible=True)
            chart_htmls['engagement_time'] = fig_engagement_time.to_html(full_html=False, include_plotlyjs='cdn')
            # 4. Insights for Engagement Trend over time
            peak_engagement_date = engagement_over_time.loc[engagement_over_time['engagements'].idxmax()]
            lowest_engagement_date = engagement_over_time.loc[engagement_over_time['engagements'].idxmin()]

            insights['engagement_time'] = [
                f"There was a significant engagement spike on **{peak_engagement_date['date'].strftime('%Y-%m-%d')}** with {int(peak_engagement_date['engagements'])} engagements, likely related to a specific event or campaign.",
                f"The period around **{lowest_engagement_date['date'].strftime('%Y-%m-%d')}** shows stable low engagement, indicating a need for new content strategies or a review of inactive periods.",
                "Recurring daily/weekly engagement patterns might be visible, which can be leveraged for optimal posting schedules."
            ]


            # 3.3. Bar chart: Platform Engagements
            platform_engagements = df.groupby('platform')['engagements'].sum().reset_index()
            platform_engagements = platform_engagements.sort_values(by='engagements', ascending=False)
            fig_platform = px.bar(
                platform_engagements,
                x='platform',
                y='engagements',
                title='<span style="font-size: 1.5em; font-weight: bold;">Platform Engagements</span>',
                labels={'platform': 'Platform', 'engagements': 'Total Engagements'},
                color='platform',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            chart_htmls['platform'] = fig_platform.to_html(full_html=False, include_plotlyjs='cdn')
            # 4. Insights for Platform Engagements
            most_effective_platform = platform_engagements.iloc[0]
            least_effective_platform = platform_engagements.iloc[-1]
            insights['platform'] = [
                f"**{most_effective_platform['platform']}** is the most dominant platform in generating engagements ({int(most_effective_platform['engagements'])}), indicating a suitable marketing focus.",
                f"**{least_effective_platform['platform']}** has low engagement ({int(least_effective_platform['engagements'])}); the content strategy or resource allocation there might need re-evaluation.",
                "Some platforms show untapped engagement growth potential."
            ]

            # 3.4. Pie chart: Media Type Mix
            media_type_counts = df['media_type'].value_counts().reset_index()
            media_type_counts.columns = ['Media Type', 'Count']
            fig_media_type = px.pie(
                media_type_counts,
                values='Count',
                names='Media Type',
                title='<span style="font-size: 1.5em; font-weight: bold;">Media Type Mix</span>',
                color_discrete_sequence=px.colors.sequential.Agsunset
            )
            chart_htmls['media_type'] = fig_media_type.to_html(full_html=False, include_plotlyjs='cdn')
            # 4. Insights for Media Type Mix
            most_popular_media_type = media_type_counts.loc[media_type_counts['Count'].idxmax()]
            least_popular_media_type = media_type_counts.loc[media_type_counts['Count'].idxmin()]
            insights['media_type'] = [
                f"**{most_popular_media_type['Media Type']}** content is the most frequently used format ({most_popular_media_type['Count']} instances), likely reflecting audience preference or current content strategy.",
                f"There's an opportunity to experiment with **{least_popular_media_type['Media Type']}** media types, which are currently underutilized.",
                "The balance across various media types can be improved to reach a wider and more diverse audience."
            ]

            # 3.5. Bar chart: Top 5 Locations
            location_engagements = df.groupby('location')['engagements'].sum().nlargest(5).reset_index()
            location_engagements = location_engagements.sort_values(by='engagements', ascending=False)
            fig_location = px.bar(
                location_engagements,
                x='location',
                y='engagements',
                title='<span style="font-size: 1.5em; font-weight: bold;">Top 5 Locations with Highest Engagement</span>',
                labels={'location': 'Location', 'engagements': 'Total Engagements'},
                color='location',
                color_discrete_sequence=px.colors.qualitative.Vivid
            )
            chart_htmls['location'] = fig_location.to_html(full_html=False, include_plotlyjs='cdn')
            # 4. Insights for Top 5 Locations
            top_location = location_engagements.iloc[0] if not location_engagements.empty else None
            second_location = location_engagements.iloc[1] if len(location_engagements) > 1 else None
            insights['location'] = []
            if top_location is not None:
                insights['location'].append(f"**{top_location['location']}** is the geographic area with the highest engagement ({int(top_location['engagements'])}), indicating a strong audience concentration or content relevance there.")
                if second_location is not None:
                    insights['location'].append(f"Targeted geographic marketing can be further focused on areas like **{top_location['location']}** and **{second_location['location']}** for local campaigns or community events.")
                else:
                    insights['location'].append(f"Targeted geographic marketing can be further focused on **{top_location['location']}** for local campaigns or community events.")
                insights['location'].append("Understanding the audience characteristics in these locations can help tailor future messages and content.")
            else:
                insights['location'] = ["No location data available for insights."]

            return render_template_string(HTML_TEMPLATE, chart_htmls=chart_htmls, insights=insights, error=None)

        except Exception as e:
            return render_template_string(HTML_TEMPLATE, error=f"An error occurred: {e}")

if __name__ == '__main__':
    # You can run this Flask app using `python app.py` in your terminal.
    # It will typically run on http://127.0.0.1:5000/
    app.run(debug=True)
