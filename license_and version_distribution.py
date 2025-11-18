"""
License and Version Distribution Analyzer
Analyzes distribution patterns in ArXiv metadata extraction results.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from collections import Counter
from typing import Dict, Tuple, List, Any
import os


class LicenseVersionAnalyzer:
    """Analyzes license and version distributions from ArXiv metadata."""
    
    def __init__(self, csv_path: str = "arxiv_metadata.csv", output_dir: str = ".") -> None:
        self.csv_path = csv_path
        self.output_dir = output_dir
        self.df = None
        self.setup_plotting()
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def setup_plotting(self) -> None:
        """Configure matplotlib for consistent styling."""
        plt.style.use('default')
        sns.set_palette("husl")
    
    def load_data(self) -> bool:
        """Load and preprocess the CSV data."""
        try:
            self.df = pd.read_csv(self.csv_path)
            print(f"Loaded dataset with {len(self.df)} records")
            return True
        except FileNotFoundError:
            print(f"Error: File '{self.csv_path}' not found")
            return False
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def preprocess_data(self) -> None:
        """Clean and prepare data for analysis."""
        if self.df is None:
            return
            
        # Clean license names
        self.df['license_name'] = self.df['license_name'].fillna('Unknown')
        self.df['license_name'] = self.df['license_name'].replace('', 'Unknown')
        
        # Clean version data
        self.df['version'] = self.df['version'].fillna('Unknown')
        self.df['version'] = self.df['version'].replace('', 'Unknown')
    
    def get_license_distribution(self) -> Dict[str, int]:
        """Calculate license type distribution."""
        if self.df is None:
            return {}
        
        license_counts = self.df['license_name'].value_counts().to_dict()
        return dict(sorted(license_counts.items(), key=lambda x: x[1], reverse=True))
    
    def get_version_distribution(self) -> Dict[str, int]:
        """Calculate version distribution."""
        if self.df is None:
            return {}
        
        version_counts = self.df['version'].value_counts().to_dict()
        # Sort versions numerically
        return dict(sorted(version_counts.items(), 
                         key=lambda x: int(re.search(r'(\d+)', x[0]).group(1)) if re.search(r'(\d+)', x[0]) else 0))
    
    def generate_summary_statistics(self) -> Dict[str, Any]:
        """Generate comprehensive summary statistics."""
        if self.df is None:
            return {}
        
        total_records = len(self.df)
        valid_licenses = len(self.df[self.df['license_name'] != 'Unknown'])
        valid_versions = len(self.df[self.df['version'] != 'Unknown'])
        
        # Most common licenses
        top_licenses = self.df['license_name'].value_counts().head(5).to_dict()
        
        return {
            'total_records': total_records,
            'records_with_license': valid_licenses,
            'records_with_version': valid_versions,
            'license_coverage': (valid_licenses / total_records) * 100,
            'version_coverage': (valid_versions / total_records) * 100,
            'top_licenses': top_licenses,
        }
    
    def plot_license_distribution(self, save_path: str = None) -> None:
        """Create clean license distribution bar plot."""
        if self.df is None:
            return
        
        license_data = self.get_license_distribution()
        
        plt.figure(figsize=(12, 6))
        
        licenses = list(license_data.keys())
        counts = list(license_data.values())
        
        bars = plt.bar(range(len(licenses)), counts, color='skyblue', edgecolor='black')
        plt.title('License Type Distribution', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('License Type', fontsize=12)
        plt.ylabel('Number of Papers', fontsize=12)
        
        # Set x-axis labels with rotation to prevent overlap
        plt.xticks(range(len(licenses)), licenses, rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{count}', ha='center', va='bottom', fontweight='bold')
        
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            full_path = os.path.join(self.output_dir, save_path)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            print(f"License distribution plot saved to: {full_path}")
        
        plt.show()
    
    def plot_version_distribution(self, save_path: str = None) -> None:
        """Create clean version distribution bar plot."""
        if self.df is None:
            return
        
        version_data = self.get_version_distribution()
        
        # Filter out 'Unknown' for cleaner visualization
        filtered_versions = {k: v for k, v in version_data.items() if k != 'Unknown'}
        
        plt.figure(figsize=(10, 6))
        
        versions = list(filtered_versions.keys())
        counts = list(filtered_versions.values())
        
        bars = plt.bar(range(len(versions)), counts, color='lightcoral', edgecolor='black')
        plt.title('Version Distribution', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Version', fontsize=12)
        plt.ylabel('Number of Papers', fontsize=12)
        plt.xticks(range(len(versions)), versions)
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{count}', ha='center', va='bottom', fontweight='bold')
        
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            full_path = os.path.join(self.output_dir, save_path)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            print(f"Version distribution plot saved to: {full_path}")
        
        plt.show()
    
    def generate_report(self, report_name: str = "analysis_report.txt") -> None:
        """Generate a comprehensive text report."""
        if self.df is None:
            return
        
        summary = self.generate_summary_statistics()
        license_dist = self.get_license_distribution()
        version_dist = self.get_version_distribution()
        
        report_path = os.path.join(self.output_dir, report_name)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("ARXIV LICENSE AND VERSION DISTRIBUTION REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("SUMMARY STATISTICS:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total records analyzed: {summary['total_records']:,}\n")
            f.write(f"Records with license information: {summary['records_with_license']:,}\n")
            f.write(f"Records with version information: {summary['records_with_version']:,}\n")
            f.write(f"License coverage: {summary['license_coverage']:.1f}%\n")
            f.write(f"Version coverage: {summary['version_coverage']:.1f}%\n\n")
            
            f.write("TOP 5 LICENSES:\n")
            f.write("-" * 15 + "\n")
            for license_name, count in summary['top_licenses'].items():
                percentage = (count / summary['total_records']) * 100
                f.write(f"{license_name}: {count:,} ({percentage:.1f}%)\n")
            
            f.write("\nDETAILED LICENSE DISTRIBUTION:\n")
            f.write("-" * 30 + "\n")
            for license_name, count in license_dist.items():
                percentage = (count / summary['total_records']) * 100
                f.write(f"{license_name}: {count:,} ({percentage:.1f}%)\n")
            
            f.write("\nVERSION DISTRIBUTION:\n")
            f.write("-" * 20 + "\n")
            for version, count in version_dist.items():
                percentage = (count / summary['total_records']) * 100
                f.write(f"{version}: {count:,} ({percentage:.1f}%)\n")
            
            f.write(f"\nReport generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"Comprehensive report saved to: {report_path}")
    
    def run_analysis(self) -> None:
        """Run the complete distribution analysis."""
        if not self.load_data():
            return
        
        self.preprocess_data()
        
        # Generate plots
        self.plot_license_distribution("license_distribution.png")
        self.plot_version_distribution("version_distribution.png")
        
        # Generate comprehensive report
        self.generate_report("analysis_report.txt")
        
        # Print summary to console
        summary = self.generate_summary_statistics()
        license_dist = self.get_license_distribution()
        
        print("\n" + "="*50)
        print("ANALYSIS COMPLETED")
        print("="*50)
        print(f"Total records: {summary['total_records']:,}")
        print(f"License coverage: {summary['license_coverage']:.1f}%")
        print(f"Version coverage: {summary['version_coverage']:.1f}%")
        print(f"Most common license: {list(summary['top_licenses'].keys())[0]}")
        print(f"\nOutput files saved to: {self.output_dir}")


def main():
    """Main execution function."""

    input_path = r"D:\User\Ajeeth\Training Courses\license_extraction_v2\iSearch Metadata Collection\arxiv_metadata.csv"
    output_dir = r"D:\User\Ajeeth\Training Courses\license_extraction_v2\iSearch Metadata Collection\result_analysis"
    
    analyzer = LicenseVersionAnalyzer(input_path, output_dir)
    analyzer.run_analysis()


if __name__ == "__main__":
    main()