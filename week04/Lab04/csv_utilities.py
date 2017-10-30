import csv

def add_entry(row):
    with open("default_csv.csv", 'a') as csv_out:
        writer = csv.writer(csv_out)
        writer.writerow(row)

def get_all_entries():
    all_entries = []
    with open("default_csv.csv", 'r') as csv_in:
        reader = csv.reader(csv_in)

        for row in reader:
            all_entries.append(row)

    return all_entries




