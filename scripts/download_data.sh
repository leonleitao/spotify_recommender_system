
kaggle datasets download -d yamaerenay/spotify-dataset-19212020-160k-tracks --unzip  -p data
chmod +x scripts/preprocess_data.py
export PYTHONPATH=.
python scripts/preprocess_data.py
rm data/data_by*.csv
rm data/data_w_genres.csv