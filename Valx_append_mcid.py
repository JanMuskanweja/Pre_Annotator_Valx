import pandas as pd
import argparse
import csv

def process_mcid_pid_csv(input_file, output_file):
    df1 = pd.read_csv(input_file,skiprows=[0])
    
    df2 = pd.read_csv(output_file)
    pid_mcid_columns = df1.iloc[:, [0, 1]]
    
    df2 = pd.concat([df2, pid_mcid_columns], axis=1)
    df2.to_csv(output_file, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a CSV file and add indices')
    parser.add_argument('-i', default='input.csv', help='Input CSV file')
    parser.add_argument('-o', default='output.csv', help='Output CSV file')

    args = parser.parse_args()
    process_mcid_pid_csv(args.i, args.o)

