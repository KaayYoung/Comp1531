import random
import copy

user_list = input("Put a few comma separated numbers/characters/words:\n").split(',')
random.seed(a=0)

def shuffle(li):
    """
    This function returns a new list that is created by shuffling the elements of the
    provided list
    :param li: The list to be shuffled
    :return shuffled_list: The shuffled list
    """
    old_list = copy.deepcopy(li)
    shuffled_list = []

    while len(li) != len(shuffled_list):
        element = old_list[random.randint(0, len(old_list) - 1)]
        shuffled_list.append(element)
        old_list.remove(element)

    return shuffled_list

print("Shuffled List:")
output = shuffle(user_list)
out_string = output[0]

for entry in output[1:]:
    out_string += "," + entry

print(out_string)