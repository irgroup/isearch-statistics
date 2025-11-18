# isearch-statistics

# ArXiv Metadata Extraction and Analysis Suite

A comprehensive Python toolkit for extracting, processing, and analyzing metadata from ArXiv scientific papers through the iSearch dataset.


## Overview

This suite consists of two main components:

1. **Metadata Extractor** - Downloads and processes ArXiv abstract pages to extract comprehensive metadata
2. **Distribution Analyzer** - Analyzes and visualizes license and version distribution patterns

## Prerequisites

- Python 3.8+
- Required packages:
  ```bash
  pip install pandas matplotlib seaborn requests beautifulsoup4

## Features

### Metadata Extractor

**Input**: iSearch dataset (`iSearchIDs.txt`)

**Processing**:
- Downloads ArXiv abstract pages
- Extracts license information (URL + standardized names)
- Captures latest version numbers
- Collects comprehensive paper metadata

**Output**:
- `arxiv_metadata.csv` - Complete dataset with all extracted fields
- `abstract_pages/` - Local cache of downloaded HTML pages

**Extracted Fields**:
- Document ID, Abstract URL
- License URL, License Name, Version
- Title, Authors, Comments, Subjects
- Journal Reference, Related DOI

### Distribution Analyzer

**Input**: Generated `arxiv_metadata.csv`

**Analysis**:
- License type distribution and coverage statistics
- Version distribution patterns
- Coverage analysis and quality metrics

**Output**:
- Professional visualizations (PNG)
- Comprehensive analysis report (TXT)
- Console summary with key metrics

## Usage

### 1. Metadata Extraction

```python
from arxiv_metadata_extractor import ArXivMetadataExtractor

extractor = ArXivMetadataExtractor()
extractor.START_DOC_ID = 60987  # Optional: Set range
extractor.END_DOC_ID = 61041    # Optional: Set range
extractor.run()
```

### 2. Distribution analysis
```python
from license_version_analyzer import LicenseVersionAnalyzer

analyzer = LicenseVersionAnalyzer(
    csv_path="arxiv_metadata.csv",
    output_dir="result_analysis"
)
analyzer.run_analysis()
```

### 3. Complete Pipeline
Run both extraction and analysis sequentially.

### Configuration
### Extraction Parameters (in code)

INPUT_PATH = "iSearchIDs.txt"           # Source dataset
OUTPUT_CSV_PATH = "arxiv_metadata.csv"  # Output file
ABSTRACT_FOLDER = "abstract_pages"      # HTML cache
REQUEST_DELAY = 0.5                     # Rate limiting
DOC_ID_RANGE = (60987, 61041)           # Processing range

### Analysis Parameters

python
csv_path = "arxiv_metadata.csv"         # Input data
output_dir = "result_analysis"          # Output directory

## Use Cases

- **Research Analysis**: Study license adoption trends in academic publishing
- **Data Quality**: Assess metadata completeness in scholarly datasets  
- **Collection Development**: Inform acquisition decisions for libraries/institutions
- **Open Science**: Track adoption of open access licenses over time
