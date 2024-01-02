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
try:
    import psycopg2
except ImportError:
    # If psycopg2 is not installed, install psycopg2-binary
    import subprocess
    subprocess.run(['pip', 'install', 'psycopg2-binary'])

import argparse
import os
import csv
import pandas as pd
from Valx_CTgov import extract_variables
from Valx_append_indices import process_csv
from Valx_json import convert_csv_to_json
from Valx_append_mcid import process_mcid_pid_csv

def manipulate_data(input_csv_path, output_csv_path):
    # Read the original CSV file
    df = pd.read_csv(input_csv_path)

    # Manipulate the "criterion" column and create a new column "manipulated_text"
    df['manipulated_text'] = 'Inclusion Criteria:# - ' + df['criterion_text']

    # Select only the "nctid" and "manipulated_text" columns
    result_df = df[['nctid', 'manipulated_text']]
    output = result_df.values.tolist()
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(output)
def main():
    parser = argparse.ArgumentParser(description='Extract and structure numeric lab test comparison statements from text using Valx_CTgov')
    parser.add_argument('-f1', default='data/rules.csv', help='Domain knowledge feature list CSV file')
    parser.add_argument('-f2', default='data/variable_features_umls.csv', help='UMLS feature list CSV file')
    parser.add_argument('-v', default='All', help='Variable name: All, HBA1C, BMI, Glucose, Creatinine, BP-Systolic, BP-Diastolic')

    args = parser.parse_args()
    try:
       connection = psycopg2.connect(
          host='localhost',
          port='5432',
          database='doccano_db',
          user='doccano_user',
          password='abc357'
       )
    except psycopg2.Error as e:
       print("Error connecting to the database:", e)

    pid = int(input("Enter the pid value:"))
    sql_query = """
    SELECT pc.pid, pc.mcid, cr.nctid, cr.criterion
    FROM miimansa.criteria_inventory cr
    INNER JOIN miimansa.project_criteria pc ON pc.mcid = cr.mcid
    WHERE pc.pid = %s;
    """
    df = pd.read_sql_query(sql_query, connection, params=(pid,))
    
    input_csv_path = os.path.join('data', f'{pid}.csv')
    df.to_csv(input_csv_path, index= False)
    print(f"Data for pid {pid} exported to '{input_csv_path}'")
    manipulated_data_file_name = 'data/valx_input.csv'

    # Manipulate the data first
    manipulate_data(input_csv_path, manipulated_data_file_name)
    print(f"Manipulated data saved as data/valx_input.csv")

    extract_variables(manipulated_data_file_name, args.f1, args.f2, args.v)
    process_csv('data/valx_input_exp_All.csv', 'data/valx_appended_csv_output.csv')
    process_mcid_pid_csv(input_csv_path, 'data/valx_appended_csv_output.csv')
    output_json_file = f'data/{pid}_json.json'
    convert_csv_to_json('data/valx_appended_csv_output.csv', output_json_file)
    

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
