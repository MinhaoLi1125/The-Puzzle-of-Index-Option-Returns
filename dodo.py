"""Run or update the project. This file uses the `doit` Python package. It works
like a Makefile, but is Python-based
"""

import sys
sys.path.insert(1, "./src/")
import os
import shutil

import config
from pathlib import Path
from doit.tools import run_once
import platform

OUTPUT_DIR = Path(config.OUTPUT_DIR)
DATA_DIR = Path(config.DATA_DIR)
REPORTS_DIR = Path(config.REPORTS_DIR)

# fmt: off
## Helper functions for automatic execution of Jupyter notebooks
def jupyter_execute_notebook(notebook):
    return f"jupyter nbconvert --execute --to notebook --ClearMetadataPreprocessor.enabled=True --inplace ./src/{notebook}.ipynb"
def jupyter_to_html(notebook, output_dir=OUTPUT_DIR):
    return f"jupyter nbconvert --to html --output-dir={output_dir} ./src/{notebook}.ipynb"
def jupyter_to_md(notebook, output_dir=OUTPUT_DIR):
    """Requires jupytext"""
    return f"jupytext --to markdown --output-dir={output_dir} ./src/{notebook}.ipynb"
def jupyter_to_python(notebook, build_dir):
    """Convert a notebook to a python script"""
    return f"jupyter nbconvert --to python ./src/{notebook}.ipynb --output _{notebook}.py --output-dir {build_dir}"
def jupyter_clear_output(notebook):
    return f"jupyter nbconvert --ClearOutputPreprocessor.enabled=True --ClearMetadataPreprocessor.enabled=True --inplace ./src/{notebook}.ipynb"
# fmt: on

# Check if .env file exists. If not, create it by copying from .env.example
env_file = ".env"
env_example_file = "env.example"

if not os.path.exists(env_file):
    shutil.copy(env_example_file, env_file)

def task_load_OptionsMetrics():
    file_dep = [
        "./src/config.py",
        "./src/load_OptionsMetrics.py"
    ]
    
    targets = [DATA_DIR / "pulled" / "OptionsMetrics.parquet"]

    return {
        'actions': [
            "ipython ./src/config.py", 
            "ipython ./src/load_OptionsMetrics.py"
        ],     
        'targets': targets, 
        'file_dep': file_dep,
        'clean': True,
        'verbosity': 2,
    }
    

def task_filter_merge():
    
    file_dep = [
        "./src/config.py",
        "./src/filter_merge.py"
    ]
    
    
    targets = [
        DATA_DIR / "manual" / "data_filter_3.parquet", 
        OUTPUT_DIR / "latex.xlsx"
    ]
               
    return {
        'actions': [
            "ipython ./src/config.py",
            "ipython ./src/filter_merge.py"
        ],     
        'targets': targets, 
        'file_dep': file_dep,
        'clean': True,
        'verbosity': 2,
    }



def task_table2_analysis():
    file_dep = [
        "./src/table2_analysis.py"
    ]
    

    targets = [OUTPUT_DIR.joinpath(f"table2_month.xlxs")]

    return {
        'actions': [
            "ipython ./src/table2_analysis.py"
        ],     
        'targets': targets, 
        'file_dep': file_dep,
        'clean': True,
        'verbosity': 2,
    }


def task_plot():
    file_dep = [
        "./src/config.py",
        "./src/plot.py"
    ]
    
    targets = [
        OUTPUT_DIR / "iv_plt.png", 
        OUTPUT_DIR /'ttm_plt.png', 
        OUTPUT_DIR / 'moneyness_plt.png',
        
    ]

    return {
        'actions': [
            "ipython ./src/config.py",
            "ipython ./src/plot.py"
        ],     
        'targets': targets, 
        'file_dep': file_dep,
        'clean': True,
        'verbosity': 2,
    }


def task_df_to_latex_write_up():
    file_dep = [
        "./src/df_to_latex_writeup.py"
    ]
    
    targets = [REPORTS_DIR / "write-up.tex"]

    return {
        'actions': [
            "ipython ./src/df_to_latex_writeup.py"
        ],     
        'targets': targets, 
        'file_dep': file_dep,
        'clean': True,
        'verbosity': 2,
    }
    
def task_compile_latex_docs():
    file_dep = [
        "./reports/write-up.tex",
    ]
    file_output = [
        "./reports/write-up.pdf",
    ]
    targets = [file for file in file_output]

    return {
        "actions": [
            "latexmk -xelatex -cd ./reports/write-up.tex",  # Compile
            "latexmk -xelatex -c -cd ./reports/write-up.tex",  # Clean
            # "latexmk -CA -cd ../reports/",
        ],
        "targets": targets,
        "file_dep": file_dep,
        "clean": True,
    }
