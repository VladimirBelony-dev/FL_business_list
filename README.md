# Florida Corporation Data Processing & Document Number Matching System

## Overview

This project demonstrates a comprehensive data processing pipeline for extracting, cleaning, and matching Florida corporation data with document numbers. The system processes over 8 million officer records from raw text files and matches them with company data using advanced fuzzy matching algorithms.

## 🎯 Project Goals

- Extract officer and company data from Florida corporation text files
- Match company names with their corresponding document numbers
- Create a comprehensive database with proper formatting
- Achieve high matching accuracy while preserving data integrity

## 📊 Data Sources

### Input Files
- **cordata0.txt - cordata9.txt**: Florida corporation data (10 files, ~1.6GB each)
- **npcordata0.txt - npcordata9.txt**: Florida non-profit corporation data (10 files, ~28MB each)
- **Corps 10-2-25.xlsx**: Target company list for matching (18,857 companies)

### Output Files
- **new_officer_sheet_20251004_161742.csv**: Complete extracted data (8.1M records, 2.3GB)
- **Corps_10-2-25_FORMATTED Final 10-4-25.xlsx**: Final formatted results with document numbers

## 🏗️ System Architecture

### Phase 1: Data Extraction (`extract_officers_full.py`)
- **Purpose**: Extract structured data from raw text files
- **Key Features**:
  - Chunked processing for memory efficiency
  - Fixed-width field parsing
  - Address component extraction (city, state, zip)
  - Officer role prioritization

### Phase 2: Document Number Matching (`document_number_matcher.py`)
- **Purpose**: Match companies with document numbers using fuzzy matching
- **Key Features**:
  - RapidFuzz for high-performance matching
  - Intelligent indexing system (exact, prefix, token)
  - Parallel processing capabilities
  - Configurable similarity thresholds

### Phase 3: Data Integration (`fill_officer_address_data.py`)
- **Purpose**: Merge matched data and apply professional formatting
- **Key Features**:
  - Corps-style formatting (blue/white alternating rows)
  - Single-line address formatting
  - Multiple output sheets (Full Data, Corps View, Statistics)
  - Professional Excel styling

## 🔧 Technical Implementation

### Data Structure Analysis

The raw text files use a fixed-width format:
```
Position 0-12:   Document Number
Position 12-165: Company Name (initially truncated - fixed)
Position 165-315: Address Line 1
Position 315-465: Address Line 2 (contains city, state, zip)
Position 600-900: Officer Information
```

### Key Challenges Solved

1. **Company Name Truncation**: Initial extraction was missing first 3 letters
   - **Problem**: `UNTANG LLC` instead of `WOYUNTANG LLC`
   - **Solution**: Adjusted extraction position from 15 to 12

2. **Address Parsing**: Complex address format with embedded data
   - **Pattern**: `CITY FL33304` (no space between state and zip)
   - **Solution**: Multi-pattern regex matching with fallbacks

3. **Memory Management**: Processing 8+ million records
   - **Solution**: Chunked processing and efficient data structures

4. **Matching Accuracy**: Fuzzy matching with high precision
   - **Solution**: Intelligent indexing + RapidFuzz + role prioritization

### Status Code Decoding

Discovered the meaning of status codes in the data:
- **AFLAL** = Active Florida Limited Liability Company
  - **A** = Active
  - **FL** = Florida  
  - **AL** = Authorized to do business (foreign LLC)

## 📈 Results

### Data Processing Statistics
- **Total Records Processed**: 8,142,243 officer records
- **Unique Companies**: 7,923,160
- **Unique Document Numbers**: 8,037,681
- **Processing Time**: ~17 minutes for full extraction

### Matching Performance
- **Total Companies in Target**: 18,857
- **Successfully Matched**: 15,664 (83.1%)
- **Exact Matches**: 8,445
- **Fuzzy Matches**: 7,219

### Data Quality
- **Complete Address Records**: 8,142,243 (100%)
- **Florida Records**: 7,090,424 (87%)
- **Properly Formatted**: 100%

## 🚀 Usage Instructions

### Prerequisites
```bash
pip install pandas numpy rapidfuzz openpyxl beautifulsoup4 requests lxml
```

### Step 1: Extract Officer Data
```bash
python extract_officers_full.py
```
This creates `new_officer_sheet_YYYYMMDD_HHMMSS.csv` with all extracted data.

