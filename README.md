# 🍺 Brewery Data Pipeline with Apache Airflow

This project implements a complete **ETL pipeline** using **Apache Airflow** orchestrated via **Docker**. It extracts brewery data from a public API, processes and validates the data, stores it in a structured format (Parquet), and organizes the flow into **Bronze**, **Silver**, and **Gold** layers following the **Medallion Architecture**.

---

## 📂 Project Structure

```
.
├── dags/                      # Airflow DAGs
│   └── brewery_etl_dag.py     # Main DAG orchestrating the pipeline
├── etl/                       # Python functions for each ETL step
│   ├── extract.py             # Extract breweries from API
│   ├── transform.py           # Clean, normalize, and partition data
├── tests/                     # Unit tests for validation
│   ├── test_extract.py
│   └── test_transform.py
├── data_lake/                 # Persisted data lake
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── requirements.txt           # Python dependencies
├── docker-compose.yaml        # Docker stack definition
├── start.sh                   # Startup script for Linux/macOS
├── start.bat                  # Startup script for Windows
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/FlavioBaldissera/brewery-pipeline
cd brewery-pipeline
```

---

### 2. Run the pipeline

#### 🪟 For Windows

```cmd
start.bat
```

#### 🐧 For Linux/macOS

```bash
chmod +x start.sh   # only the first time
./start.sh
```

These scripts will:

- Build Docker images  
- Initialize the Airflow metadata DB and admin user  
- Start all required Airflow services  
- Wait for Airflow to become ready  
- Automatically **unpause** and **trigger** the DAG `brewery_etl`

Once running, access the Airflow UI at:  
👉 **http://localhost:8080**

---

## 👤 Admin Login

The default admin user created is:

- **Username:** `admin`  
- **Password:** `admin`  

You can customize credentials by editing environment variables in the `.env` file or the scripts.

---

## 📅 Running the DAG manually (optional)

If needed (e.g., for re-runs), you can trigger the DAG again from:

### The Airflow UI
1. Visit `http://localhost:8080`
2. Locate the `brewery_etl` DAG
3. Click ▶️ **Trigger DAG**

### Or from the CLI

```bash
docker-compose exec airflow-webserver airflow dags trigger brewery_etl
```

This will execute:

- `extract_breweries` → stores raw JSON in **Bronze**
- `transform_breweries` → cleans and partitions to Parquet by `state` in **Silver**
- `transform_breweries_gold` → aggregates and stores summary as Parquet in **Gold**

---


## 🧊 Data Lake Design

The ETL flow writes files to `data_lake/`, structured by layer:

```
data_lake/
├── bronze/
│   └── breweries_YYYYMMDD.json
├── silver/
│   └── breweries_YYYYMMDD.parquet/
│       ├── state=Texas/breweries.parquet
│       ├── state=Oklahoma/breweries.parquet
│       └── ...
└── gold/
    └── breweries_summary_YYYYMMDD.parquet
```

Partitioning by `state` is done to optimize analytical queries and performance.

---

## 🔔 Monitoring & Alerting

Suggested monitoring strategies:

- **Airflow UI:** Tracks retries, failures, execution duration
- **Email alerts:** Can be configured with Airflow's SMTP settings
- **Logging:** All tasks are logged for observability
- **Unit tests:** Prevent writing invalid/incomplete data
- **Future tools:** Integrate with tools like:
    - **Great Expectations** (data quality validation)
    - **Prometheus + Grafana** (metrics/alerts)
    - **Sentry** or **DataDog** (exception monitoring)

---

## 🧼 Cleaning Up

To stop and remove containers, networks, and volumes:

```bash
docker-compose down -v
```

To rebuild everything from scratch (use with caution):

```bash
docker-compose down --volumes
docker-compose up --build -d
```

---

## ✅ Requirements

- Docker & Docker Compose
- Internet access (to call external API)
- Python 3.10 (inside containers)

---

## 📍 Notes

- All DAG logic is orchestrated using `brewery_etl_dag.py`
- External scripts are organized under the `etl/` folder
- DAGs and helper functions are imported dynamically using Python’s module system
- Volumes are mapped so local files are persisted and visible under `data_lake/`

---