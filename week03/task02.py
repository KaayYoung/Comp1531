fib_dict = {
    0: 0,
    1: 1,
    2: 1,
    3: 2
}

# Define this function to return the expected output
# Do not print it from this function
def fib_sequence(num):
    if num < 0:
        return "Invalid input"
    if num in fib_dict:
        return fib_dict[num]
        # print("%d", fib_dict[num])
    fib_dict[num] = fib_sequence(num - 1) + fib_sequence(num - 2)
    return fib_dict[num]

number = int(input())
print(fib_sequence(number))