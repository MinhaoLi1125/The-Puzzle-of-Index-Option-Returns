import pandas as pd
import os

path1 = f'../output/table2_all.xlsx'
path2 = f'../output/latex.xlsx'
table1 = pd.read_excel(path1, names=['', 'Calls', 'CallPercentage', 'Puts', 'PutPercentage'])
table2 = pd.read_excel(path2)

latex_table1 = table1.to_latex(
    index=False,  # To not include the DataFrame index as a column in the table
    caption="Summary Statistics for Calls and Puts, April 1986 to January 2021 (Table 2 in Paper)",  # The caption to appear above the table in the LaTeX document
    #label="tab:model_comparison",  # A label used for referencing the table within the LaTeX document
    position="htbp",  # The preferred positions where the table should be placed in the document ('here', 'top', 'bottom', 'page')
    column_format="|l|l|l|l|l|",  # The format of the columns: left-aligned with vertical lines between them
    escape=False,  # Disable escaping LaTeX special characters in the DataFrame
    float_format="{:0.4f}".format  # Formats floats to two decimal places
)

latex_table2 = table2.to_latex(
    index=False,  # To not include the DataFrame index as a column in the table
    caption="Filters (Table B.1 in Paper)",  # The caption to appear above the table in the LaTeX document
    #label="tab:model_comparison",  # A label used for referencing the table within the LaTeX document
    position="htbp",  # The preferred positions where the table should be placed in the document ('here', 'top', 'bottom', 'page')
    column_format="|l|l|l|l|",  # The format of the columns: left-aligned with vertical lines between them
    escape=False,  # Disable escaping LaTeX special characters in the DataFrame
    float_format="{:0.2f}".format  # Formats floats to two decimal places
)

latex_content1 = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}

\title{The Puzzle of Index Option Returns}
\author{Minhao Li \and Yun Hu \and Zean Li \and Zilin Song}
\date{}

\begin{document}

\maketitle

\section*{The Nature of Replication}


\tab Beyond standard linear factor methodology in explaining S&P 500 Index call and put option returns, this academic paper hypothesized several crisis-related factors, including price jumps, volatility jumps, and liquidity to explain the cross-sectional variation in returns. In conclusion, their hypothesis was not rejected, and it has shown that the alphas of short-maturity out-of-money puts become economically and statistically insignificant.

In our replication project, we automatically downloaded option data from WRDS, and then filtered out certain rows based on the criteria given in the paper. This data filtering process contains 3 levels of filters, and each level contains three to five subfilters. As a result, we replicated the numbers in Table B.1 quite successfully (with roughly 0.93 million rows in total and only 30 thousands rows in difference). After we replicated the Table B.1, we used the resulting DataFrame to replicate Table 2. In the end, we were also able to reproduce the numbers close enough.

We also automated the whole workflow by leveraging doit, which utilize the dodo.py file to replicate our tables without manual works.
"""

table_content = f"""
{latex_table1}
{latex_table2}
"""

latex_content2 = r"""
\section*{How the project went: success, challenges, data sources}

We found our success in replicating the numbers closely while at the same time utilizing some knowledge in option pricing. For example, when writing the last two filters, we need to first write a program to calculate the implied volatility and the implied market interest rate, and fit the calculated implied volatility to a normal distribution. Then, remove the samples that deviate too much. Calculating the implied volatility requires solving the function inversely through the pricing formula, and it is necessary to avoid numerous issues such as data missing, data mismatch, and problems with cleaning the original data. This not only uses a lot of statistical knowledge but also requires analysis combining option pricing theory.

challenges:
"""


# Write to .tex file
tex_file = f'../reports/write-up.tex'
with open(tex_file, "w") as file:
    file.write(latex_content1)
    file.write(latex_content2)
    file.write(table_content)
    file.write(r"\end{document}")
    
print("PDF created with the LaTeX table.")