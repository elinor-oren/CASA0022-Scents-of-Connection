import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV files
directory = '/Users/elinor/Documents/GitHub/CASA0022-dissertation/data'
df1 = pd.read_csv(os.path.join(directory,'data_participant_1_headset_1_20240627.csv'))
df2 = pd.read_csv(os.path.join(directory, 'data_participant_2_headset_2_20240627.csv'))

# Check the number of data points (rows) in each dataset
data_length_df1 = len(df1)
data_length_df2 = len(df2)

# Print the number of data points
print(f"Number of data points in Headset 1: {data_length_df1}")
print(f"Number of data points in Headset 2: {data_length_df2}")

# Exclude certain columns for analysis
exclude_columns = ['timestamp', 'signal_strength', 'attention', 'meditation']
columns_to_analyze = [col for col in df1.columns if col not in exclude_columns]

# Calculate standard deviation for each dataset
std_df1 = df1[columns_to_analyze].std()
std_df2 = df2[columns_to_analyze].std()

# Find most and least variable columns for each dataset
most_variable_column_df1 = std_df1.idxmax()
least_variable_column_df1 = std_df1.idxmin()
most_variable_column_df2 = std_df2.idxmax()
least_variable_column_df2 = std_df2.idxmin()

# Calculate correlations between the same columns across the two datasets
correlations = {col: df1[col].corr(df2[col]) for col in columns_to_analyze}
most_correlated = max(correlations, key=correlations.get)
least_correlated = min(correlations, key=correlations.get)

# Output the results
variability_results = {
    "Headset 1 Most Variable": (most_variable_column_df1, std_df1[most_variable_column_df1]),
    "Headset 1 Least Variable": (least_variable_column_df1, std_df1[least_variable_column_df1]),
    "Headset 2 Most Variable": (most_variable_column_df2, std_df2[most_variable_column_df2]),
    "Headset 2 Least Variable": (least_variable_column_df2, std_df2[least_variable_column_df2]),
    "Most Correlated Columns": (most_correlated, correlations[most_correlated]),
    "Least Correlated Columns": (least_correlated, correlations[least_correlated])
}

# Plotting the data over time for the selected columns
fig, axes = plt.subplots(nrows=len(columns_to_analyze), ncols=1, figsize=(10, 20), sharex=True)
for i, col in enumerate(columns_to_analyze):
    axes[i].plot(df1['timestamp'], df1[col], label=f'Headset 1 {col}')
    axes[i].plot(df2['timestamp'], df2[col], label=f'Headset 2 {col}')
    axes[i].set_title(f'Change Over Time - {col}')
    axes[i].set_ylabel(col)
    axes[i].legend()

plt.xlabel('Time')
plt.tight_layout()
plt.show()

variability_results
