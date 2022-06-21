# My Master Project
This repo collects all my `Python` scripts that I use to:
1. Scrape the target texts and pictures the website into dataset
2. Extract and enrich new features from the dataset, such as gender from fullname, new picture attributes from `Google Cloud Vision` and `AWS Rekognition`
3. Ingest the data to my local `MSSQL` database.

# Prerequisite 
MSSQL database is installed, and the schema is already created.

# How to run
Simple install the python dependency and then run the script.
```
# Install dependency
pip install requirements.txt

# Run the script
python src/main.py
```
