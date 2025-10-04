import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def fill_corps_columns():
    """Fill empty columns in Corps 10-2-25.xlsx with matched document numbers"""
    
    print("="*80)
    print("FILLING CORPS 10-2-25.XLSX WITH MATCHED DOCUMENT NUMBERS")
    print("="*80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load the original Corps file
    print("\nLoading original Corps 10-2-25.xlsx...")
    try:
        corps_df = pd.read_excel('Corps 10-2-25.xlsx')
        print(f"  [LOADED] {len(corps_df):,} companies from Corps file")
        print(f"  Columns: {list(corps_df.columns)}")
    except Exception as e:
        print(f"Error loading Corps file: {e}")
        return
    
    # Load the matching results
    print("\nLoading matching results...")
    try:
        # Find the most recent matching results file
        import glob
        matching_files = glob.glob('fast_document_matches_*.xlsx')
        if not matching_files:
            print("No matching results found!")
            return
        
        # Get the most recent file
        latest_file = max(matching_files, key=lambda x: x.split('_')[-1].replace('.xlsx', ''))
        print(f"  Using results file: {latest_file}")
        
        matches_df = pd.read_excel(latest_file, sheet_name='Matches')
        print(f"  [LOADED] {len(matches_df):,} matching results")
        print(f"  Columns: {list(matches_df.columns)}")
    except Exception as e:
        print(f"Error loading matching results: {e}")
        return
    
    # Create a mapping from company name to document number
    print("\nCreating company-to-document mapping...")
    company_to_doc = {}
    for _, row in matches_df.iterrows():
        if pd.notna(row['document_number']) and row['document_number'] != '':
            company_to_doc[row['original_company']] = {
                'document_number': row['document_number'],
                'matched_name': row['matched_name'],
                'similarity_score': row['similarity_score'],
                'match_quality': row['match_quality']
            }
    
    print(f"  [MAPPED] {len(company_to_doc):,} companies with document numbers")
    
    # Check what columns exist in Corps file
    print(f"\nOriginal Corps file columns:")
    for i, col in enumerate(corps_df.columns):
        print(f"  {i+1:2d}. {col}")
    
    # Add new columns for document numbers and matching info
    print("\nAdding new columns to Corps file...")
    
    # Initialize new columns
    corps_df['Document_Number'] = ''
    corps_df['Matched_Company_Name'] = ''
    corps_df['Match_Similarity_Score'] = 0
    corps_df['Match_Quality'] = ''
    corps_df['Match_Status'] = 'No Match'
    
    # Fill in the data
    print("Filling in document numbers...")
    matches_found = 0
    
    for idx, row in corps_df.iterrows():
        company_name = row.get('Company', '')
        
        if company_name in company_to_doc:
            match_data = company_to_doc[company_name]
            corps_df.at[idx, 'Document_Number'] = match_data['document_number']
            corps_df.at[idx, 'Matched_Company_Name'] = match_data['matched_name']
            corps_df.at[idx, 'Match_Similarity_Score'] = match_data['similarity_score']
            corps_df.at[idx, 'Match_Quality'] = match_data['match_quality']
            corps_df.at[idx, 'Match_Status'] = 'Matched'
            matches_found += 1
    
    print(f"  [FILLED] {matches_found:,} companies with document numbers")
    
    # Calculate statistics
    total_companies = len(corps_df)
    match_rate = (matches_found / total_companies) * 100 if total_companies > 0 else 0
    
    # Quality breakdown
    quality_counts = corps_df['Match_Quality'].value_counts()
    
    print(f"\nMatch Statistics:")
    print(f"  Total companies: {total_companies:,}")
    print(f"  Matched companies: {matches_found:,}")
    print(f"  Match rate: {match_rate:.1f}%")
    print(f"  Unmatched companies: {total_companies - matches_found:,}")
    
    print(f"\nMatch Quality Breakdown:")
    for quality, count in quality_counts.items():
        if quality != '':
            print(f"  {quality}: {count:,}")
    
    # Save the updated Corps file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'Corps_10-2-25_FILLED_{timestamp}.xlsx'
    
    print(f"\nSaving updated Corps file...")
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main data with filled columns
            corps_df.to_excel(writer, sheet_name='Corps Data', index=False)
            
            # Summary statistics
            summary_data = {
                'Metric': [
                    'Total Companies',
                    'Matched Companies', 
                    'Match Rate (%)',
                    'Exact Matches',
                    'Fuzzy Matches',
                    'No Matches',
                    'Processing Date'
                ],
                'Value': [
                    f"{total_companies:,}",
                    f"{matches_found:,}",
                    f"{match_rate:.1f}%",
                    f"{len(corps_df[corps_df['Match_Quality'] == 'Exact']):,}",
                    f"{len(corps_df[corps_df['Match_Quality'].isin(['Excellent', 'Very Good', 'Good', 'Fair'])]):,}",
                    f"{total_companies - matches_found:,}",
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Show sample of matched companies
            matched_sample = corps_df[corps_df['Match_Status'] == 'Matched'].head(20)
            matched_sample.to_excel(writer, sheet_name='Sample Matches', index=False)
            
            # Auto-adjust column widths
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"  [SAVED] {output_file}")
        
    except Exception as e:
        print(f"Error saving file: {e}")
        return
    
    # Show sample results
    print(f"\nSample matched companies:")
    print("-" * 80)
    sample = corps_df[corps_df['Match_Status'] == 'Matched'].head(10)
    for _, row in sample.iterrows():
        print(f"{row['Company'][:50]:<50} -> {row['Document_Number']} ({row['Match_Similarity_Score']:.0f}%)")
    
    print(f"\n" + "="*80)
    print("CORPS FILE UPDATED SUCCESSFULLY!")
    print("="*80)
    print(f"Output file: {output_file}")
    print(f"Match rate: {match_rate:.1f}%")
    print(f"Ready for use!")
    
    return corps_df

if __name__ == "__main__":
    result = fill_corps_columns()

