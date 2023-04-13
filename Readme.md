<h2>Summarize Security Findings</h2>

<h4>Automates the execution of a tool on different repositories.</h4>

![exceloutput](https://gcdnb.pbrd.co/images/Pc77F8KqRmjJ.png)

.xlsv & .csv - represent the detections

.txt - an automatically generated verbal summarization of the tool used, CLI commands, repositories and findings.

.xlsx findings are Grouped By repository name and provide a concise overview of the detected vulnerabilities.

<br>

<hr>
<br>

<h3>Preqreuisities</h3>
In order to use the automation tool, you have to be familiar with the scanning tool and what you want it to achieve.

For example, if we're using Gitleaks, we need the following: 

* Paths of local repositories that the tool is intended to scan

* Correct CLI Syntax (gitleaks detect ..)

* Awareness of the JSON output (what Key/Value pairs of each Object do we want to keep?)

<br>

<h3>Usage</h3>
Under 'main.py' define the following variables:

* directories - list that provides the automation tool with the PATH to each repo directory that the tool will be scanning.

* tool_cmd - instructions for the tool to run in the CLI

* headers - when examining the .json output, which Keys and Values we want to preserve and display later on in the .xlsx file?

* jq_cmd - instructions for parsing of the ```{output_file}.json``` to only keep the ```headers``` that we defined, without redundant info.

* <b>Note that 'headers' must match the headers used in 'jq_cmd', example in the below section.</b>

* (Optional) output_file - for example ```findings.json```, the file in which findings data will be stored in. You don't have to change it.

* (Optional) tool_version - for example ```1.17.1``` - version of the tool at the time of testing it.

Files (.json, .csv) will be created in each of the target directories. These files were used to generate the final, merged .xlsx and .csv. You may review them to examine the findings, however, the next scan you initiate will erase these files and overwrite them with new findings.

<br>

<h3>Definition Examples:</h3>

```python
directories = [
    "~/Documents/JavascriptRepos/repoName",
    "~/Documents/PythonRepos/anotherRepo",
    "~/Documents/..."
]
```

```python
# OPTIONAL DEFINITIONS
output_file = 'findings.json'
tool_version = "undefined"  # or alternatively, "1.12.1" for example
```

Example - Horusec (only keep 'severity', 'language', 'confidence', 'code', 'details' when parsing JSON output)
```python
# MANDATORY DEFINITIONS
tool_cmd = ["horusec", "start", "-p=.", "-o=json", f"-O=./{output_file}", "-s=LOW"] 
headers = ['severity', 'language', 'confidence', 'code', 'details']
jq_cmd = ['jq', '[.analysisVulnerabilities[].vulnerabilities | {severity, language, confidence, code, details}]']
```

Example - Semgrep (only keep 'severity', 'path', 'lines', 'message' when parsing JSON output)
```python
tool_cmd = ["semgrep", "scan", "--config=auto", "--verbose", f"--output=./{output_file}", "--json", "--severity=ERROR", "--severity=WARNING"]
headers = ['severity', 'path', 'lines', 'message']
jq_cmd = ['jq', '[.results[] | {lines: .extra.lines, message: .extra.message, severity: .extra.severity, path: .path}]']
```

For a better understanding:
```python
headers = ['One', 'Two']
jq_cmd = ['jq', {One, Two}']
```

<br>

<h3>Program Output</h3>

<b>Files generated for Horusec v2.8.0</b>

<b>horusec-v2.8.0.csv</b> - .csv file containing merged findings / detections of all repos together.

<b>horusec-v2.8.0.xlsx</b> - Excel sheet, a conversion of the .csv file with subtle styling for an easier read of the detections.

<b>horusec-v2.8.0.txt</b> - Verbal summarization to conclude what the .xlsx report is about and how it was generated.