def fizz_buzz(number=100):
    """
    This method displays fizz when a number
    is divisible by 3, buzz when an number
    is divisible by 5 and the number itself
    for every number between 1 and n
    :param n: The limit. (Default 100)
    """

    for i in range(number):
        #Check if divisible by 3 and 5. If so, print fizzbuzz
        if i % 3 == 0 and i % 5 == 0:
            print("fizzbuzz")
        # Print buzz if divisible by 3
        elif i % 3 == 0:
            print("fizz")
        # Print buzz if divisible by 5
        elif i % 5 == 0:
            print("buzz")
        #Print the number otherwise
        else:
            print(i)