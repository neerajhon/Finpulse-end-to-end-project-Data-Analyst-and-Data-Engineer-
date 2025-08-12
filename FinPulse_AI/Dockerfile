FROM apache/airflow:2.8.1

# Switch to airflow user before installing Python packages
USER airflow

# Install required Python packages
RUN pip install --no-cache-dir joblib scikit-learn pandas numpy
