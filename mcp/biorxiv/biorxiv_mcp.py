#!/usr/bin/env python3
"""
BioRxiv MCP Server for GAIA System
Based on gosset-ai/mcps implementation

Provides access to bioRxiv and medRxiv preprint repositories for AI assistants.
Supports searching recent preprints, finding published versions, and accessing detailed preprint information.
"""

import asyncio
import json
import os
import logging
import argparse
from datetime import datetime, timedelta
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


class BioRxivMCPServer:
    """BioRxiv MCP Server implementation for accessing preprint repositories"""
    
    def __init__(self, server_name: str = "biorxiv-mcp"):
        self.server_name = server_name
        self.base_url = "https://api.biorxiv.org"
        self.client = None
        
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
        async def get_preprint_by_doi(doi: str) -> str:
            """
            Get detailed preprint information by DOI.
            
            Args:
                doi: Digital Object Identifier of the preprint
                
            Returns:
                JSON string with preprint details
            """
            return await self.get_preprint_by_doi(doi)
        
        @self.app.tool()
        async def find_published_version(doi: str) -> str:
            """
            Find published journal version of a preprint.
            
            Args:
                doi: DOI of the preprint to find published version for
                
            Returns:
                JSON string with published version information if found
            """
            return await self.find_published_version(doi)
        
        @self.app.tool()
        async def get_recent_preprints(
            server: str = "biorxiv",
            interval: int = 7,
            limit: int = 30
        ) -> str:
            """
            Get recent preprints from bioRxiv or medRxiv.
            
            Args:
                server: Server to query ('biorxiv' or 'medrxiv')
                interval: Number of days back to search (default: 7)
                limit: Maximum number of results (default: 30)
                
            Returns:
                JSON string with recent preprints
            """
            return await self.get_recent_preprints(server, interval, limit)
        
        @self.app.tool()
        async def search_preprints(
            start_date: str,
            end_date: str,
            server: str = "biorxiv",
            category: Optional[str] = None,
            limit: int = 50
        ) -> str:
            """
            Search preprints by date range and optional category.
            
            Args:
                start_date: Start date in YYYY-MM-DD format
                end_date: End date in YYYY-MM-DD format
                server: Server to query ('biorxiv' or 'medrxiv')
                category: Optional category filter
                limit: Maximum number of results (default: 50)
                
            Returns:
                JSON string with search results
            """
            return await self.search_preprints(start_date, end_date, server, category, limit)
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to BioRxiv API"""
        if not self.client:
            raise RuntimeError("HTTP client not initialized. Use async context manager.")
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = await self.client.get(url, params=params or {})
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
    
    async def get_preprint_by_doi(self, doi: str) -> str:
        """Get detailed preprint information by DOI"""
        try:
            # Remove URL prefix if present
            if doi.startswith("https://doi.org/"):
                doi = doi.replace("https://doi.org/", "")
            elif doi.startswith("doi:"):
                doi = doi.replace("doi:", "")
            
            # BioRxiv API endpoint for DOI lookup
            endpoint = f"details/{doi}"
            result = await self._make_request(endpoint)
            
            # Format the response
            if "collection" in result and result["collection"]:
                preprint = result["collection"][0]
                formatted_result = {
                    "doi": preprint.get("doi"),
                    "title": preprint.get("title"),
                    "authors": preprint.get("authors"),
                    "abstract": preprint.get("abstract"),
                    "published_date": preprint.get("date"),
                    "version": preprint.get("version"),
                    "category": preprint.get("category"),
                    "server": preprint.get("server"),
                    "url": f"https://doi.org/{preprint.get('doi')}"
                }
                return json.dumps(formatted_result, indent=2)
            else:
                return json.dumps({"error": "Preprint not found"})
        
        except Exception as e:
            logger.error(f"Error getting preprint by DOI: {e}")
            return json.dumps({"error": f"Failed to fetch preprint: {str(e)}"})
    
    async def find_published_version(self, doi: str) -> str:
        """Find published journal version of a preprint"""
        try:
            # Remove URL prefix if present
            if doi.startswith("https://doi.org/"):
                doi = doi.replace("https://doi.org/", "")
            elif doi.startswith("doi:"):
                doi = doi.replace("doi:", "")
            
            # BioRxiv API endpoint for published version lookup
            endpoint = f"pub/{doi}"
            result = await self._make_request(endpoint)
            
            # Format the response
            if "messages" in result and result["messages"]:
                published_info = result["messages"][0]
                formatted_result = {
                    "preprint_doi": doi,
                    "published_doi": published_info.get("published_doi"),
                    "journal": published_info.get("journal"),
                    "published_date": published_info.get("published_date"),
                    "crossref_status": published_info.get("status"),
                    "url": f"https://doi.org/{published_info.get('published_doi')}" if published_info.get('published_doi') else None
                }
                return json.dumps(formatted_result, indent=2)
            else:
                return json.dumps({"message": "No published version found", "preprint_doi": doi})
        
        except Exception as e:
            logger.error(f"Error finding published version: {e}")
            return json.dumps({"error": f"Failed to find published version: {str(e)}"})
    
    async def get_recent_preprints(self, server: str = "biorxiv", interval: int = 7, limit: int = 30) -> str:
        """Get recent preprints from bioRxiv or medRxiv"""
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=interval)
            
            # Format dates for API
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # BioRxiv API endpoint for recent preprints
            endpoint = f"details/{server}/{start_date_str}/{end_date_str}"
            result = await self._make_request(endpoint)
            
            # Format the response
            if "collection" in result and result["collection"]:
                preprints = result["collection"][:limit]  # Limit results
                
                formatted_results = []
                for preprint in preprints:
                    formatted_preprint = {
                        "doi": preprint.get("doi"),
                        "title": preprint.get("title"),
                        "authors": preprint.get("authors"),
                        "abstract": preprint.get("abstract", "")[:300] + "..." if preprint.get("abstract", "") and len(preprint.get("abstract", "")) > 300 else preprint.get("abstract", ""),
                        "published_date": preprint.get("date"),
                        "version": preprint.get("version"),
                        "category": preprint.get("category"),
                        "server": preprint.get("server"),
                        "url": f"https://doi.org/{preprint.get('doi')}"
                    }
                    formatted_results.append(formatted_preprint)
                
                return json.dumps({
                    "search_parameters": {
                        "server": server,
                        "start_date": start_date_str,
                        "end_date": end_date_str,
                        "interval_days": interval,
                        "limit": limit
                    },
                    "total_found": len(formatted_results),
                    "preprints": formatted_results
                }, indent=2)
            else:
                return json.dumps({
                    "search_parameters": {
                        "server": server,
                        "start_date": start_date_str,
                        "end_date": end_date_str,
                        "interval_days": interval
                    },
                    "total_found": 0,
                    "preprints": []
                })
        
        except Exception as e:
            logger.error(f"Error getting recent preprints: {e}")
            return json.dumps({"error": f"Failed to fetch recent preprints: {str(e)}"})
    
    async def search_preprints(
        self,
        start_date: str,
        end_date: str,
        server: str = "biorxiv",
        category: Optional[str] = None,
        limit: int = 50
    ) -> str:
        """Search preprints by date range and optional category"""
        try:
            # Validate date format
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                return json.dumps({"error": "Date format must be YYYY-MM-DD"})
            
            # BioRxiv API endpoint for date range search
            endpoint = f"details/{server}/{start_date}/{end_date}"
            
            # Add category filter if specified
            params = {}
            if category:
                params["category"] = category
            
            result = await self._make_request(endpoint, params)
            
            # Format the response
            if "collection" in result and result["collection"]:
                preprints = result["collection"][:limit]  # Limit results
                
                formatted_results = []
                for preprint in preprints:
                    # Filter by category if specified (client-side filtering)
                    if category and category.lower() not in preprint.get("category", "").lower():
                        continue
                    
                    formatted_preprint = {
                        "doi": preprint.get("doi"),
                        "title": preprint.get("title"),
                        "authors": preprint.get("authors"),
                        "abstract": preprint.get("abstract", "")[:300] + "..." if preprint.get("abstract", "") and len(preprint.get("abstract", "")) > 300 else preprint.get("abstract", ""),
                        "published_date": preprint.get("date"),
                        "version": preprint.get("version"),
                        "category": preprint.get("category"),
                        "server": preprint.get("server"),
                        "url": f"https://doi.org/{preprint.get('doi')}"
                    }
                    formatted_results.append(formatted_preprint)
                
                return json.dumps({
                    "search_parameters": {
                        "server": server,
                        "start_date": start_date,
                        "end_date": end_date,
                        "category": category,
                        "limit": limit
                    },
                    "total_found": len(formatted_results),
                    "preprints": formatted_results
                }, indent=2)
            else:
                return json.dumps({
                    "search_parameters": {
                        "server": server,
                        "start_date": start_date,
                        "end_date": end_date,
                        "category": category
                    },
                    "total_found": 0,
                    "preprints": []
                })
        
        except Exception as e:
            logger.error(f"Error searching preprints: {e}")
            return json.dumps({"error": f"Failed to search preprints: {str(e)}"})


async def main():
    """Main function to run the BioRxiv MCP server"""
    parser = argparse.ArgumentParser(description="BioRxiv MCP Server")
    parser.add_argument("--name", default="biorxiv-mcp", help="Server name")
    parser.add_argument("--working-directory", help="Working directory")
    
    args = parser.parse_args()
    
    if args.working_directory:
        os.chdir(args.working_directory)
    
    if not FastMCP or not stdio_server:
        logger.error("FastMCP or stdio_server not available. Cannot start server.")
        return
    
    # Create and start the server
    async with BioRxivMCPServer(args.name) as server:
        logger.info(f"Starting BioRxiv MCP Server: {args.name}")
        
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