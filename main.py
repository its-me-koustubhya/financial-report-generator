import os
import argparse
from datetime import datetime
from graph.workflow import create_report_workflow

def save_report_to_file(report: str, company_name: str, output_dir: str = "output") -> str:
    """
    Saves the generated report to a markdown file.
    
    Args:
        report: The report content
        company_name: Name of the company analyzed
        output_dir: Directory to save reports
        
    Returns:
        Path to the saved file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_company_name = company_name.replace(" ", "_").replace("/", "_")
    filename = f"{safe_company_name}_report_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)
    
    # Save the report
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return filepath


def generate_report(company_name: str, analysis_focus: str = None, verbose: bool = True) -> dict:
    """
    Generates a financial analysis report for a given company.
    
    Args:
        company_name: Name of the company to analyze
        analysis_focus: Optional specific focus for the analysis
        verbose: Whether to print progress messages
        
    Returns:
        Dictionary containing the final state with the report
    """
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"🚀 Business Report Generator")
        print(f"{'='*70}")
        print(f"📊 Company: {company_name}")
        if analysis_focus:
            print(f"🔍 Focus: {analysis_focus}")
        print(f"{'='*70}\n")
    
    # Create the workflow
    app = create_report_workflow()
    
    # Initial state
    initial_state = {
        "user_input": company_name,
        "analysis_focus": analysis_focus,
        "raw_data": [],
        "data_sources": [],
        "key_metrics": None,
        "insights": [],
        "trends": [],
        "report_sections": None,
        "final_report": "",
        "current_step": "",
        "messages": [],
        "data_collection_attempts": 0,
        "writing_attempts": 0
    }
    
    # Run the workflow
    if verbose:
        print("⏳ Starting report generation workflow...\n")
    
    result = app.invoke(initial_state)
    
    if verbose:
        print(f"\n{'='*70}")
        print("✅ Workflow Completed!")
        print(f"{'='*70}")
        print(f"\n📊 Statistics:")
        print(f"   • Data collection attempts: {result.get('data_collection_attempts', 0)}")
        print(f"   • Writing attempts: {result.get('writing_attempts', 0)}")
        print(f"   • Sources collected: {len(result.get('data_sources', []))}")
        print(f"   • Report length: {len(result.get('final_report', ''))} characters")
        print(f"   • Status: {result.get('current_step', 'unknown')}")
    
    return result


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Generate financial analysis reports using AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
          python main.py "Tesla"
          python main.py "Apple Inc" --focus "Q4 2024 performance"
          python main.py "Microsoft" --no-save
          python main.py "Amazon" --output reports/
        """
    )
    
    parser.add_argument(
        "company",
        type=str,
        help="Name of the company to analyze"
    )
    
    parser.add_argument(
        "--focus",
        type=str,
        default=None,
        help="Specific focus or aspect to analyze (optional)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Output directory for reports (default: output/)"
    )
    
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save report to file, only display"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress messages"
    )
    
    args = parser.parse_args()
    
    try:
        # Generate the report
        result = generate_report(
            company_name=args.company,
            analysis_focus=args.focus,
            verbose=not args.quiet
        )
        
        report = result.get('final_report', '')
        
        # Save to file unless --no-save flag is used
        if not args.no_save and report:
            filepath = save_report_to_file(report, args.company, args.output)
            print(f"\n💾 Report saved to: {filepath}")
        
        # Display report preview
        if not args.quiet:
            print(f"\n{'='*70}")
            print("📄 Report Preview (first 500 characters):")
            print(f"{'='*70}")
            print(report[:500] + "..." if len(report) > 500 else report)
            print(f"{'='*70}\n")
        
        # Exit with success
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        return 1
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())