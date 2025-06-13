#!/usr/bin/env python3
"""
PubMed MCP Server for GAIA System
Based on gosset-ai/mcps implementation

Provides access to PubMed research database for scientific literature search.
Supports paper search, abstract retrieval, author searches, and related articles.
"""

import os
import sys
from typing import Any, List, Optional
import httpx
from pathlib import Path

# Add the parent directory to sys.path to import from mcp package
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    # Try alternative import path
    try:
        from mcp.server.models import Tool, ToolResult
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        
        # Create a simple FastMCP wrapper
        class FastMCP:
            def __init__(self, name: str, working_dir: str = None):
                self.name = name
                self.working_dir = working_dir
                self.server = Server(name)
                self.tools = []
                
            def tool(self):
                def decorator(func):
                    # Register the tool with the server
                    tool = Tool(
                        name=func.__name__,
                        description=func.__doc__ or "",
                        input_schema={
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    )
                    self.tools.append((tool, func))
                    return func
                return decorator
                
            async def run(self):
                # Run the server
                from mcp.server.stdio import stdio_server
                async with stdio_server() as (read_stream, write_stream):
                    await self.server.run(read_stream, write_stream)
    except ImportError:
        print("Error: Could not import MCP server components")
        sys.exit(1)

# Initialize FastMCP server
mcp = FastMCP("pubmed-mcp", working_dir=str(Path(__file__).parent))

# Constants
ENTREZ_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
DATABASE = "pubmed"
TOOL_NAME = "GAIA-MCP-PubMed"
EMAIL = "research@gaia-bt.com"  # Required by NCBI

async def make_entrez_request(endpoint: str, params: dict, is_json: bool = True) -> Any:
    """Make a request to the Entrez API with proper error handling."""
    url = f"{ENTREZ_BASE_URL}/{endpoint}.fcgi"
    
    # Add required parameters
    params.update({
        "db": DATABASE,
        "tool": TOOL_NAME,
        "email": EMAIL,
    })
    
    if is_json:
        params["retmode"] = "json"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            
            if is_json:
                return response.json()
            return response.text
        except Exception as e:
            return {"error": str(e)} if is_json else f"Error: {str(e)}"

@mcp.tool()
async def search_pubmed(query: str, max_results: int = 10) -> str:
    """Search PubMed for articles matching the query.
    
    Args:
        query: Search query in PubMed syntax
        max_results: Maximum number of results to return (default: 10)
    """
    # First use ESearch to get IDs
    search_params = {
        "term": query,
        "retmax": max_results,
        "sort": "relevance",
        "usehistory": "y"
    }
    
    search_result = await make_entrez_request("esearch", search_params)
    
    if isinstance(search_result, dict) and "error" in search_result:
        return f"Error searching PubMed: {search_result['error']}"
    
    if "esearchresult" not in search_result:
        return "No search results found"
    
    result = search_result["esearchresult"]
    id_list = result.get("idlist", [])
    
    if not id_list:
        return f"No articles found for query: {query}"
    
    # Now fetch summaries for these IDs
    summary_params = {
        "id": ",".join(id_list),
        "retmax": max_results
    }
    
    summary_result = await make_entrez_request("esummary", summary_params)
    
    if isinstance(summary_result, dict) and "error" in summary_result:
        return f"Error fetching summaries: {summary_result['error']}"
    
    # Format the results
    output = [f"Found {result.get('count', 0)} articles (showing top {len(id_list)}):"]
    
    if "result" in summary_result:
        for pmid in id_list:
            if pmid in summary_result["result"]:
                article = summary_result["result"][pmid]
                output.append(f"\n{'-'*60}")
                output.append(f"PMID: {pmid}")
                output.append(f"Title: {article.get('title', 'N/A')}")
                
                # Get authors
                authors = article.get("authors", [])
                if authors:
                    author_names = [f"{a.get('name', '')}" for a in authors[:3]]
                    if len(authors) > 3:
                        author_names.append("et al.")
                    output.append(f"Authors: {', '.join(author_names)}")
                
                output.append(f"Journal: {article.get('source', 'N/A')}")
                output.append(f"Date: {article.get('pubdate', 'N/A')}")
                
                # Add DOI if available
                doi = article.get("elocationid", "")
                if doi and "doi" in doi:
                    output.append(f"DOI: {doi}")
    
    return "\n".join(output)

@mcp.tool()
async def get_article_details(pmid: str) -> str:
    """Get detailed information about a specific PubMed article.
    
    Args:
        pmid: PubMed ID of the article
    """
    # Fetch article details
    params = {
        "id": pmid,
        "rettype": "abstract",
        "retmode": "text"
    }
    
    abstract_text = await make_entrez_request("efetch", params, is_json=False)
    
    if "Error:" in abstract_text:
        return abstract_text
    
    # Also get structured data
    summary_params = {"id": pmid}
    summary_result = await make_entrez_request("esummary", summary_params)
    
    output = [f"Article Details for PMID: {pmid}", "="*60]
    
    # Add structured data if available
    if isinstance(summary_result, dict) and "result" in summary_result and pmid in summary_result["result"]:
        article = summary_result["result"][pmid]
        output.append(f"\nTitle: {article.get('title', 'N/A')}")
        
        # Full author list
        authors = article.get("authors", [])
        if authors:
            author_names = [f"{a.get('name', '')}" for a in authors]
            output.append(f"\nAuthors: {', '.join(author_names)}")
        
        output.append(f"\nJournal: {article.get('source', 'N/A')}")
        output.append(f"Publication Date: {article.get('pubdate', 'N/A')}")
        output.append(f"Volume: {article.get('volume', 'N/A')}, Issue: {article.get('issue', 'N/A')}, Pages: {article.get('pages', 'N/A')}")
        
        # Add identifiers
        output.append(f"\nPMID: {pmid}")
        doi = article.get("elocationid", "")
        if doi:
            output.append(f"DOI: {doi}")
        
        # Add PubMed Central ID if available
        pmc = article.get("pmcid", "")
        if pmc:
            output.append(f"PMC: {pmc}")
    
    # Add abstract
    output.append(f"\n{'='*60}\nAbstract and Full Text:\n{'='*60}\n")
    output.append(abstract_text)
    
    return "\n".join(output)

@mcp.tool()
async def find_related_articles(pmid: str, max_results: int = 10) -> str:
    """Find articles related to a specific PubMed article.
    
    Args:
        pmid: PubMed ID of the reference article
        max_results: Maximum number of related articles to return
    """
    # Use ELink to find related articles
    params = {
        "dbfrom": DATABASE,
        "id": pmid,
        "cmd": "neighbor_score"
    }
    
    link_result = await make_entrez_request("elink", params)
    
    if isinstance(link_result, dict) and "error" in link_result:
        return f"Error finding related articles: {link_result['error']}"
    
    # Extract related PMIDs
    related_ids = []
    if "linksets" in link_result:
        for linkset in link_result["linksets"]:
            if "linksetdbs" in linkset:
                for db in linkset["linksetdbs"]:
                    if db.get("dbto") == DATABASE and "links" in db:
                        related_ids.extend(db["links"][:max_results])
                        break
    
    if not related_ids:
        return f"No related articles found for PMID: {pmid}"
    
    # Fetch summaries for related articles
    summary_params = {
        "id": ",".join(related_ids[:max_results])
    }
    
    summary_result = await make_entrez_request("esummary", summary_params)
    
    output = [f"Related articles for PMID {pmid} (top {len(related_ids)}):"]
    
    if "result" in summary_result:
        for rid in related_ids:
            if rid in summary_result["result"]:
                article = summary_result["result"][rid]
                output.append(f"\n{'-'*40}")
                output.append(f"PMID: {rid}")
                output.append(f"Title: {article.get('title', 'N/A')}")
                
                # Short author list
                authors = article.get("authors", [])
                if authors:
                    first_author = authors[0].get("name", "")
                    if len(authors) > 1:
                        output.append(f"Authors: {first_author} et al.")
                    else:
                        output.append(f"Author: {first_author}")
                
                output.append(f"Journal: {article.get('source', 'N/A')} ({article.get('pubdate', 'N/A')})")
    
    return "\n".join(output)

@mcp.tool()
async def search_by_author(author_name: str, max_results: int = 10) -> str:
    """Search PubMed for articles by a specific author.
    
    Args:
        author_name: Name of the author to search for
        max_results: Maximum number of results to return
    """
    # Format author name for PubMed search
    query = f"{author_name}[Author]"
    return await search_pubmed(query, max_results)

@mcp.tool()
async def get_citations(pmid: str) -> str:
    """Get articles that cite a specific PubMed article.
    
    Args:
        pmid: PubMed ID of the article
    """
    # Use ELink to find citing articles
    params = {
        "dbfrom": DATABASE,
        "linkname": "pubmed_pubmed_citedin",
        "id": pmid
    }
    
    link_result = await make_entrez_request("elink", params)
    
    if isinstance(link_result, dict) and "error" in link_result:
        return f"Error finding citations: {link_result['error']}"
    
    # Extract citing PMIDs
    citing_ids = []
    if "linksets" in link_result:
        for linkset in link_result["linksets"]:
            if "linksetdbs" in linkset:
                for db in linkset["linksetdbs"]:
                    if "links" in db:
                        citing_ids.extend(db["links"])
                        break
    
    if not citing_ids:
        return f"No citations found for PMID: {pmid} (or citation data not available)"
    
    # Limit results
    citing_ids = citing_ids[:20]  # Top 20 citations
    
    # Fetch summaries
    summary_params = {
        "id": ",".join(citing_ids)
    }
    
    summary_result = await make_entrez_request("esummary", summary_params)
    
    output = [f"Articles citing PMID {pmid} (found {len(citing_ids)} citations):"]
    
    if "result" in summary_result:
        for cid in citing_ids:
            if cid in summary_result["result"]:
                article = summary_result["result"][cid]
                output.append(f"\n{'-'*40}")
                output.append(f"PMID: {cid}")
                output.append(f"Title: {article.get('title', 'N/A')}")
                output.append(f"Journal: {article.get('source', 'N/A')} ({article.get('pubdate', 'N/A')})")
    
    return "\n".join(output)

if __name__ == "__main__":
    import asyncio
    
    print(f"Starting PubMed MCP Server...")
    print(f"Server name: {mcp.name}")
    print(f"Working directory: {mcp.working_dir}")
    
    try:
        asyncio.run(mcp.run())
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error running server: {e}")
        sys.exit(1)