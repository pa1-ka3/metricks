# Overwiew

Package for analyze click-data files and produce Sanky diagrams

# Installation

## 1. Prerequisites 
 Python 3  (min version 3.6) (max 3.10? due to critical changes in holoviews API)

## 2. Create virtual environment

a. Type in cmd in desired folder:
`py -3 -m venv .venv`

b. then activate environment:
`venv\Scripts\activate`

say your folder named * * D:\content-team\click-data * *
then after successful activation it will looks like 
* * (venv) D:\content-team\click-data> * *

c. In virtual environment install required libs
`pip install holoviews bokeh pandas`

d. Place click-analyzer nearby venv

Recommended structure of module with venv (for Windows)
click-data/
├── click-analyzer/
│   ├── analyzer.py
│   └── ...
└── venv/
    ├── etc/
    ├── Lib/
    ├── Scripts/
    └── ...
Update parameters in run_analyzer.bat and place it into click-data


## 3. Run analysis

 In cmd launch run_analyzer.bat
`(venv) D:\content-team\click-data>run_analyzer.bat >out.txt 2>err.txt`

