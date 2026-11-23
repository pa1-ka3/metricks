# metricks (click-analyzer)

A Python package for measuring the quality of a document search system from its **click-data logs** (user search and document-open events).

It is used to:

- compute click-based search metrics: **CTR@1 / CTR@10 / CTR@100** and **Non-Click rate**, plus the distribution of the first-click position;
- build a **baseline dataset** of queries with relevant (clicked) documents from the logs;
- compute ranking-quality metrics **MRR@10** and **NDCG@10** by comparing the baseline with the results of the search engine;
- collect these numbers into a weekly CSV report (`metrics_report.csv`);
- analyse queries (normalization, popularity, clustering by type) and draw Sankey diagrams of user search sessions.

> The package is designed to be imported as a Python package (modules use relative imports) and expects to be installed under the name `click_analyzer` (see [Running the weekly report](#running-the-weekly-report)). The default paths in the scripts are Windows paths and are specific to the original environment; adjust them to your setup.

## Metrics

| Metric | Description | Source |
|--------|-------------|--------|
| `CTR@K` | Share of searches in which the topmost clicked document is at position ≤ K (K = 1, 10, 100). | [query_clickthrough_statistics.py](query_clickthrough_statistics.py) |
| `Non-Click` | `1 - CTR`: share of searches without any document click. | [query_clickthrough_statistics.py](query_clickthrough_statistics.py) |
| `MRR10`, `NDCG10` | Mean Reciprocal Rank and Normalized DCG over the top 10 results, computed against the baseline dataset. | [create_baseline.py](create_baseline.py), [MRR_EWB/](MRR_EWB) |

Click events, search queries and "qta" (query-to-action) events are grouped into sessions and searches, and extra actions (e.g. `linkcopied`, `downloadpdf`, `smartsearch*`, see [constants.py](constants.py)) are tracked separately from document-open actions (`documentvieweropened`, `documentviewed`).

## Package layout

| Module | Purpose |
|--------|---------|
| [statistics_collector.py](statistics_collector.py) | **Main entry point.** Selects the last full week of click data, computes CTR/Non-Click and MRR/NDCG, and updates `metrics_report.csv`. |
| [files_selector.py](files_selector.py), [sort_click_data_files.py](sort_click_data_files.py) | Select and sort click-data directories/files for a period (previous Sunday → last Saturday). |
| [analyser.py](analyser.py) | Reads click-data log files and accumulates events; also a CLI that dumps session summaries. |
| [accumulations.py](accumulations.py), [collections_helpers.py](collections_helpers.py), [constants.py](constants.py) | Event grouping, click-through calculation and dictionary helpers. |
| [query_clickthrough_statistics.py](query_clickthrough_statistics.py) | Computes CTR@K, Non-Click rate, first-click statistics and writes detailed event dumps. |
| [create_dataset.py](create_dataset.py) | Builds the baseline dataset `adataset.<start>.<end>.json(.bz2)` (queries with relevant documents) from daily click data. |
| [create_baseline.py](create_baseline.py), [MRR_EWB/](MRR_EWB) | Runs the queries in the test environment, combines results with the baseline and calculates MRR/NDCG. |
| [get_queries_by_users.py](get_queries_by_users.py) | Extracts unique queries, query counts and queries per user from click data. |
| [normalization.py](normalization.py), [most_popular.py](most_popular.py), [clustering_predefined.py](clustering_predefined.py) | Query normalization (stop-word removal), most popular queries, and clustering by type (boolean, document numbers, abbreviations, wildcards, letters/digits only, etc.). |
| [diagram_plotly.py](diagram_plotly.py), [diagram_holoviews.py](diagram_holoviews.py) | Sankey diagrams of search sessions (Plotly / HoloViews). |
| [test/](test) | Unit tests for accumulations, grouping and click metrics. |

## Installation

### Prerequisites

- Python 3.6+ (up to 3.10 if you use the HoloViews diagrams, due to breaking changes in the HoloViews API).
- Access to the click-data logs (the weekly collector reads them from `<click-data-root>\<YYYY-MM>\...`).

### Setup (Windows)

1. Create and activate a virtual environment:

   ```
   py -3 -m venv venv
   venv\Scripts\activate
   ```

2. Install the dependencies:

   ```
   pip install pandas tqdm python-dateutil nltk regex plotly holoviews bokeh panel
   ```

   Only the dependencies of the modules you use are required (e.g. `holoviews`, `bokeh`, `panel` and `plotly` are needed only for diagrams; `nltk` for query normalization). The MRR/NDCG calculation also requires the external `dataset_tools` module (`Metrics_v2`, `Report`).

3. Place this package next to the virtual environment in a folder named `click_analyzer`:

   ```
   click-data/
   ├── click_analyzer/        <- this repository
   │   ├── statistics_collector.py
   │   └── ...
   ├── venv/
   └── run_statistics_colector.bat
   ```

## Usage

### Running the weekly report

[run_statistics_colector.bat](run_statistics_colector.bat) runs the collector and uploads the resulting report. Place it in the `click-data` folder and run:

```
(venv) D:\content-team\click-data> run_statistics_colector.bat
```

or run the collector directly:

```
python -m click_analyzer.statistics_collector > out_statistics_collector.txt
```

The collector:

1. cleans the work folders;
2. selects the click-data for the last full week (previous Sunday → last Saturday);
3. computes CTR@1/10/100 and Non-Click rate;
4. calculates MRR10 and NDCG10 against the latest baseline dataset;
5. adds/replaces the row for the period end date in `metrics_report.csv`, makes a dated backup and copies the report to the target location.

The report has the columns `Data, CTR1, CTR10, CTR100, Non-Click, MRR10, NDCG10`.

The input, work and output paths are hard-coded in `statistics_collector.py`, `create_baseline.py` and the `.bat` file; update them for your environment.

### Individual tools

Run the modules from the parent folder of the package so that relative imports work:

```
# CTR and other click-through statistics
python -m click_analyzer.query_clickthrough_statistics --clickPath <click-data-dir> --outputFile <output-prefix> [--sessionid <id>] [--userid <id>]

# Session summaries from raw click data
python -m click_analyzer.analyser --clickPath <click-data-dir> --outputFile <output-file>

# Queries, counts and queries per user
python -m click_analyzer.get_queries_by_users --clickPath <click-data-dir> --outputFile <output-file> [--sessionid <id>] [--userid <id>]

# Baseline dataset for a date range
python -m click_analyzer.create_dataset --inputDir <click-data-dir> --outputDir <output-dir> --startDate YYYY-MM-DD --endDate YYYY-MM-DD
```

Query normalization, popularity and clustering ([normalization.py](normalization.py), [most_popular.py](most_popular.py), [clustering_predefined.py](clustering_predefined.py)) are scripts with input/output paths defined in their `__main__` blocks.

### Tests

From the parent folder of the package:

```
python -m unittest discover -s click_analyzer/test -t . -p "*_test.py"
```
