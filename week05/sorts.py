from utilities import swap

def BubbleSort(numbers):
    all_changes = []
    flag = 1
    while flag == 1:
        flag = 0
        for i in range(len(numbers) - 1):
            if numbers[i+1] < numbers[i]:
                swap(numbers, i+1, i)
                all_changes.append(list(numbers))
                flag = 1

    return all_changes


