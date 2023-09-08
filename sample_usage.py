import argparse
from Valx_CTgov import extract_variables

def main():
    parser = argparse.ArgumentParser(description='Extract and structure numeric lab test comparison statements from text using Valx_CTgov')
    parser.add_argument('-i', default='data/diabetes.csv', help='Input CSV file')
    parser.add_argument('-f1', default='data/rules.csv', help='Domain knowledge feature list CSV file')
    parser.add_argument('-f2', default='data/variable_features_umls.csv', help='UMLS feature list CSV file')
    parser.add_argument('-v', default='All', help='Variable name: All, HBA1C, BMI, Glucose, Creatinine, BP-Systolic, BP-Diastolic')

    args = parser.parse_args()

    extract_variables(args.i, args.f1, args.f2, args.v)

    # result = extract_lab_measurement_info(text)
    # print("result: ", result)


if __name__ == '__main__':
    main()
