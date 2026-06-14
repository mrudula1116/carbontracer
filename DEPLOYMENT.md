# CarbonTracer Deployment Guide

This guide provides instructions on how to deploy the CarbonTracer application to **Streamlit Community Cloud**.

## Prerequisites

1.  A GitHub account.
2.  A Streamlit Community Cloud account (you can sign up at [share.streamlit.io](https://share.streamlit.io) using your GitHub account).
3.  Ensure your code is committed to a public or private GitHub repository.

## Project Structure

Your repository should have the following structure:
```text
carbon-tracer/
├── app.py                 # Main Streamlit application
├── calculations.py        # Core calculation logic
├── recommendations.py     # Emission reduction plan logic
├── requirements.txt       # Python dependencies
└── DEPLOYMENT.md          # This file
```

## Step-by-Step Deployment

1.  **Log in to Streamlit Community Cloud**: Go to [share.streamlit.io](https://share.streamlit.io) and log in.
2.  **Create a New App**: Click on the **"New app"** button in the upper right corner.
3.  **Connect GitHub**: If prompted, authorize Streamlit to access your GitHub repositories.
4.  **Select Repository**:
    *   **Repository**: Choose the repository containing `carbon-tracer`.
    *   **Branch**: Select `main` or the branch you wish to deploy.
    *   **Main file path**: Enter `app.py`.
5.  **Deploy**: Click the **"Deploy!"** button.
6.  **Wait for Build**: Streamlit will read your `requirements.txt`, install dependencies (like `streamlit`, `pandas`, `plotly`), and spin up the container. This usually takes 1-2 minutes.

## Post-Deployment & Maintenance

-   **Updates**: Any push to the selected GitHub branch will automatically trigger a re-deployment. You do not need to manually click deploy again.
-   **Logs**: You can view the app logs in the bottom right corner of the deployed app (click "Manage app") if you encounter any errors.
-   **Data Storage**: Note that since we are using a local CSV file (`footprint_history.csv`) for the Progress Tracker, data will *reset* whenever the app container reboots on Streamlit Cloud. 
    -   *Future Enhancement*: To make progress tracking persistent across reboots and multiple users, integrate a database like **Supabase** or **Firebase** in a future update.

## Troubleshooting

-   **ModuleNotFoundError**: Ensure all packages imported in your Python files are listed in `requirements.txt`.
-   **App "Sleeping"**: Streamlit Community Cloud will put your app to sleep after 7 days of inactivity. You can wake it up by visiting the URL.
