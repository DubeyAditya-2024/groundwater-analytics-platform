import pandas as pd
import numpy as np
import os  # Added import for file path checking
from sklearn.preprocessing import OneHotEncoder
import joblib


def load_and_engineer_data(csv_path="raw_data.csv"):
    try:
        # Load Data (Using simulated data as default)
        dates = pd.date_range(start='2020-01-01', periods=1000, freq='D')
        df = pd.DataFrame({
            'Date': dates,
            'Water_Level': np.random.rand(1000) * 20 + 50,
            'Rainfall_mm': np.random.rand(1000) * 10,
            'PET_mm': np.random.rand(1000) * 5,
            'Avg_Temp_C': np.random.rand(1000) * 15 + 20,
            'Lat': np.random.choice([10.0, 10.1, 10.2], 1000),
            'Lon': np.random.choice([78.0, 78.1, 78.2], 1000),
            'Elevation': np.random.choice([200, 250, 300], 1000),
            'Soil_Type': np.random.choice(['Clay', 'Sand', 'Loam'], 1000),
            'LULC': np.random.choice(['Agri', 'Urban', 'Forest'], 1000)
        })

    except Exception as e:
        print(f"FATAL ERROR during simulated data creation: {e}")
        return None

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').set_index('Date')

    # Feature Engineering
    df['Prev_Level'] = df['Water_Level'].shift(1)
    df['Rainfall_7day'] = df['Rainfall_mm'].rolling(window=7).sum()
    df['Rainfall_30days'] = df['Rainfall_mm'].rolling(window=30).sum()
    df['PET_30days'] = df['PET_mm'].rolling(window=30).sum()
    df['Target_Recharge'] = df['Water_Level'].diff(-30).fillna(0)

    # Categorical Encoding
    encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    encoded_features = encoder.fit_transform(df[['Soil_Type', 'LULC']])
    encoded_df = pd.DataFrame(encoded_features, index=df.index,
                              columns=encoder.get_feature_names_out(['Soil_Type', 'LULC']))
    df = pd.concat([df, encoded_df], axis=1).dropna()

    # Save the prepared data and encoder
    df.to_csv('prepared_data.csv')
    joblib.dump(encoder, 'ohe_encoder.pkl')

    print("-------------------------------------------------------")
    print(f"✅ Data pipeline finished.")
    print(f"File created and saved at: {os.path.abspath('prepared_data.csv')}")
    print("-------------------------------------------------------")
    return df


if __name__ == '__main__':
    load_and_engineer_data()