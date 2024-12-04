"""
GitHub Repository Analyzer

by Ekaterina Bolotskaya
11/30/2024

This Streamlit app allows users to analyze and visualize data from GitHub repositories.
Users can select a GitHub entity (organization or user) and input their GitHub token for enhanced metrics access.
The app fetches repository details including stars, forks, issues, and traffic metrics such as unique views and clones.
The data is displayed in a table or visualized through interactive plots, allowing users to filter and explore various repository metrics.

Features:
- Choose between user or org repository data from GitHub.
- Fetch and display repository data: stars, forks, open issues, and last updated dates.
- Display traffic data: unique views and clones for each repository (last 14 days).
- Table view with filtering capabilities to analyze repositories based on different metrics.
- Interactive plots view to visualize the distribution of repository metrics.
- User authentication via GitHub token is recommended to access traffic data.

Dependencies:
- Streamlit
- HTTPX (for asynchronous requests)
- Plotly (for interactive visualizations)
- Pandas (for data manipulation)
"""


import streamlit as st
import httpx
from datetime import datetime
import asyncio
import plotly.express as px
import pandas as pd

GITHUB_API_URL = "https://api.github.com"
DEFAULT_ENTITY_TYPE = "org" 
DEFAULT_ENTITY_NAME = "mit-ll" 
DEFAULT_USER_NAME = "EkaterinaBolotskaya" 

# Function to get repository data for an entity
async def get_repositories(entity_type, entity_name, github_token):
    async with httpx.AsyncClient() as client:
        repositories = []
        page = 1

        while True:
            repos_data = await fetch_repositories(client, entity_type, entity_name, page, github_token)
            if not repos_data:
                break

            for repo in repos_data:
                last_updated_date = datetime.fromisoformat(repo["updated_at"][:-1])
                inactivity_days = (datetime.utcnow() - last_updated_date).days

                unique_views, unique_clones = await fetch_traffic_data(client, entity_name, repo["name"], github_token)

                repositories.append(
                    {
                        "name": repo["name"],
                        "description": repo["description"],
                        "url": repo["html_url"],
                        "last_updated": repo["updated_at"],
                        "stars": repo["stargazers_count"],
                        "forks": repo["forks_count"],
                        "open_issues": repo["open_issues_count"],
                        "inactivity_days": inactivity_days,
                        "archived": repo["archived"],
                        "unique_views": unique_views,
                        "unique_clones": unique_clones
                    }
                )

            page += 1

        return repositories

# Function to fetch traffic data (views and clones) for a given repository
async def fetch_traffic_data(client: httpx.AsyncClient, entity_name: str, repo_name: str, token: str):
    traffic_url = f"{GITHUB_API_URL}/repos/{entity_name}/{repo_name}/traffic/views"
    clones_url = f"{GITHUB_API_URL}/repos/{entity_name}/{repo_name}/traffic/clones"

    headers = {"Authorization": f"token {token}"} if token else {}

    traffic_response = await client.get(traffic_url, headers=headers)
    clones_response = await client.get(clones_url, headers=headers)

    unique_views = 0
    unique_clones = 0

    if traffic_response.status_code == 200:
        traffic_data = traffic_response.json()
        unique_views = sum(view['uniques'] for view in traffic_data.get('views', []))

    if clones_response.status_code == 200:
        clones_data = clones_response.json()
        unique_clones = sum(clone['uniques'] for clone in clones_data.get('clones', []))

    return unique_views, unique_clones

# Function to fetch repository data (name, description, stars, etc.) from GitHub API
async def fetch_repositories(client: httpx.AsyncClient, entity_type: str, entity_name: str, page: int, token: str):
    if entity_type == "org" or entity_type == "user":
        url = f"{GITHUB_API_URL}/{entity_type}s/{entity_name}/repos?per_page=100&page={page}"
    else:
        raise ValueError("Invalid entity type. Must be 'org' or 'user'.")

    headers = {"Authorization": f"token {token}"} if token else {}

    response = await client.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch repositories: {response.text}")
    return response.json()
    
