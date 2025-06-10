# Strava_EDA
Exploratory Data Analysis using my data pulled from my Strava Account.

## 📊 View the Live Report

[![Open Power BI Report](https://img.shields.io/badge/View%20Report-PowerBI-blue)]([https://app.powerbi.com/view?r=eyJrIjoiYjczNzAyNGQtM2NlNi00N2U2LTg4NDEtY2VmYTIyMDBjNzg3IiwidCI6IjNjM2VkNTUxLWFiYmUtNGExNS1hMDlhLTkzOTZiOGE3Njg5YSIsImMiOjJ9)]

---

GitHub: [WilliamHeidel/Strava_EDA](https://github.com/WilliamHeidel/Strava_EDA)

## Overview

Implemented a fully automated analytics pipeline to extract, warehouse, and visualize personal Strava activity data.

## Data Ingestion & Automation

- Built a **dlt**-based extractor to handle Strava OAuth and incremental REST API pulls.
- Configured **GitHub Actions** to run the extraction daily, loading raw JSON data into an **S3** bucket and then into **Amazon Redshift**.

## Data Modeling & Warehousing

- Developed a **dbt** project on Redshift to clean, normalize, and document source tables.
- Created incremental models, defined schema tests, and maintained lineage for reliable, auditable analytics.

## Analysis & Reporting

- Defined custom **DAX** measures (e.g., distance-weighted average heart rate) to drive insights.
- Built an interactive **Power BI** dashboard with drill-throughs and bookmarks.
- Published the report publicly via **GitHub Pages** for easy sharing.

## Technologies & Tools

Python, dlt, GitHub Actions, AWS S3, Amazon Redshift, dbt, Power BI, HTML/CSS (GitHub Pages)
