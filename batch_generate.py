"""
Batch Report Generator
Generate reports for multiple companies at once
"""

from main import generate_report, save_report_to_file

def batch_generate(companies: list, output_dir: str = "output"):
    """
    Generate reports for multiple companies.
    
    Args:
        companies: List of company names
        output_dir: Directory to save reports
    """
    
    print(f"\n{'='*70}")
    print(f"📊 Batch Report Generator")
    print(f"{'='*70}")
    print(f"Companies to analyze: {len(companies)}")
    print(f"{'='*70}\n")
    
    results = []
    
    for i, company in enumerate(companies, 1):
        print(f"\n[{i}/{len(companies)}] Processing: {company}")
        print("-" * 70)
        
        try:
            result = generate_report(company, verbose=False)
            report = result.get('final_report', '')
            
            if report:
                filepath = save_report_to_file(report, company, output_dir)
                print(f"✅ Success: {filepath}")
                results.append({"company": company, "status": "success", "file": filepath})
            else:
                print(f"⚠️  No report generated")
                results.append({"company": company, "status": "no_report"})
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({"company": company, "status": "error", "error": str(e)})
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 Batch Processing Summary")
    print(f"{'='*70}")
    
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = len(results) - successful
    
    print(f"✅ Successful: {successful}/{len(companies)}")
    print(f"❌ Failed: {failed}/{len(companies)}")
    
    if failed > 0:
        print("\nFailed companies:")
        for r in results:
            if r['status'] != 'success':
                print(f"  • {r['company']} - {r['status']}")
    
    print(f"{'='*70}\n")
    
    return results


if __name__ == "__main__":
    # Example: Analyze multiple companies
    companies = [
        "Tesla",
        "Apple Inc",
        "Microsoft",
        "Amazon",
        "Google"
    ]
    
    batch_generate(companies)