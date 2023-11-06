
import csv
import json
import argparse

def convert_csv_to_json(input_file, output_file):
    # Initialize an empty list to store the JSON objects
    json_objects = []
    labels = ['TVariable', 'TRelation', 'TNegativeValue', 'TValue', 'TUnit']
    labels2 = ['TVariable', 'TRelation', 'TValue', 'TUnit']
    relation_mapping = {
        '<': 'TCreLt',
        '>': 'TCreGt',
        'V2V': 'TCreVtoV',
        '<=': 'TCreLte',
        '>=': 'TCreGte',
        '>negation': 'TCreGte'
    }

    # Open the input CSV file
    with open(input_file, 'r', newline='') as csv_in:
        reader = csv.reader(csv_in)
        # Initialize an ID counter
        id_counter = 551
        # Iterate through the rows in the input CSV file
        for row in reader:
            # Extract values from columns
            id_value = row[0]  # Assuming the ID is in the first column
            pid = row[6]
            mcid = row[7]
            text_value = row[2]  # Assuming the text is in the third column
            entities_column = eval(row[5])  # Assuming entities are in the sixth column
            # Initialize an empty list to store entities
            entities = []
            unique_entities = set()
            # Iterate through the entities in the sixth column
            # Iterate through each entity and offset string
            for i, entity_info in enumerate(entities_column):
                if len(entity_info) == 5:
                    entity = {}
                    for j, offset_string_list in enumerate(entity_info):
                        offset_string = offset_string_list[0]
                        if offset_string != '-1':  # Skip entries with -1 offset
                            start_offset, end_offset = map(int, offset_string.split(','))
                            if j == 1:
                                data = row[4]
                                parsed_data = eval(data)
                                label = relation_mapping.get(parsed_data[i][1], '')
                            else:
                                label = labels[j]

                            entity_key = (start_offset, end_offset)

                            if entity_key not in unique_entities:
                                # Create an entity dictionary
                                entity = {
                                    "id": id_counter,  # You can use the start_offset as an ID
                                    "label": label,
                                    "start_offset": start_offset,
                                    "end_offset": end_offset
                                }
                                id_counter += 1

                                entities.append(entity)
                                unique_entities.add(entity_key)
                else:
                    entity = {}
                    for j, offset_string_list in enumerate(entity_info):
                        offset_string = offset_string_list[0]
                        if offset_string != '-1':  # Skip entries with -1 offset
                            start_offset, end_offset = map(int, offset_string.split(','))
                            if j == 1:
                                data = row[4]
                                parsed_data = eval(data)
                                label = relation_mapping.get(parsed_data[i][1], '')
                            else:
                                label = labels2[j]

                            entity_key = (start_offset, end_offset)

                            if entity_key not in unique_entities:
                                entity = {
                                    "id": id_counter,  # You can use the start_offset as an ID
                                    "label": label,
                                    "start_offset": start_offset,
                                    "end_offset": end_offset
                                }
                                id_counter += 1

                                entities.append(entity)
                                unique_entities.add(entity_key)
         
            clinical_url = "https://classic.clinicaltrials.gov/ct2/show/"+id_value
            json_obj = {
                "id_url": clinical_url,
                "pid": pid,
                "mcid": mcid,
                "text": text_value,
                "entities": entities,
                "relations": [],  # Assuming there are no relations in your data
                "Comments": []  # Assuming there are no comments in your data
            }

            json_objects.append(json_obj)

    # Write the JSON objects to the output JSON file
    with open(output_file, 'w') as json_out:
        for json_obj in json_objects:
            json.dump(json_obj, json_out)
            json_out.write('\n')

    print("JSON conversion completed.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert CSV to JSON')
    parser.add_argument('-i', '--input',  help='Input CSV file path')
    parser.add_argument('-o', '--output', help='Output JSON file path')
    args = parser.parse_args()

    convert_csv_to_json(args.input, args.output)

