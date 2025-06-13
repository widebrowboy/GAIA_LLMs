"""
BioMCP Integration for GAIA Research System

Integrates BioMCP's biomedical research capabilities with GAIA's research pipeline.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger(__name__)


class BioMCPIntegration:
    """Integration layer for BioMCP biomedical research tools"""
    
    def __init__(self, mcp_manager=None):
        """
        Initialize BioMCP integration
        
        Args:
            mcp_manager: Optional MCP manager instance
        """
        self.mcp_manager = mcp_manager
        self.logger = logging.getLogger(__name__)
        
        # Map of server names to their capabilities
        self.server_capabilities = {
            "biomcp": ["search_articles", "search_trials", "search_variants", "get_article", "get_trial"],
            "pubmed-mcp": ["search_pubmed", "get_article_details", "find_related_articles", "search_by_author", "get_citations"],
            "clinicaltrials-mcp": ["search_clinical_trials", "get_trial_details", "search_trials_by_sponsor", "search_trials_by_condition", "get_trial_results"]
        }
    
    async def search_biomedical_articles(
        self, 
        query: str, 
        limit: int = 10,
        include_abstracts: bool = True
    ) -> Dict[str, Any]:
        """
        Search biomedical articles using BioMCP
        
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
            
            # Try pubmed-mcp first for article search
            result = await self.call_tool_safe(
                client_id="pubmed-mcp",
                tool_name="search_pubmed",
                arguments={
                    "query": query,
                    "max_results": limit
                }
            )
            
            # Fallback to biomcp if pubmed-mcp is not available
            if not result:
                self.logger.debug("PubMed MCP not available, falling back to BiomCP")
                result = await self.call_tool_safe(
                    client_id="biomcp",
                    tool_name="search_articles",
                    arguments={
                        "query": query,
                        "limit": limit,
                        "include_abstracts": include_abstracts
                    }
                )
            
            if not result:
                raise RuntimeError("No MCP server available for article search")
            
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
        Search clinical trials using BioMCP
        
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
            
            # Try clinicaltrials-mcp first for trial search
            result = await self.call_tool_safe(
                client_id="clinicaltrials-mcp",
                tool_name="search_clinical_trials",
                arguments={
                    "query": condition,
                    "condition": condition,
                    "status": status,
                    "max_results": limit
                }
            )
            
            # Fallback to biomcp if clinicaltrials-mcp is not available
            if not result:
                self.logger.debug("ClinicalTrials MCP not available, falling back to BiomCP")
                result = await self.call_tool_safe(
                    client_id="biomcp",
                    tool_name="search_trials",
                    arguments=arguments
                )
            
            if not result:
                raise RuntimeError("No MCP server available for trial search")
            
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
        Search genetic variants using BioMCP
        
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
            
            result = await self.call_tool_safe(
                client_id="biomcp",
                tool_name="search_variants",
                arguments=arguments
            )
            
            if not result:
                raise RuntimeError("No MCP server available for variant search")
            
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
            
            # Try pubmed-mcp first for article details
            result = await self.call_tool_safe(
                client_id="pubmed-mcp",
                tool_name="get_article_details",
                arguments={
                    "pmid": article_id
                }
            )
            
            # Fallback to biomcp if pubmed-mcp is not available
            if not result:
                self.logger.debug("PubMed MCP not available, falling back to BiomCP")
                result = await self.call_tool_safe(
                    client_id="biomcp",
                    tool_name="get_article",
                    arguments={
                        "article_id": article_id
                    }
                )
            
            if not result:
                raise RuntimeError("No MCP server available for article details")
            
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
            
            # Try clinicaltrials-mcp first for trial details
            result = await self.call_tool_safe(
                client_id="clinicaltrials-mcp",
                tool_name="get_trial_details",
                arguments={
                    "nct_id": trial_id
                }
            )
            
            # Fallback to biomcp if clinicaltrials-mcp is not available
            if not result:
                self.logger.debug("ClinicalTrials MCP not available, falling back to BiomCP")
                result = await self.call_tool_safe(
                    client_id="biomcp",
                    tool_name="get_trial",
                    arguments={
                        "trial_id": trial_id
                    }
                )
            
            if not result:
                raise RuntimeError("No MCP server available for trial details")
            
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
        """Process BioMCP result into standardized format"""
        if not result or "content" not in result:
            return {
                "success": False,
                "error": "No content in BioMCP result",
                "search_type": search_type,
                "results": []
            }
        
        content = result["content"]
        if not content or len(content) == 0:
            return {
                "success": False,
                "error": "Empty content in BioMCP result",
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
    
    async def deduplicate_research_results(
        self,
        results: List[Dict[str, Any]],
        similarity_threshold: float = 0.85
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicate research results based on similarity
        
        Args:
            results: List of research results
            similarity_threshold: Threshold for considering items as duplicates
            
        Returns:
            Deduplicated list of results
        """
        if not results:
            return []
        
        deduplicated = []
        seen_items = []
        
        for result in results:
            is_duplicate = False
            
            # Check against already seen items
            for seen in seen_items:
                similarity = self._calculate_similarity(result, seen)
                if similarity >= similarity_threshold:
                    # If duplicate, keep the one with higher score or more complete data
                    if self._get_result_score(result) > self._get_result_score(seen):
                        # Replace the seen item with this one
                        deduplicated = [r if r != seen else result for r in deduplicated]
                        seen_items = [s if s != seen else result for s in seen_items]
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                deduplicated.append(result)
                seen_items.append(result)
        
        return deduplicated
    
    def _calculate_similarity(self, item1: Dict[str, Any], item2: Dict[str, Any]) -> float:
        """Calculate similarity between two research items"""
        # Simple similarity based on title/identifier matching
        title1 = str(item1.get("title", "")).lower()
        title2 = str(item2.get("title", "")).lower()
        
        # Check for exact ID matches
        id1 = item1.get("id") or item1.get("pmid") or item1.get("nct_id")
        id2 = item2.get("id") or item2.get("pmid") or item2.get("nct_id")
        
        if id1 and id2 and str(id1) == str(id2):
            return 1.0
        
        # Check title similarity
        if title1 and title2:
            # Simple word overlap similarity
            words1 = set(title1.split())
            words2 = set(title2.split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0.0
        
        return 0.0
    
    def _get_result_score(self, result: Dict[str, Any]) -> float:
        """Calculate a quality score for a research result"""
        score = 0.0
        
        # Score based on data completeness
        if result.get("title"):
            score += 1.0
        if result.get("abstract") or result.get("description"):
            score += 2.0
        if result.get("authors"):
            score += 1.0
        if result.get("year") or result.get("date"):
            score += 0.5
        if result.get("journal") or result.get("source"):
            score += 1.0
        if result.get("doi") or result.get("pmid") or result.get("nct_id"):
            score += 1.5
        
        # Additional score for specific fields
        if result.get("citations_count", 0) > 0:
            score += min(result["citations_count"] / 100, 2.0)
        
        return score
    
    async def call_tool_safe(
        self,
        client_id: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Safely call an MCP tool with error handling
        
        Args:
            client_id: MCP client ID
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool result or None if error
        """
        try:
            if not self.mcp_manager:
                raise RuntimeError("MCP manager not available")
            
            # Use call_mcp_tool instead of call_tool to avoid "Method not implemented" error
            if hasattr(self.mcp_manager, 'call_mcp_tool'):
                result = await self.mcp_manager.call_mcp_tool(
                    server_name=client_id,
                    tool_name=tool_name,
                    arguments=arguments
                )
            else:
                # Fallback to call_tool if call_mcp_tool is not available
                result = await self.mcp_manager.call_tool(
                    client_id=client_id,
                    tool_name=tool_name,
                    arguments=arguments
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error calling tool {tool_name} on {client_id}: {e}")
            return None