### Step 2: Match Document Numbers
```bash
python document_number_matcher.py
```
This creates `fast_document_matches_YYYYMMDD_HHMMSS.xlsx` with matching results.

### Step 3: Create Final Formatted Output
```bash
python fill_officer_address_data.py
```
This creates the final formatted Excel file with Corps styling.

## 📁 File Structure

```
├── extract_officers_full.py          # Data extraction engine
├── document_number_matcher.py        # Fuzzy matching system
├── fill_officer_address_data.py      # Formatting and integration
├── requirements.txt                  # Python dependencies
├── README.md                        # This documentation
├── cordata*.txt                     # Raw corporation data (10 files)
├── npcordata*.txt                   # Raw non-profit data (10 files)
├── Corps 10-2-25.xlsx               # Target company list
└── output/                          # Generated files
    ├── new_officer_sheet_*.csv      # Extracted data
    ├── fast_document_matches_*.xlsx # Matching results
    └── Corps_10-2-25_FORMATTED*.xlsx # Final output
```

## 🔍 Key Technical Decisions

### 1. Fixed-Width Parsing vs. Delimited
**Decision**: Fixed-width parsing
**Rationale**: Raw data uses fixed positions, more reliable than delimiter-based parsing

### 2. Fuzzy Matching Library
**Decision**: RapidFuzz over FuzzyWuzzy
**Rationale**: 10x faster performance, better memory efficiency

### 3. Chunked Processing
**Decision**: Process in 50K record chunks
**Rationale**: Prevents memory overflow with 8M+ records

### 4. Address Formatting
**Decision**: Single-line addresses with no wrapping
**Rationale**: Better readability and data consistency

### 5. Excel Formatting
**Decision**: Corps-style alternating blue/white rows
**Rationale**: Professional appearance matching corporate standards

## 🎨 Output Formatting

The final Excel file includes:
- **Full Data Sheet**: All columns with complete information
- **Corps View Sheet**: Standard 4-column view (Company, Officer, Address, City State Zip)
- **Statistics Sheet**: Processing summary and metrics

### Visual Features
- Alternating blue (#D9E2F3) and white row colors
- Dark blue headers (#4472C4) with white text
- Professional borders and typography
- Auto-adjusted column widths
- Single-line address formatting

## 🔧 Customization Options

### Matching Threshold
```python
matcher = FastDocumentMatcher(match_threshold=80)  # Adjust 0-100
```

### Officer Role Priority
```python
priority_roles = ['CEO', 'PRES', 'CFO', 'COO', 'DIR', 'MGR', 'VP', 'SEC']
```

### Processing Chunk Size
```python
chunk_size = 50000  # Adjust based on available memory
```

## 📊 Performance Metrics

| Operation | Records | Time | Memory |
|-----------|---------|------|--------|
| Data Extraction | 8.1M | 17 min | ~2GB |
| Document Matching | 18.8K | 2 min | ~500MB |
| Formatting | 18.8K | 30 sec | ~100MB |

## 🐛 Known Issues & Solutions

### Issue: Company Name Truncation
**Problem**: First 3 letters missing from company names
**Solution**: Adjusted extraction position from 15 to 12

### Issue: Address Line Wrapping
**Problem**: Multi-line addresses in Excel cells
**Solution**: Removed line breaks and disabled text wrapping

### Issue: Memory Overflow
**Problem**: Processing 8M+ records at once
**Solution**: Implemented chunked processing

## 🔮 Future Enhancements

1. **Web Scraping Integration**: Direct lookup from Bizprofile.net
2. **Real-time Updates**: Incremental processing for new data
3. **API Development**: RESTful API for data access
4. **Machine Learning**: Improved matching algorithms
5. **Data Validation**: Automated quality checks

## 📝 Lessons Learned

1. **Data Quality First**: Always validate field positions before processing
2. **Memory Management**: Chunk large datasets to prevent crashes
3. **User Experience**: Professional formatting matters for adoption
4. **Performance**: Choose libraries based on speed, not just features
5. **Documentation**: Clear instructions enable others to use your work

## 🤝 Contributing

This project demonstrates advanced data processing techniques for corporate data. Feel free to:
- Fork and modify for your own datasets
- Improve matching algorithms
- Add new data sources
- Enhance formatting options

## 📄 License

This project is provided as-is for educational and research purposes. Please ensure compliance with data usage policies when working with corporate information.

---

**Created by**: Vladimir Belony  
**Date**: October 4, 2025  
**Purpose**: Florida Corporation Data Processing & Document Number Matching
