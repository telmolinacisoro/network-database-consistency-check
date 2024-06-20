# Function to swap middle parts of an input string
def swapParts(input_string):
    parts = input_string.split('-')
    if len(parts) != 4:
        raise ValueError("Input string must have exactly 4 parts separated by dashes")
    parts[1], parts[2] = parts[2], parts[1]
    return '-'.join(parts)
