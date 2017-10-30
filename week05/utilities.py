def convert_to_list(string_input):
    """
    :param string_input: String version of the list
    """
    return [int(item) for item in string_input.split(",")]

def swap(numbers, index1, index2):
    """
    :param numbers: A list of numbers
    :param index1: First index
    :param index2: Second index
    """
    temp = numbers[index1]
    numbers[index1] = numbers[index2]
    numbers[index2] = temp