# Function to plot a bar distribution of a specified metric
def plot_distribution(data, column_name):
    df = pd.DataFrame(data)

    # Binning
    num_bins = min(max(df[column_name]) - min(df[column_name]) + 1, 15)
    bin_edges = pd.cut(df[column_name], bins=num_bins, retbins=True, right=True)[1]
    df['bins'] = pd.cut(df[column_name], bins=bin_edges, right=True)

    grouped = df.groupby('bins').agg(repos=('name', lambda names: "<br>".join(names))).reset_index()
    counts = df['bins'].value_counts().sort_index()
    bin_labels = [f"{bin_edges[i]:.2f} - {bin_edges[i+1]:.2f}" for i in range(len(bin_edges)-1)]

    # Create a bar chart using the counts and bin labels
    fig = px.bar(
        x=bin_labels,  
        y=counts,  
        labels={'x': column_name.capitalize(), 'y': 'Count'},
        title=f"Distribution of {column_name.capitalize()}"
    )

    # Hover data
    fig.update_traces(
        hovertemplate="Count: %{y}<br><b>Repos:</b><br>%{customdata}",
        customdata=grouped['repos'],  
    )

    st.plotly_chart(fig)

# Main function that runs the Streamlit app
def main():
    st.title("GitHub Repository Analyzer")

    # Entity selection and input fields with default values
    entity_type_label = st.selectbox("Select Entity Type", ["Organization", "User"], index=0 if DEFAULT_ENTITY_TYPE == "org" else 1)
    if entity_type_label == "Organization":
        entity_type = "org"
        entity_name = st.text_input("Enter the Organization Name", value=DEFAULT_ENTITY_NAME)
    else:
        entity_type = "user"
        entity_name = st.text_input("Enter the User Name", value=DEFAULT_USER_NAME)

    github_token = st.text_input("Enter your GitHub Token (Optional but Recommended)", value="", type="password")
    st.write("Providing a GitHub token will allow tracking user engagement metrics for your repositories.")
    
    if not entity_name:
        st.warning(f"Please enter a valid {entity_type_label.lower()} name.")
        return

    # Get repo data
    if "repositories" not in st.session_state or st.session_state.entity_name != entity_name:
        repositories = asyncio.run(get_repositories(entity_type, entity_name, github_token))
        st.session_state.repositories = repositories
        st.session_state.entity_name = entity_name
    else:
        repositories = st.session_state.repositories

    # App tabs
    tabs = st.selectbox("Choose a tab", ["Repository Data", "Interactive Plots"])

    if tabs == "Repository Data":

        df = pd.DataFrame(repositories)
        df = df[["name", "url", "last_updated", "stars", "forks", "open_issues", "inactivity_days", "unique_views", "unique_clones", "description"]]
        df.columns = ["Name", "URL", "Last Updated", "Stars", "Forks", "Open Issues", "Inactivity Days", "Unique Views", "Unique Clones", "Description"]
        st.dataframe(df)

    elif tabs == "Interactive Plots":
        
        st.write("---")
        
        # Select a metric for filtering and choose limits
        filter_metric = st.selectbox("Select Metric to Filter By", ["Stars", "Inactivity Days", "Forks", "Open Issues", "Unique Views", "Unique Clones"])
        filter_metric_snake = filter_metric.lower().replace(" ", "_")

        min_value = min(repositories, key=lambda x: x[filter_metric_snake])[filter_metric_snake]
        max_value = max(repositories, key=lambda x: x[filter_metric_snake])[filter_metric_snake]
        
        slider_min = st.slider(f"Select {filter_metric} Range", min_value, max_value, (min_value, max_value))

        st.write("---")

        # Select a metric to plot
        plot_metric = st.selectbox("Select Metric to Plot", ["Stars", "Inactivity Days", "Forks", "Open Issues", "Unique Views", "Unique Clones"])

        st.write("---")

        filtered_data = [repo for repo in repositories if slider_min[0] <= repo[filter_metric.lower().replace(" ", "_")] <= slider_min[1]]

        # Plot the selected metric for the filtered data
        plot_distribution(filtered_data, plot_metric.lower().replace(" ", "_"))


if __name__ == "__main__":
    main()
