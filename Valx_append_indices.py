def find_index(text, pattern):
    indices = []
    start = text.find(pattern)
    end = start+len(pattern)
    indices.append(f"{start}, {end}")
    return indices
    
import re

# Create a dictionary to map relations to words
relation_word_dict = {
    "<": r"(less than|lesser than|below|under|within|<|lower than|worse than|younger than|to <|past)",
    ">": r"(more than|greater than|greater|above|over|superior to|exceeding|exceed|>|larger than|prior|older than|prior|higher than)",
    "<=": r"(no more or around|below or equal to|lower or equal to|small than or equal to|less than or equal to|less than or equal|less or equal to|lesser than or equal to|lesser or equal to|lower than or equal to|equal to or lower than|equal to or below|equal to or less than|equal or less than|up to and including|smaller / equal|at most|up to|maximum|max|past|prior|< or equal to|=<|<=|â‰¤|< or = to|< or =|</=|<-|= or <|to|< -)",
    ">=": r"(more than or equal to|equal to or greater than|equal to or higher than|equal to or more than|equal or greater than|equal to or above|superior or equal to|greater than or equal to|greater or equal to|higher or equal than|higher or equal to|greater than or equal|great or equal to|at least|greater / equal|above or equal to|minimum|> or equal to|and older|or older|within|â‰¥|>=|=>|> or = to|= or >|> or =|>/=|>-|= or >)",
    "=": r"(equal to|=)",
    "V2V": r"(\d+\s*[-to]+\s*\d+)",
    "negation": r"(past|previous|last)\s+(\d+)"
}

def relationWord(element, text):
    match = re.search(relation_word_dict.get(element, ""), text)
    if match:
        return match.group(0)
    return None

import argparse
import csv
import re

def process_csv(input_file, output_file):
    # Open the input CSV file and create an output CSV file
    with open(input_file, 'r', newline='') as csv_in, open(output_file, 'w', newline='') as csv_out:
        reader = csv.reader(csv_in)
        writer = csv.writer(csv_out)
        
        # Iterate through the rows in the input CSV file
        for row in reader:
            text = row[-1]  # Assuming the list of lists is in the last column
            if text:
               sublist = eval(text)
            else:
               sublist = []

            all_indices = []

            for element in sublist:
                indices_for_element = []
                negation = 0
                # Iterate through each sub-element in the element
                for sub_element in element:
                    if sub_element in ['<', '>=', '=', '<=', '>', "V2V"]:
                        pattern = relationWord(sub_element, row[2])
                    elif re.search("years", sub_element):
                        pattern = "years"
                    elif sub_element == ">negation":
                        pattern = "within"
                        negation = 1
                    else:
                        pattern = sub_element
                    if pattern:
                        indices_for_element.append(find_index(row[2], pattern))
                    else:
                        indices_for_element.append(['-1, -1'])
                    if negation == 1:
                        find_negate = relationWord("negation", row[2])
                        indices_for_element.append(find_index(row[2], find_negate))
                        
                unique_indices_for_element = []
                for index in indices_for_element:
                    if index not in unique_indices_for_element:
                        unique_indices_for_element.append(index)
                while len(unique_indices_for_element) < 4:
                    unique_indices_for_element.append(['-1, -1'])
                all_indices.append(unique_indices_for_element)
            row.append(all_indices)
            writer.writerow(row)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a CSV file and add indices')
    parser.add_argument('-i', default='input.csv', help='Input CSV file')
    parser.add_argument('-o', default='output.csv', help='Output CSV file')

    args = parser.parse_args()
    process_csv(args.i, args.o)

