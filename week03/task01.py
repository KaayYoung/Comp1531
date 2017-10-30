# Read string input and split into a list based on the spaces
string = str(input()).split(" ")
# Initialize a dictionary
words = {}
# Initialize new list
newString = []
# For all words, filter the words that have been spotted before
for word in string:
    if word.lower() not in words:
        words[word.lower()]=1
        new_string.append(word)

# Sort the words
new_string = sorted(new_string, key=lambda x: x.lower())
# Turn the list into a string
unique_string = ' '.join(new_string)
#Output the string
print(unique_string)