import csv

input_file = 'hawaii_nonprofit_names.csv'   # Change this to your input CSV filename
output_file = 'hawaii_nonprofit_names_without.csv' # Output file with cleaned data

with open(input_file, newline='', encoding='utf-8') as csv_in, \
     open(output_file, 'w', newline='', encoding='utf-8') as csv_out:

    reader = csv.reader(csv_in)
    writer = csv.writer(csv_out)

    for row in reader:
        cleaned_row = [cell.replace('.', '').replace(',', '') for cell in row]
        writer.writerow(cleaned_row)

print("Cleaning complete! Check", output_file)
