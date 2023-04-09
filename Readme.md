<h2>Summarize Security Findings</h2>

Automates the execution of a tool on different repositories. Outcome is a findings.xlsx file in the root directory of this Python program.

findings.xlsx summarizes the tool's findings for each repository scanned and shortens the process of researching new tools.

Findings are grouped by the repository name and provide a concise overview of the detected vulnerabilities.

<hr>

<h3>Preqreuisities</h3>
In order to use the automation tool, you have to be familiar with the scanning tool and what you want it to achieve.
For example, if we're using Gitleaks, we need the following: 
* Paths of local repositories that the tool is intended to scan
* Correct CLI Syntax (gitleaks detect ..)
* Awareness of the JSON output (what Key/Value pairs of each Object do we want to keep?)




<h3>Usage</h3>
Under 'toolExecution.py' define the following variables:
* directories - provides the automation tool with the PATH to each repository directory that the tool will be scanning.
* output_file - for example ```findings.json```, the file in which findings data will be stored in. You don't have to change it.
* tool_cmd - instructions for the tool to run in the CLI
* headers - when examining the .json output, which Keys and Values we want to preserve and display later on in the .xlsx file?
* jq_cmd - instructions for parsing of the ```output_file.json``` to only keep the ```headers``` that we defined, without redundant info.

<h4>Note that every definition is later relied on and used, do not hard-code anything that needs to be written inside the defined variables.</h4>

After defining the required variables, run the program. A file named 'output.xlsx' will be created in the root dir of the Python program, in addition to a 'merged_findings.csv' in case you want to review and edit the .csv that contains the merged findings from all repositories. 

<h3>Definition Examples:</h3>
```python
directories = [
    "/Users/lironbiam/Documents/GoatRepositories/Kotlin/AndroGoat",
    "/Users/lironbiam/Documents/GoatRepositories/Swift/iGoat-Swift",
    "/Users/lironbiam/Documents/GoatRepositories/Kotlin/Goatlin",
    "/Users/lironbiam/Documents/GoatRepositories/Kotlin/NotyKT"
]
```

```python
output_file = 'findings.json'
tool_cmd = ["horusec", "start", "-p=.", "-o=json", f"-O=./{output_file}", "-s=LOW, MEDIUM"]
```
The headers & jq_cmd of ``jq '[.analysisVulnerabilities[].vulnerabilities | {confidence, details, language, severity}]'`` will be written as:
```python
headers = ['severity', 'language', 'confidence', 'code', 'details']
jq_cmd = ['jq', f'[.analysisVulnerabilities[].vulnerabilities | {{ {", ".join([f"{header}: .{header}" for header in headers])} }}]']
```
Another Example, ``jq '{DetectorName, Raw}'`` will be written as:
```python
headers = ['DetectorName', 'Raw']
jq_cmd = ['jq', f'[{{ {", ".join([f"{header}: .{header}" for header in headers])} }}]']
```
Basically the ``'{DetectorName, Raw}'`` translates into:
```python
{{ {", ".join([f"{header}: .{header}" for header in headers])} }}
```
For a better understanding:
```python
headers = ['DetectorName', 'Raw']
jq_cmd = ['jq', f'[ THE_UGLY_STATEMENT ]']
```