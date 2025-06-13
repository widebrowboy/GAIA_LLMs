#!/usr/bin/env python3
"""
ClinicalTrials.gov MCP Server for GAIA System
Based on gosset-ai/mcps implementation

Provides access to ClinicalTrials.gov database for clinical trial information.
Supports trial search, trial details, and sponsor/condition searches.
"""

import os
import sys
from typing import Any, List, Optional, Dict
import httpx
from pathlib import Path
import json

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
mcp = FastMCP("clinicaltrials-mcp", working_dir=str(Path(__file__).parent))

# Constants
API_BASE_URL = "https://clinicaltrials.gov/api/v2"
TOOL_NAME = "GAIA-MCP-ClinicalTrials"

async def make_api_request(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make a request to the ClinicalTrials.gov API."""
    url = f"{API_BASE_URL}/{endpoint}"
    
    headers = {
        "User-Agent": f"{TOOL_NAME}/1.0"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": f"HTTP error: {str(e)}"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

def format_trial_summary(trial: Dict[str, Any]) -> str:
    """Format a trial summary for display."""
    protocol = trial.get("protocolSection", {})
    id_module = protocol.get("identificationModule", {})
    status_module = protocol.get("statusModule", {})
    desc_module = protocol.get("descriptionModule", {})
    design_module = protocol.get("designModule", {})
    
    output = []
    output.append(f"NCT ID: {id_module.get('nctId', 'N/A')}")
    output.append(f"Title: {id_module.get('briefTitle', 'N/A')}")
    
    # Status info
    output.append(f"Status: {status_module.get('overallStatus', 'N/A')}")
    
    # Study type and phase
    study_type = design_module.get('studyType', 'N/A')
    phases = design_module.get('phases', [])
    output.append(f"Study Type: {study_type}")
    if phases:
        output.append(f"Phase: {', '.join(phases)}")
    
    # Conditions
    conditions_module = protocol.get("conditionsModule", {})
    conditions = conditions_module.get("conditions", [])
    if conditions:
        output.append(f"Conditions: {', '.join(conditions[:3])}")
    
    # Sponsors
    sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
    lead_sponsor = sponsor_module.get("leadSponsor", {})
    if lead_sponsor:
        output.append(f"Lead Sponsor: {lead_sponsor.get('name', 'N/A')}")
    
    # Enrollment
    enrollment_info = design_module.get("enrollmentInfo", {})
    if enrollment_info:
        output.append(f"Enrollment: {enrollment_info.get('count', 'N/A')} ({enrollment_info.get('type', 'N/A')})")
    
    return "\n".join(output)

@mcp.tool()
async def search_clinical_trials(
    query: str,
    condition: Optional[str] = None,
    intervention: Optional[str] = None,
    sponsor: Optional[str] = None,
    status: Optional[str] = None,
    phase: Optional[str] = None,
    max_results: int = 10
) -> str:
    """Search ClinicalTrials.gov for clinical trials.
    
    Args:
        query: General search query
        condition: Medical condition or disease
        intervention: Treatment or intervention type
        sponsor: Trial sponsor name
        status: Trial status (e.g., "RECRUITING", "COMPLETED")
        phase: Trial phase (e.g., "PHASE1", "PHASE2", "PHASE3")
        max_results: Maximum number of results to return
    """
    params = {
        "format": "json",
        "pageSize": max_results,
        "query.term": query
    }
    
    # Add specific filters if provided
    filters = []
    if condition:
        filters.append(f"AREA[Condition]{condition}")
    if intervention:
        filters.append(f"AREA[Intervention]{intervention}")
    if sponsor:
        filters.append(f"AREA[Sponsor]{sponsor}")
    if status:
        filters.append(f"AREA[OverallStatus]{status}")
    if phase:
        filters.append(f"AREA[Phase]{phase}")
    
    if filters:
        params["filter.advanced"] = " AND ".join(filters)
    
    result = await make_api_request("studies", params)
    
    if "error" in result:
        return f"Error searching trials: {result['error']}"
    
    studies = result.get("studies", [])
    total_count = result.get("totalCount", 0)
    
    if not studies:
        return "No clinical trials found matching your criteria."
    
    output = [f"Found {total_count} trials (showing top {len(studies)}):"]
    
    for i, study in enumerate(studies, 1):
        output.append(f"\n{'='*60}")
        output.append(f"Result {i}:")
        output.append(format_trial_summary(study))
    
    return "\n".join(output)

@mcp.tool()
async def get_trial_details(nct_id: str) -> str:
    """Get detailed information about a specific clinical trial.
    
    Args:
        nct_id: NCT identifier (e.g., "NCT12345678")
    """
    # Ensure NCT ID is properly formatted
    if not nct_id.upper().startswith("NCT"):
        nct_id = f"NCT{nct_id}"
    
    result = await make_api_request(f"studies/{nct_id}")
    
    if "error" in result:
        return f"Error fetching trial details: {result['error']}"
    
    if "studies" not in result or not result["studies"]:
        return f"No trial found with NCT ID: {nct_id}"
    
    study = result["studies"][0]
    protocol = study.get("protocolSection", {})
    
    output = [f"Clinical Trial Details: {nct_id}", "="*80]
    
    # Identification
    id_module = protocol.get("identificationModule", {})
    output.append(f"\nTitle: {id_module.get('briefTitle', 'N/A')}")
    official_title = id_module.get("officialTitle")
    if official_title and official_title != id_module.get("briefTitle"):
        output.append(f"Official Title: {official_title}")
    
    # Status
    status_module = protocol.get("statusModule", {})
    output.append(f"\nOverall Status: {status_module.get('overallStatus', 'N/A')}")
    
    start_date = status_module.get("startDateStruct", {})
    if start_date:
        output.append(f"Start Date: {start_date.get('date', 'N/A')}")
    
    completion_date = status_module.get("primaryCompletionDateStruct", {})
    if completion_date:
        output.append(f"Primary Completion Date: {completion_date.get('date', 'N/A')}")
    
    # Description
    desc_module = protocol.get("descriptionModule", {})
    brief_summary = desc_module.get("briefSummary")
    if brief_summary:
        output.append(f"\nBrief Summary:\n{brief_summary}")
    
    # Design
    design_module = protocol.get("designModule", {})
    output.append(f"\nStudy Type: {design_module.get('studyType', 'N/A')}")
    
    phases = design_module.get("phases", [])
    if phases:
        output.append(f"Phase: {', '.join(phases)}")
    
    # Primary purpose
    design_info = design_module.get("designInfo", {})
    if design_info:
        output.append(f"Primary Purpose: {design_info.get('primaryPurpose', 'N/A')}")
        output.append(f"Allocation: {design_info.get('allocation', 'N/A')}")
        output.append(f"Masking: {design_info.get('maskingInfo', {}).get('masking', 'N/A')}")
    
    # Enrollment
    enrollment_info = design_module.get("enrollmentInfo", {})
    if enrollment_info:
        output.append(f"\nEnrollment: {enrollment_info.get('count', 'N/A')} ({enrollment_info.get('type', 'N/A')})")
    
    # Conditions
    conditions_module = protocol.get("conditionsModule", {})
    conditions = conditions_module.get("conditions", [])
    if conditions:
        output.append(f"\nConditions: {', '.join(conditions)}")
    
    # Interventions
    arms_module = protocol.get("armsInterventionsModule", {})
    interventions = arms_module.get("interventions", [])
    if interventions:
        output.append("\nInterventions:")
        for intervention in interventions:
            output.append(f"  - {intervention.get('type', 'N/A')}: {intervention.get('name', 'N/A')}")
            desc = intervention.get("description")
            if desc:
                output.append(f"    Description: {desc[:200]}...")
    
    # Outcomes
    outcomes_module = protocol.get("outcomesModule", {})
    primary_outcomes = outcomes_module.get("primaryOutcomes", [])
    if primary_outcomes:
        output.append("\nPrimary Outcomes:")
        for outcome in primary_outcomes[:3]:
            output.append(f"  - {outcome.get('measure', 'N/A')}")
            time_frame = outcome.get("timeFrame")
            if time_frame:
                output.append(f"    Time Frame: {time_frame}")
    
    # Eligibility
    eligibility_module = protocol.get("eligibilityModule", {})
    if eligibility_module:
        output.append("\nEligibility Criteria:")
        output.append(f"  Ages: {eligibility_module.get('minimumAge', 'N/A')} to {eligibility_module.get('maximumAge', 'N/A')}")
        output.append(f"  Sex: {eligibility_module.get('sex', 'N/A')}")
        output.append(f"  Accepts Healthy Volunteers: {eligibility_module.get('healthyVolunteers', 'N/A')}")
    
    # Sponsors
    sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
    lead_sponsor = sponsor_module.get("leadSponsor", {})
    if lead_sponsor:
        output.append(f"\nLead Sponsor: {lead_sponsor.get('name', 'N/A')} ({lead_sponsor.get('class', 'N/A')})")
    
    collaborators = sponsor_module.get("collaborators", [])
    if collaborators:
        output.append("Collaborators:")
        for collab in collaborators[:3]:
            output.append(f"  - {collab.get('name', 'N/A')}")
    
    # Locations
    locations_module = protocol.get("contactsLocationsModule", {})
    locations = locations_module.get("locations", [])
    if locations:
        output.append(f"\nNumber of Study Locations: {len(locations)}")
        # Show first few locations
        output.append("Sample Locations:")
        for loc in locations[:3]:
            facility = loc.get("facility", "N/A")
            city = loc.get("city", "N/A")
            country = loc.get("country", "N/A")
            output.append(f"  - {facility}, {city}, {country}")
    
    # References
    references_module = protocol.get("referencesModule", {})
    references = references_module.get("references", [])
    if references:
        output.append(f"\nReferences: {len(references)} publications")
    
    return "\n".join(output)

@mcp.tool()
async def search_trials_by_sponsor(sponsor_name: str, max_results: int = 10) -> str:
    """Search for clinical trials by sponsor organization.
    
    Args:
        sponsor_name: Name of the sponsoring organization
        max_results: Maximum number of results to return
    """
    return await search_clinical_trials(
        query=sponsor_name,
        sponsor=sponsor_name,
        max_results=max_results
    )

@mcp.tool()
async def search_trials_by_condition(condition: str, status: Optional[str] = None, max_results: int = 10) -> str:
    """Search for clinical trials by medical condition.
    
    Args:
        condition: Medical condition or disease name
        status: Optional trial status filter (e.g., "RECRUITING")
        max_results: Maximum number of results to return
    """
    return await search_clinical_trials(
        query=condition,
        condition=condition,
        status=status,
        max_results=max_results
    )

@mcp.tool()
async def get_trial_results(nct_id: str) -> str:
    """Get reported results for a clinical trial if available.
    
    Args:
        nct_id: NCT identifier (e.g., "NCT12345678")
    """
    # Ensure NCT ID is properly formatted
    if not nct_id.upper().startswith("NCT"):
        nct_id = f"NCT{nct_id}"
    
    result = await make_api_request(f"studies/{nct_id}")
    
    if "error" in result:
        return f"Error fetching trial results: {result['error']}"
    
    if "studies" not in result or not result["studies"]:
        return f"No trial found with NCT ID: {nct_id}"
    
    study = result["studies"][0]
    
    # Check if results are available
    has_results = study.get("hasResults", False)
    if not has_results:
        return f"No results have been posted for trial {nct_id} yet."
    
    results_section = study.get("resultsSection", {})
    if not results_section:
        return f"Results section not available for trial {nct_id}."
    
    output = [f"Clinical Trial Results: {nct_id}", "="*80]
    
    # Participant flow
    participant_flow = results_section.get("participantFlowModule", {})
    if participant_flow:
        output.append("\nParticipant Flow:")
        groups = participant_flow.get("groups", [])
        for group in groups:
            output.append(f"  {group.get('title', 'N/A')}: {group.get('description', 'N/A')[:100]}...")
    
    # Baseline characteristics
    baseline = results_section.get("baselineCharacteristicsModule", {})
    if baseline:
        output.append("\nBaseline Characteristics:")
        measures = baseline.get("measures", [])
        for measure in measures[:5]:
            output.append(f"  - {measure.get('title', 'N/A')}")
    
    # Outcome measures
    outcome_measures = results_section.get("outcomeMeasuresModule", {})
    if outcome_measures:
        measures = outcome_measures.get("outcomeMeasures", [])
        output.append(f"\nOutcome Measures ({len(measures)} total):")
        
        for measure in measures[:3]:
            output.append(f"\n  {measure.get('title', 'N/A')}")
            output.append(f"    Type: {measure.get('type', 'N/A')}")
            output.append(f"    Time Frame: {measure.get('timeFrame', 'N/A')}")
            
            # Show group results
            groups = measure.get("groups", [])
            if groups:
                output.append("    Results by Group:")
                for group in groups:
                    value = group.get("value", "N/A")
                    output.append(f"      - {group.get('title', 'N/A')}: {value}")
    
    # Adverse events
    adverse_events = results_section.get("adverseEventsModule", {})
    if adverse_events:
        output.append("\nAdverse Events Summary:")
        frequency_threshold = adverse_events.get("frequencyThreshold", "N/A")
        output.append(f"  Frequency Threshold: {frequency_threshold}")
        
        # Serious events
        serious_events = adverse_events.get("seriousEvents", {})
        if serious_events:
            total_serious = sum(group.get("seriousNumAffected", 0) for group in serious_events.get("groups", []))
            output.append(f"  Total Participants with Serious Adverse Events: {total_serious}")
        
        # Other events
        other_events = adverse_events.get("otherEvents", {})
        if other_events:
            total_other = sum(group.get("otherNumAffected", 0) for group in other_events.get("groups", []))
            output.append(f"  Total Participants with Other Adverse Events: {total_other}")
    
    return "\n".join(output)

if __name__ == "__main__":
    import asyncio
    
    print(f"Starting ClinicalTrials.gov MCP Server...")
    print(f"Server name: {mcp.name}")
    print(f"Working directory: {mcp.working_dir}")
    
    try:
        asyncio.run(mcp.run())
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error running server: {e}")
        sys.exit(1)