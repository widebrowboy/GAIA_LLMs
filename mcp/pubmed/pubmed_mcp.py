#!/usr/bin/env python3
"""
PubMed MCP Server for GAIA System
Based on gosset-ai/mcps implementation

Provides access to PubMed research database for scientific literature search.
Supports paper search, abstract retrieval, author searches, and related articles.
"""

import asyncio
import json
import os
import logging
import argparse
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
import httpx

# FastMCP imports
try:
    from mcp.server.fastmcp import FastMCP
    from mcp.server.stdio import stdio_server
except ImportError:
    # Fallback if FastMCP is not available
    print("Warning: FastMCP not available. Using basic MCP implementation.")
    FastMCP = None
    stdio_server = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PubMedMCPServer:
    """PubMed MCP Server implementation for accessing scientific literature"""
    
    def __init__(self, server_name: str = "pubmed-mcp"):
        self.server_name = server_name
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.client = None
        self.tool_name = "GAIA-MCP-PubMed"
        self.email = "research@gaia-bt.com"  # Required by NCBI
        
        # Initialize FastMCP if available
        if FastMCP:
            self.app = FastMCP(server_name)
            self._register_tools()
        else:
            self.app = None
            logger.warning("FastMCP not available. Server may not function properly.")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.client = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.client:
            await self.client.aclose()
    
    def _register_tools(self):
        """Register tools with FastMCP if available"""
        if not self.app:
            return
        
        @self.app.tool()
        async def search_pubmed(query: str, max_results: int = 20) -> str:
            """
            Search PubMed articles by query.
            
            Args:
                query: Search query for PubMed articles
                max_results: Maximum number of results to return (default: 20)
                
            Returns:
                JSON string with search results
            """
            return await self.search_pubmed(query, max_results)
        
        @self.app.tool()
        async def get_pubmed_abstract(pmid: str) -> str:
            """
            Get abstract for a specific PubMed article.
            
            Args:
                pmid: PubMed ID of the article
                
            Returns:
                JSON string with article abstract and details
            """
            return await self.get_pubmed_abstract(pmid)
        
        @self.app.tool()
        async def find_by_author(author: str, max_results: int = 15) -> str:
            """
            Find articles by specific author.
            
            Args:
                author: Author name to search for
                max_results: Maximum number of results to return (default: 15)
                
            Returns:
                JSON string with author's publications
            """
            return await self.find_by_author(author, max_results)
        
        @self.app.tool()
        async def get_related_articles(pmid: str, max_results: int = 10) -> str:
            """
            Get articles related to a specific publication.
            
            Args:
                pmid: PubMed ID of the reference article
                max_results: Maximum number of related articles (default: 10)
                
            Returns:
                JSON string with related articles
            """
            return await self.get_related_articles(pmid, max_results)
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to NCBI Entrez API"""
        if not self.client:
            raise RuntimeError("HTTP client not initialized. Use async context manager.")
        
        url = f"{self.base_url}/{endpoint}"
        
        # Add required parameters
        params.update({
            'tool': self.tool_name,
            'email': self.email,
            'retmode': 'json'
        })
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise
    
    async def search_pubmed(self, query: str, max_results: int = 20) -> str:
        """Search PubMed articles by query"""
        try:
            # Step 1: Search for article IDs
            search_params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'sort': 'relevance'
            }
            
            search_result = await self._make_request('esearch.fcgi', search_params)
            
            if not search_result.get('esearchresult', {}).get('idlist'):
                return json.dumps({"error": "No articles found for query", "query": query})
            
            pmids = search_result['esearchresult']['idlist']
            
            # Step 2: Get article summaries
            summary_params = {
                'db': 'pubmed',
                'id': ','.join(pmids)
            }
            
            summary_result = await self._make_request('esummary.fcgi', summary_params)
            
            # Format results
            articles = []
            for pmid in pmids:
                if pmid in summary_result.get('result', {}):
                    article_data = summary_result['result'][pmid]
                    
                    # Extract authors
                    authors = []
                    if 'authors' in article_data:
                        authors = [author['name'] for author in article_data['authors'][:3]]  # First 3 authors
                        if len(article_data['authors']) > 3:
                            authors.append('et al.')
                    
                    article = {
                        'pmid': pmid,
                        'title': article_data.get('title', 'No title'),
                        'authors': authors,
                        'journal': article_data.get('source', 'Unknown journal'),
                        'pub_date': article_data.get('pubdate', 'Unknown date'),
                        'doi': article_data.get('elocationid', '').replace('doi: ', '') if 'doi:' in article_data.get('elocationid', '') else None,
                        'pubmed_url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        'abstract_available': 'hasabstract' in article_data and article_data['hasabstract'] == 1
                    }
                    articles.append(article)
            
            return json.dumps({
                'query': query,
                'total_found': len(articles),
                'articles': articles
            }, indent=2)
        
        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            return json.dumps({"error": f"Failed to search PubMed: {str(e)}"})
    
    async def get_pubmed_abstract(self, pmid: str) -> str:
        """Get abstract for a specific PubMed article"""
        try:
            # Get article details including abstract
            fetch_params = {
                'db': 'pubmed',
                'id': pmid,
                'rettype': 'abstract',
                'retmode': 'text'
            }
            
            # Get abstract in text format
            url = f"{self.base_url}/efetch.fcgi"
            params = {
                'tool': self.tool_name,
                'email': self.email,
                'db': 'pubmed',
                'id': pmid,
                'rettype': 'abstract',
                'retmode': 'text'
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            abstract_text = response.text
            
            # Also get summary for metadata
            summary_params = {
                'db': 'pubmed',
                'id': pmid
            }
            
            summary_result = await self._make_request('esummary.fcgi', summary_params)
            
            if pmid in summary_result.get('result', {}):
                article_data = summary_result['result'][pmid]
                
                # Extract authors
                authors = []
                if 'authors' in article_data:
                    authors = [author['name'] for author in article_data['authors']]
                
                result = {
                    'pmid': pmid,
                    'title': article_data.get('title', 'No title'),
                    'authors': authors,
                    'journal': article_data.get('source', 'Unknown journal'),
                    'pub_date': article_data.get('pubdate', 'Unknown date'),
                    'doi': article_data.get('elocationid', '').replace('doi: ', '') if 'doi:' in article_data.get('elocationid', '') else None,
                    'abstract': abstract_text.strip() if abstract_text.strip() else 'Abstract not available',
                    'pubmed_url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                }
                
                return json.dumps(result, indent=2)
            else:
                return json.dumps({"error": f"Article with PMID {pmid} not found"})
        
        except Exception as e:
            logger.error(f"Error getting abstract: {e}")
            return json.dumps({"error": f"Failed to get abstract: {str(e)}"})
    
    async def find_by_author(self, author: str, max_results: int = 15) -> str:
        """Find articles by specific author"""
        try:
            # Format author query
            author_query = f"{author}[Author]"
            
            return await self.search_pubmed(author_query, max_results)
        
        except Exception as e:
            logger.error(f"Error finding articles by author: {e}")
            return json.dumps({"error": f"Failed to find articles by author: {str(e)}"})
    
    async def get_related_articles(self, pmid: str, max_results: int = 10) -> str:
        """Get articles related to a specific publication"""
        try:
            # Use ELink to find related articles
            link_params = {
                'dbfrom': 'pubmed',
                'db': 'pubmed',
                'id': pmid,
                'cmd': 'neighbor',
                'linkname': 'pubmed_pubmed'
            }
            
            link_result = await self._make_request('elink.fcgi', link_params)
            
            if not link_result.get('linksets'):
                return json.dumps({"error": f"No related articles found for PMID {pmid}"})
            
            # Extract related PMIDs
            related_pmids = []
            for linkset in link_result['linksets']:
                if 'linksetdbs' in linkset:
                    for linksetdb in linkset['linksetdbs']:
                        if 'links' in linksetdb:
                            related_pmids.extend(linksetdb['links'][:max_results])
            
            if not related_pmids:
                return json.dumps({"error": f"No related articles found for PMID {pmid}"})
            
            # Get summaries for related articles
            summary_params = {
                'db': 'pubmed',
                'id': ','.join(map(str, related_pmids[:max_results]))
            }
            
            summary_result = await self._make_request('esummary.fcgi', summary_params)
            
            # Format results
            related_articles = []
            for related_pmid in map(str, related_pmids[:max_results]):
                if related_pmid in summary_result.get('result', {}):
                    article_data = summary_result['result'][related_pmid]
                    
                    authors = []
                    if 'authors' in article_data:
                        authors = [author['name'] for author in article_data['authors'][:3]]
                        if len(article_data['authors']) > 3:
                            authors.append('et al.')
                    
                    article = {
                        'pmid': related_pmid,
                        'title': article_data.get('title', 'No title'),
                        'authors': authors,
                        'journal': article_data.get('source', 'Unknown journal'),
                        'pub_date': article_data.get('pubdate', 'Unknown date'),
                        'pubmed_url': f"https://pubmed.ncbi.nlm.nih.gov/{related_pmid}/"
                    }
                    related_articles.append(article)
            
            return json.dumps({
                'reference_pmid': pmid,
                'total_related': len(related_articles),
                'related_articles': related_articles
            }, indent=2)
        
        except Exception as e:
            logger.error(f"Error getting related articles: {e}")
            return json.dumps({"error": f"Failed to get related articles: {str(e)}"})


async def main():
    """Main function to run the PubMed MCP server"""
    parser = argparse.ArgumentParser(description="PubMed MCP Server")
    parser.add_argument("--name", default="pubmed-mcp", help="Server name")
    parser.add_argument("--working-directory", help="Working directory")
    
    args = parser.parse_args()
    
    if args.working_directory:
        os.chdir(args.working_directory)
    
    if not FastMCP or not stdio_server:
        logger.error("FastMCP or stdio_server not available. Cannot start server.")
        return
    
    # Create and start the server
    async with PubMedMCPServer(args.name) as server:
        logger.info(f"Starting PubMed MCP Server: {args.name}")
        
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await server.app.run(read_stream, write_stream)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise