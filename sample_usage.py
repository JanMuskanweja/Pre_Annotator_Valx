try:
    import pandas as pd
except ImportError:
    print("Pandas not found. Installing...")
    try:
        import subprocess
        subprocess.check_call(['pip', 'install', 'pandas'])
        import pandas as pd
        print("Pandas has been successfully installed.")
    except Exception as e:
        print("An error occurred while installing Pandas:", e)

import argparse
import pandas as pd
from Valx_CTgov import extract_variables

def main():
    parser = argparse.ArgumentParser(description='Extract and structure numeric lab test comparison statements from text using Valx_CTgov')
    parser.add_argument('-i', default='data/diabetes.csv', help='Input CSV file')
    parser.add_argument('-f1', default='data/rules.csv', help='Domain knowledge feature list CSV file')
    parser.add_argument('-f2', default='data/variable_features_umls.csv', help='UMLS feature list CSV file')
    parser.add_argument('-v', default='All', help='Variable name: All, HBA1C, BMI, Glucose, Creatinine, BP-Systolic, BP-Diastolic')

    args = parser.parse_args()
    extract_variables(args.i, args.f1, args.f2, args.v)

    csv_file_path = 'data/diabetes_exp_All.csv'

    # Load csv_file_path into a pandas dataframe
    df = pd.read_csv(csv_file_path)

    # Check the columns of the DataFrame
    old_columns = df.columns

    # Rename the columns
    df.columns = ['nct_id', 'inclusion_exclusion', 'col3', 'col4', "col5"]

    # Insert old_columns as the first row of df
    df = pd.concat([pd.DataFrame([old_columns], columns=df.columns), df], ignore_index=True)

    # Extract the first 2 rows of the dataframe
    df_head = df.head(5)
    print("first_row:\n", df_head)

    # Iterate over rows
    for i in range(min(2, df.shape[0])):
        print("row ", i, ": ", df.iloc[i, 4])

    # Create a new dataframe containing only the 0th and 4th columns of df
    df_subset = df.iloc[:, [0, 4]]
    print("df_subset:\n", df_subset)

    # Save this dataframe as a new CSV file
    df_subset.to_csv('data/diabetes_exp_All_subset.csv', index=False)


if __name__ == '__main__':
    main()
