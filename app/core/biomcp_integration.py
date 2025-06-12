"""
BiomCP Integration for GAIA Research System

Integrates BiomCP's biomedical research capabilities with GAIA's research pipeline.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger(__name__)


class BiomCPIntegration:
    """Integration layer for BiomCP biomedical research tools"""
    
    def __init__(self, mcp_manager=None):
        """
        Initialize BiomCP integration
        
        Args:
            mcp_manager: Optional MCP manager instance
        """
        self.mcp_manager = mcp_manager
        self.logger = logging.getLogger(__name__)
    
    async def search_biomedical_articles(
        self, 
        query: str, 
        limit: int = 10,
        include_abstracts: bool = True
    ) -> Dict[str, Any]:
        """
        Search biomedical articles using BiomCP
        
        Args:
            query: Search query
            limit: Maximum number of results
            include_abstracts: Whether to include abstracts
            
        Returns:
            Search results with articles and metadata
        """
        try:
            if not self.mcp_manager:
                raise RuntimeError("MCP manager not available")
            
            result = await self.mcp_manager.call_tool(
                client_id="biomcp",
                tool_name="search_articles",
                arguments={
                    "query": query,
                    "limit": limit,
                    "include_abstracts": include_abstracts
                }
            )
            
            return self._process_biomcp_result(result, "article_search")
            
        except Exception as e:
            self.logger.error(f"Error searching biomedical articles: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "results": []
            }
    
    async def search_clinical_trials(
        self,
        condition: str,
        status: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search clinical trials using BiomCP
        
        Args:
            condition: Medical condition or disease
            status: Trial status filter (recruiting, completed, etc.)
            limit: Maximum number of results
            
        Returns:
            Clinical trial search results
        """
        try:
            if not self.mcp_manager:
                raise RuntimeError("MCP manager not available")
            
            arguments = {
                "condition": condition,
                "limit": limit
            }
            
            if status:
                arguments["status"] = status
            
            result = await self.mcp_manager.call_tool(
                client_id="biomcp",
                tool_name="search_trials",
                arguments=arguments
            )
            
            return self._process_biomcp_result(result, "clinical_trial_search")
            
        except Exception as e:
            self.logger.error(f"Error searching clinical trials: {e}")
            return {
                "success": False,
                "error": str(e),
                "condition": condition,
                "results": []
            }
    
    async def search_genetic_variants(
        self,
        gene: str,
        variant_type: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search genetic variants using BiomCP
        
        Args:
            gene: Gene name or identifier
            variant_type: Type of variant (SNP, indel, etc.)
            limit: Maximum number of results
            
        Returns:
            Genetic variant search results
        """
        try:
            if not self.mcp_manager:
                raise RuntimeError("MCP manager not available")
            
            arguments = {
                "gene": gene,
                "limit": limit
            }
            
            if variant_type:
                arguments["variant_type"] = variant_type
            
            result = await self.mcp_manager.call_tool(
                client_id="biomcp",
                tool_name="search_variants",
                arguments=arguments
            )
            
            return self._process_biomcp_result(result, "genetic_variant_search")
            
        except Exception as e:
            self.logger.error(f"Error searching genetic variants: {e}")
            return {
                "success": False,
                "error": str(e),
                "gene": gene,
                "results": []
            }
    
    async def get_article_details(self, article_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific article
        
        Args:
            article_id: Article identifier (PMID, DOI, etc.)
            
        Returns:
            Detailed article information
        """
        try:
            if not self.mcp_manager:
                raise RuntimeError("MCP manager not available")
            
            result = await self.mcp_manager.call_tool(
                client_id="biomcp",
                tool_name="get_article",
                arguments={
                    "article_id": article_id
                }
            )
            
            return self._process_biomcp_result(result, "article_details")
            
        except Exception as e:
            self.logger.error(f"Error getting article details: {e}")
            return {
                "success": False,
                "error": str(e),
                "article_id": article_id
            }
    
    async def get_trial_details(self, trial_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific clinical trial
        
        Args:
            trial_id: Trial identifier (NCT number)
            
        Returns:
            Detailed trial information
        """
        try:
            if not self.mcp_manager:
                raise RuntimeError("MCP manager not available")
            
            result = await self.mcp_manager.call_tool(
                client_id="biomcp",
                tool_name="get_trial",
                arguments={
                    "trial_id": trial_id
                }
            )
            
            return self._process_biomcp_result(result, "trial_details")
            
        except Exception as e:
            self.logger.error(f"Error getting trial details: {e}")
            return {
                "success": False,
                "error": str(e),
                "trial_id": trial_id
            }
    
    async def comprehensive_biomedical_research(
        self,
        topic: str,
        include_articles: bool = True,
        include_trials: bool = True,
        include_variants: bool = False,
        max_results_per_type: int = 5
    ) -> Dict[str, Any]:
        """
        Perform comprehensive biomedical research on a topic
        
        Args:
            topic: Research topic
            include_articles: Whether to search articles
            include_trials: Whether to search clinical trials
            include_variants: Whether to search genetic variants
            max_results_per_type: Maximum results per search type
            
        Returns:
            Comprehensive research results
        """
        results = {
            "topic": topic,
            "timestamp": asyncio.get_event_loop().time(),
            "success": True,
            "data": {}
        }
        
        tasks = []
        
        try:
            # Search articles
            if include_articles:
                tasks.append(
                    self.search_biomedical_articles(topic, limit=max_results_per_type)
                )
            
            # Search clinical trials
            if include_trials:
                tasks.append(
                    self.search_clinical_trials(topic, limit=max_results_per_type)
                )
            
            # Search genetic variants (if topic seems gene-related)
            if include_variants:
                tasks.append(
                    self.search_genetic_variants(topic, limit=max_results_per_type)
                )
            
            # Execute all searches concurrently
            if tasks:
                search_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                if include_articles and len(search_results) > 0:
                    results["data"]["articles"] = search_results[0]
                
                if include_trials:
                    trial_index = 1 if include_articles else 0
                    if len(search_results) > trial_index:
                        results["data"]["trials"] = search_results[trial_index]
                
                if include_variants:
                    variant_index = 0
                    if include_articles:
                        variant_index += 1
                    if include_trials:
                        variant_index += 1
                    
                    if len(search_results) > variant_index:
                        results["data"]["variants"] = search_results[variant_index]
            
            # Generate summary
            results["summary"] = self._generate_research_summary(results["data"])
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive biomedical research: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results
    
    def _process_biomcp_result(self, result: Dict[str, Any], search_type: str) -> Dict[str, Any]:
        """Process BiomCP result into standardized format"""
        if not result or "content" not in result:
            return {
                "success": False,
                "error": "No content in BiomCP result",
                "search_type": search_type,
                "results": []
            }
        
        content = result["content"]
        if not content or len(content) == 0:
            return {
                "success": False,
                "error": "Empty content in BiomCP result",
                "search_type": search_type,
                "results": []
            }
        
        # Extract text content
        text_content = content[0].get("text", "")
        
        try:
            # Try to parse as JSON
            if text_content.strip().startswith('{') or text_content.strip().startswith('['):
                parsed_data = json.loads(text_content)
                return {
                    "success": True,
                    "search_type": search_type,
                    "results": parsed_data if isinstance(parsed_data, list) else [parsed_data]
                }
            else:
                # Return as text result
                return {
                    "success": True,
                    "search_type": search_type,
                    "results": [{"text": text_content}]
                }
        except json.JSONDecodeError:
            # Return as plain text
            return {
                "success": True,
                "search_type": search_type,
                "results": [{"text": text_content}]
            }
    
    def _generate_research_summary(self, data: Dict[str, Any]) -> str:
        """Generate a summary of research results"""
        summary_parts = []
        
        if "articles" in data and data["articles"].get("success"):
            article_count = len(data["articles"].get("results", []))
            summary_parts.append(f"{article_count} 생의학 논문")
        
        if "trials" in data and data["trials"].get("success"):
            trial_count = len(data["trials"].get("results", []))
            summary_parts.append(f"{trial_count} 임상시험")
        
        if "variants" in data and data["variants"].get("success"):
            variant_count = len(data["variants"].get("results", []))
            summary_parts.append(f"{variant_count} 유전자 변이")
        
        if summary_parts:
            return f"검색 완료: {', '.join(summary_parts)}"
        else:
            return "검색 결과가 없습니다."