import json

with open("crosswordlist.txt", "r") as file:
    file_content = file.read()

# Split the content into lines
lines = file_content.split("\n")

# Convert each line to a tuple (string, int)
data = [
    (line.split(";")[0].replace(" ", "").upper(), int(line.split(";")[1]))
    for line in lines
]

# sort data by number
sorted_data = []
for i in range(51):
    num = 50 - i
    for word, val in data:
        if val == num:
            sorted_data.append((word, val))

# Save the data to a JSON file
json_file_path = "crossword_words.json"
with open(json_file_path, "w") as json_file:
    json.dump(sorted_data, json_file)
