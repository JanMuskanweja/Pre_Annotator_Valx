import Valx_core

def extract_lab_measurement_info(text):
    Valx_core.init_features()
    cleaned_text = Valx_core.preprocessing(text)

    print(cleaned_text)

    """
    # Extract candidates
    sections_num, candidates_num = Valx_core.extract_candidates_numeric(text)
    name_list = "hemoglobin"  # The keyword you want to search for
    sections, candidates = Valx_core.extract_candidates_name(sections_num, candidates_num, name_list)

    for candidate in candidates:
        formalized_expression = Valx_core.formalize_expressions(candidate)
        print(formalized_expression)
    """

    """
    # Extract measurement
    measurement = Valx_core.extract_measurement(cleaned_text)

    # Extract relationship
    relationship = Valx_core.extract_relationship(cleaned_text)

    # Extract numeric quantity
    numeric_quantity = Valx_core.extract_numeric_quantity(cleaned_text)

    # Extract units
    units = Valx_core.extract_units(cleaned_text)


    return {
        "Measurement": measurement,
        "Relationship": relationship,
        "Numeric Quantity": numeric_quantity,
        "Units": units
    }
    """




# Example usage:
text = "hemoglobin > yy units"
result = extract_lab_measurement_info(text)
print(result)
