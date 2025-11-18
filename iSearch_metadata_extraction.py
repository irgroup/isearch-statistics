"""
ArXiv Metadata Extractor
Extracts license information and metadata from ArXiv papers in iSearch dataset.
"""

import csv
import time
import requests
import re
import os
from bs4 import BeautifulSoup
from typing import List, Tuple, Optional, Dict, Any
from urllib.parse import urljoin


class ArXivMetadataExtractor:
    """Extracts and processes metadata from ArXiv abstract pages."""
    
    # Configuration
    INPUT_PATH = r"D:\User\Ajeeth\Training Courses\license_extraction_v2\iSearchIDs.txt"
    OUTPUT_CSV_PATH = r"D:\User\Ajeeth\Training Courses\license_extraction_v2\arxiv_metadata.csv"
    ABSTRACT_FOLDER = r"D:\User\Ajeeth\Training Courses\license_extraction_v2\abstract_pages"
    DOC_ID_COLUMN = 0
    ABSTRACT_URL_COLUMN = 3
    
    # Processing parameters
    REQUEST_DELAY = 0.5
    REQUEST_TIMEOUT = 15
    CHECKPOINT_INTERVAL = 50
    
    # Document ID range to process
    START_DOC_ID = 60987
    END_DOC_ID = 61041
    
    LICENSE_MAPPINGS = {
        "creativecommons.org/licenses/by/4.0": "CC BY 4.0",
        "creativecommons.org/licenses/by-sa/4.0": "CC BY-SA 4.0", 
        "creativecommons.org/licenses/by-nc-sa/4.0": "CC BY-NC-SA 4.0",
        "creativecommons.org/licenses/by-nc-nd/4.0": "CC BY-NC-ND 4.0",
        "arxiv.org/licenses/nonexclusive-distrib/1.0": "arXiv Non-exclusive",
        "arxiv.org/licenses/assumed-1991-2003": "arXiv Assumed (1991-2003)",
    }
    
    HEADERS = {
        "User-Agent": "Academic-Research-Bot/1.0 (contact: researcher@institution.edu)"
    }
    
    CSV_COLUMNS = [
        "doc_id", "abs_url", "license_url", "license_name", "version",
        "title", "authors", "comments", "subjects", "journal_ref", "related_doi"
    ]

    def __init__(self):
        """Initialize the extractor and ensure required directories exist."""
        os.makedirs(self.ABSTRACT_FOLDER, exist_ok=True)

    def normalize_arxiv_url(self, url: str) -> Optional[str]:
        """Convert various ArXiv URL formats to standard abstract page URL."""
        if not url:
            return None
            
        # Remove PDF extension and normalize
        url = url.replace('.pdf', '').strip()
        
        # Extract paper ID from common ArXiv URL patterns
        patterns = [
            r"arxiv\.org/(?:abs|pdf)/([\d\.]+[a-z]*(?:v\d+)?)",
            r"arxiv\.org/([\d\.]+[a-z]*(?:v\d+)?)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                paper_id = match.group(1)
                return f"https://arxiv.org/abs/{paper_id}"
                
        return None

    def extract_numeric_id(self, doc_id: str) -> Optional[int]:
        """Extract numeric identifier from document ID string."""
        # Handle PN0-prefixed IDs (PN0123456)
        if doc_id.startswith("PN0") and len(doc_id) > 3:
            try:
                return int(doc_id[3:])
            except ValueError:
                pass
                
        # Try direct integer conversion
        try:
            return int(doc_id)
        except ValueError:
            pass
            
        # Extract numbers from mixed-format IDs
        numbers = re.findall(r'\d+', doc_id)
        if numbers:
            try:
                return int(numbers[-1])
            except ValueError:
                pass
                
        return None

    def map_license(self, license_url: str) -> str:
        """Map license URL to standardized license name."""
        if not license_url:
            return "Unknown"
            
        license_url = license_url.lower().strip()
        
        for url_pattern, license_name in self.LICENSE_MAPPINGS.items():
            if url_pattern in license_url:
                return license_name
                
        return "Other/Unmapped"

    def extract_metadata(self, html_content: str) -> Dict[str, Any]:
        """Extract all metadata fields from ArXiv abstract page HTML."""
        soup = BeautifulSoup(html_content, "html.parser")
        
        return {
            "license_url": self._extract_license_url(soup),
            "version": self._extract_version(soup),
            "title": self._extract_title(soup),
            "authors": self._extract_authors(soup),
            "comments": self._extract_comments(soup),
            "subjects": self._extract_subjects(soup),
            "journal_ref": self._extract_journal_ref(soup),
            "related_doi": self._extract_doi(soup),
        }

    def _extract_license_url(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract license URL from page."""
        # Try rel=license attribute first
        license_link = soup.select_one('a[rel="license"]')
        if license_link and license_link.get("href"):
            return self._normalize_url(license_link["href"])
            
        # Fallback: search for licenses in links
        for link in soup.find_all("a", href=True):
            if "/licenses/" in link["href"]:
                return self._normalize_url(link["href"])
                
        return None

    def _normalize_url(self, url: str) -> str:
        """Normalize relative URLs to absolute URLs."""
        if url.startswith("//"):
            return "https:" + url
        elif url.startswith("/"):
            return "https://arxiv.org" + url
        return url

    def _extract_version(self, soup: BeautifulSoup) -> str:
        """Extract latest version number from submission history."""
        history = soup.find("div", class_="submission-history")
        if history:
            versions = re.findall(r'\[v(\d+)\]', history.get_text())
            if versions:
                return f"v{max(versions, key=int)}"
                
        # Fallback: check meta tag
        meta_url = soup.find("meta", property="og:url")
        if meta_url and meta_url.get("content"):
            version_match = re.search(r'v(\d+)', meta_url["content"])
            if version_match:
                return f"v{version_match.group(1)}"
                
        return ""

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract paper title."""
        title_tag = soup.select_one("h1.title")
        if title_tag:
            title = title_tag.get_text(strip=True)
            # Remove "Title:" prefix if present
            if title.lower().startswith("title:"):
                title = title[6:].strip()
            return title
        return ""

    def _extract_authors(self, soup: BeautifulSoup) -> str:
        """Extract author names as comma-separated string."""
        authors_div = soup.find("div", class_="authors")
        if authors_div:
            authors = [a.get_text(strip=True) for a in authors_div.find_all("a")]
            return ", ".join(authors)
        return ""

    def _extract_comments(self, soup: BeautifulSoup) -> str:
        """Extract comments field."""
        comments_td = soup.find("td", class_="comments")
        return comments_td.get_text(strip=True) if comments_td else ""

    def _extract_subjects(self, soup: BeautifulSoup) -> str:
        """Extract subject categories."""
        subjects_td = soup.find("td", class_="subjects")
        return subjects_td.get_text(" ", strip=True) if subjects_td else ""

    def _extract_journal_ref(self, soup: BeautifulSoup) -> str:
        """Extract journal reference."""
        jref_td = soup.find("td", class_="jref")
        return jref_td.get_text(strip=True) if jref_td else ""

    def _extract_doi(self, soup: BeautifulSoup) -> str:
        """Extract related DOI."""
        doi_td = soup.find("td", class_="doi")
        if doi_td:
            doi_link = doi_td.find("a")
            return doi_link.get_text(strip=True) if doi_link else ""
        return ""

    def fetch_abstract_page(self, url: str) -> Optional[str]:
        """Download and return abstract page HTML content."""
        try:
            response = requests.get(
                url, 
                headers=self.HEADERS, 
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    def save_abstract_page(self, html_content: str, doc_id: str) -> bool:
        """Save abstract page HTML to file."""
        try:
            safe_filename = re.sub(r'[<>:"/\\|?*]', '_', doc_id)
            filepath = os.path.join(self.ABSTRACT_FOLDER, f"{safe_filename}.html")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return True
        except Exception as e:
            print(f"Error saving abstract page for {doc_id}: {e}")
            return False

    def load_documents_to_process(self) -> List[Tuple[str, str, int]]:
        """Load and filter documents based on ID range."""
        documents = []
        
        with open(self.INPUT_PATH, "r", encoding='utf-8') as file:
            reader = csv.reader(file, delimiter="\t")
            
            for row in reader:
                if len(row) <= max(self.DOC_ID_COLUMN, self.ABSTRACT_URL_COLUMN):
                    continue
                    
                doc_id = row[self.DOC_ID_COLUMN].strip()
                abs_url = row[self.ABSTRACT_URL_COLUMN].strip()
                
                if not abs_url:
                    continue
                    
                numeric_id = self.extract_numeric_id(doc_id)
                if (numeric_id is not None and 
                    self.START_DOC_ID <= numeric_id <= self.END_DOC_ID):
                    documents.append((doc_id, abs_url, numeric_id))
        
        # Sort by numeric ID for consistent processing
        documents.sort(key=lambda x: x[2])
        return documents

    def create_result_row(self, doc_id: str, abs_url: str, 
                         metadata: Dict[str, Any]) -> Tuple:
        """Create a CSV result row from extracted metadata."""
        license_name = self.map_license(metadata["license_url"])
        
        return (
            doc_id, abs_url,
            metadata["license_url"], license_name, metadata["version"],
            metadata["title"], metadata["authors"], metadata["comments"],
            metadata["subjects"], metadata["journal_ref"], metadata["related_doi"]
        )

    def save_results(self, results: List[Tuple], checkpoint_name: str = "") -> None:
        """Save results to CSV file."""
        file_exists = os.path.exists(self.OUTPUT_CSV_PATH)
        
        with open(self.OUTPUT_CSV_PATH, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            if not file_exists:
                writer.writerow(self.CSV_COLUMNS)
            
            writer.writerows(results)

    def process_documents(self) -> Dict[str, int]:
        """Main processing loop for documents."""
        documents = self.load_documents_to_process()
        
        if not documents:
            print(f"No documents found in range {self.START_DOC_ID}-{self.END_DOC_ID}")
            return {"processed": 0, "successful": 0}
        
        print(f"Processing {len(documents)} documents...")
        
        results = []
        stats = {"processed": 0, "successful": 0}
        
        for i, (doc_id, raw_url, numeric_id) in enumerate(documents, 1):
            abs_url = self.normalize_arxiv_url(raw_url)
            
            if not abs_url:
                results.append(self._create_empty_result(doc_id, raw_url))
                continue
                
            html_content = self.fetch_abstract_page(abs_url)
            
            if html_content:
                metadata = self.extract_metadata(html_content)
                self.save_abstract_page(html_content, doc_id)
                results.append(self.create_result_row(doc_id, abs_url, metadata))
                stats["successful"] += 1
            else:
                results.append(self._create_empty_result(doc_id, abs_url))
                
            stats["processed"] += 1
            
            # Save checkpoint periodically
            if i % self.CHECKPOINT_INTERVAL == 0:
                self.save_results(results, f"checkpoint_{i}")
                results = []
                print(f"Checkpoint: processed {i}/{len(documents)} documents")
            
            time.sleep(self.REQUEST_DELAY)
        
        # Save remaining results
        if results:
            self.save_results(results, "final")
            
        return stats

    def _create_empty_result(self, doc_id: str, abs_url: str) -> Tuple:
        """Create empty result row for failed processing."""
        return (doc_id, abs_url, None, "Unknown", "", "", "", "", "", "", "")

    def run(self) -> None:
        """Execute the complete extraction pipeline."""
        print(f"Starting ArXiv metadata extraction")
        print(f"Document ID range: {self.START_DOC_ID} - {self.END_DOC_ID}")
        print(f"Output: {self.OUTPUT_CSV_PATH}")
        
        start_time = time.time()
        stats = self.process_documents()
        elapsed_time = time.time() - start_time
        
        print(f"\nProcessing completed in {elapsed_time:.1f} seconds")
        print(f"Documents processed: {stats['processed']}")
        print(f"Successful extractions: {stats['successful']}")
        print(f"Success rate: {(stats['successful']/stats['processed'])*100:.1f}%")


def main():
    """Main entry point."""
    extractor = ArXivMetadataExtractor()
    extractor.run()


if __name__ == "__main__":
    main()