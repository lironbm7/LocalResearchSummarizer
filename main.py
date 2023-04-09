import subprocess
import re
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
import csv

# Define PATH of repo directories that the tool will scan
directories = [
    "/Users/lironbiam/Documents/GoatRepositories/Kotlin/AndroGoat",
    "/Users/lironbiam/Documents/GoatRepositories/Swift/iGoat-Swift",
    "/Users/lironbiam/Documents/GoatRepositories/Kotlin/Goatlin",
    "/Users/lironbiam/Documents/GoatRepositories/Kotlin/NotyKT"
]
# Tool definitions, see Readme.md for more information
output_file = 'findings.json'  # you don't have to change it
tool_cmd = ["horusec", "start", "-p=.", "-o=json", f"-O=./{output_file}", "-s=LOW"]
headers = ['severity', 'language', 'confidence', 'code', 'details']
jq_cmd = ['jq', f'[.analysisVulnerabilities[].vulnerabilities | {{ {", ".join([f"{header}: .{header}" for header in headers])} }}]']

####
# You don't need to change anything below this comment.
####

# Run CLI commands for each one of the directories defined above
for directory in directories:
    project_name = re.search(r'/([^/]+)/?$', directory).group(1)
    print(f'Current working directory: {project_name}')
    # change working dir
    subprocess.run(["cd", directory])
    # run tool scan
    subprocess.run(tool_cmd, cwd=directory)
    # run jq to parse the output
    with open(f"{directory}/parsed.json", "w") as f:
        subprocess.run(jq_cmd, cwd=directory, stdout=f, input=open(f"{directory}/{output_file}").read().encode())
    # Convert parsed JSON files to CSV files
    with open(f"{directory}/parsed.json") as f:
        data = json.load(f)
    with open(f"{directory}/parsed.csv", "w", newline='') as f:
        writer = csv.writer(f)
        headers_row = ['Repository'] + headers
        writer.writerow(headers_row)
        for item in data:
            data_row = [project_name] + [item[header] for header in headers]
            writer.writerow(data_row)

with open('merged_findings.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Repository'] + headers)
    for directory in directories:
        project_name = re.search(r'/([^/]+)/?$', directory).group(1)
        with open(f"{directory}/parsed.csv") as subdir_csv:
            subdir_reader = csv.reader(subdir_csv)
            next(subdir_reader) # skip header row
            for row in subdir_reader:
                writer.writerow([project_name] + row[1:])  # write all fields except the Repository field

with open('merged_findings.csv', 'r') as f:
    data = csv.reader(f)
    next(data)  # Skip header row

    # Create a new Excel workbook and select the active worksheet
    wb = Workbook()
    ws = wb.active

    ws.append(["Repository"] + headers)

    # Apply bold and fill pattern to header row
    header_row = ws[1]
    header_font = Font(bold=True)
    header_fill = PatternFill(start_color='D9D9D9', end_color='D9D9D9', fill_type='solid')
    for cell in header_row:
        cell.font = header_font
        cell.fill = header_fill

    # Define fill patterns for alternating rows
    white_fill = PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')
    grey_fill = PatternFill(start_color='F0F0F0', end_color='F0F0F0', fill_type='solid')

    # Loop through the rows of data and write them to the worksheet
    for i, row in enumerate(data, start=2):  # Start at row 2 to skip header
        ws.append(row)

        # Apply alternating fill pattern to data rows only
        if i % 2 == 0:
            for cell in ws[f'A{i}':f'Z{i}'][0]:
                cell.fill = white_fill
        else:
            for cell in ws[f'A{i}':f'Z{i}'][0]:
                cell.fill = grey_fill

    # Auto-size columns to fit their content
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    # Save the Excel workbook
    wb.save('findings.xlsx')