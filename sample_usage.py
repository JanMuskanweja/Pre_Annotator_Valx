import Valx_core

def extract_lab_measurement_info(text):
    # Preprocess text
    cleaned_text = Valx_core.preprocessing(text)

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

# Example usage:
text = "hemoglobin > yy units"
result = extract_lab_measurement_info(text)
print(result)
