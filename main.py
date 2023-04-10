import subprocess
import re
import json
import csv
import string
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill


def main():
    # Define PATH of repo directories that the tool will scan
    directories = [
        "/Users/lironbiam/Documents/GoatRepositories/Kotlin/AndroGoat",
        "/Users/lironbiam/Documents/GoatRepositories/habitica-android",
        "/Users/lironbiam/Documents/GoatRepositories/Kotlin/Goatlin",
        "/Users/lironbiam/Documents/GoatRepositories/Kotlin/NotyKT"
    ]

    # Tool definitions, see Readme.md for more information
    output_file = 'findings.json'  # Don't have to change this
    tool_cmd = ["horusec", "start", "-p=.", "-o=json", f"-O=./{output_file}", "-s=LOW"]  # CLI command for tool scan
    headers = ['severity', 'language', 'confidence', 'code', 'details']  # Headers for the CSV output file, matches the jq command's headers that we're keeping when filtering
    jq_cmd = ['jq', '[.analysisVulnerabilities[].vulnerabilities | {severity, language, confidence, code, details}]']
    # jq_cmd = ['jq', f'[.analysisVulnerabilities[].vulnerabilities | {{ {", ".join([f"{header}: .{header}" for header in headers])} }}]']  # Another method, more dynamic but less readable

    # Run CLI commands for each one of the directories defined above
    for directory in directories:
        # Extract project name from directory path
        project_name = re.search(r'/([^/]+)/?$', directory).group(1)
        print(f'Current working directory: {project_name}')
        
        # Change working directory
        subprocess.run(["cd", directory])
        
        # Run tool scan
        subprocess.run(tool_cmd, cwd=directory)
        
        # Parse tool output using jq
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
                # Handle non-printable ASCII characters in conversion from .json to .csv
                data_row = [project_name] + ["".join(filter(lambda x: x in string.printable, str(item[header]))) for header in headers]
                writer.writerow(data_row)

    # Merge findings from all directories into a single CSV file
    with open('merged_findings.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Repository'] + headers)
        for directory in directories:
            project_name = re.search(r'/([^/]+)/?$', directory).group(1)
            with open(f"{directory}/parsed.csv") as subdir_csv:
                subdir_reader = csv.reader(subdir_csv)
                next(subdir_reader)  # skip header row
                for row in subdir_reader:
                    # Write all fields except the Repository field
                    writer.writerow([project_name] + row[1:])
    
    # convert .csv to .xlsx
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

        # Define fill for alternating rows
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


if __name__ == "__main__":
    main()
