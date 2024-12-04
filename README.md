# GitHub_repo_analyzer

This is a Streamlit-based web application designed to analyze and visualize data from GitHub repositories. Users can input a GitHub organization or user, and fetch repository information, including stars, forks, open issues, and traffic data such as unique views and clones.

### Features:
- Choose between user or org repository data from GitHub.
- Fetch and display repository data: stars, forks, open issues, and last updated dates.
- Display traffic data: unique views and clones for each repository (last 14 days).
- Table view with filtering capabilities to analyze repositories based on different metrics.
- Interactive plots view to visualize the distribution of repository metrics.
- User authentication via GitHub token is recommended to access traffic data.

### Dependencies:
- **Streamlit**: For creating the interactive web interface.
- **HTTPX**: For asynchronous HTTP requests to the GitHub API.
- **Plotly**: For creating interactive visualizations.
- **Pandas**: For data manipulation and processing.

### Setup Instructions:

1. Clone this repository to your local machine:
    ```bash
    git clone https://github.com/brown-ccv-jobs/brown-ccv-fall-2024-technical-assignment-a-EkaterinaBolotskaya.git
    cd software_engineering
    ```

2. Install required dependencies:
    ```bash
    pip install streamlit httpx plotly pandas
    ```

3. Run the application:
    ```bash
    streamlit run repo_analyzer.py
    ```

5. Open the provided URL in your browser (`http://localhost:8501`) to access the app.

### Usage:

Upon starting the application, users will be prompted to select between an **Organization** or **User** and provide the corresponding name. Currently befaulted to **mit-ll** (MIT Lincoln Laboratory) and **EkaterinaBolotskaya**. You can optionally enter your GitHub token. Providing a GitHub token allows you to access additional metrics and data from private repositories, as well as higher rate limits for API requests. If no token is provided, public data will be fetched. 

!!! Large (~more than 100 repos) amounts of data will take some time to load, please be patient.

The app is divided into the following sections:

1. **Repository Data**: Displays a table with detailed information about each repository such as stars, forks, open issues, inactivity days, etc., where users can filter repositories based on specific metrics.
2. **Interactive Plots**: Displays interactive visualizations of repository metrics (such as stars, forks, views, and clones) in a bar chart with the ability to filter by specific metrics (e.g., inactivity days or stars).

### Data Fetching and Storage:

Once the data is fetched from the GitHub API, it is stored in a local cache to prevent unnecessary repeated requests. This caching mechanism allows the application to efficiently handle the large number of repositories, and it ensures that data is available for quick manipulation and filtering.

### Repo contents:

- **Source Code**: repo_analyzer.py.
- **README.md**: This file.

---

**Note on GitHub tokens**: 

Providing a GitHub token allows you to access additional metrics and data from private repositories, as well as higher rate limits for API requests. Unauthorized users are limited to 60 requests per hour, while authenticated users with a GitHub token can make up to 5,000 requests per hour. To use the token:

1. Go to [GitHub Personal Access Tokens](https://github.com/settings/tokens).
2. Generate a new classic token with the appropriate scopes (you can use the default scopes for this app).
3. Enter the token in the provided input field within the app.

