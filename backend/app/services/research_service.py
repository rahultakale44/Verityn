"""Research workflow service."""
import logging
from typing import Optional
from app.models.company import CompanyResponse
from app.models.research import ResearchRunResponse
from app.db.research import (
    create_research_run,
    update_research_run,
    save_source_evidence
)
from app.services.tavily_service import (
    tavily_service,
    TavilyConfigurationError,
    TavilySearchError
)


logger = logging.getLogger(__name__)


class ResearchService:
    """Service for conducting company research."""
    
    def generate_search_queries(self, company: CompanyResponse) -> list[str]:
        """
        Generate search queries based on company information.
        
        Args:
            company: Company record
            
        Returns:
            List of search queries
        """
        queries = []
        
        # Base query with company name
        queries.append(company.company_name)
        
        # Add company name with industry context if available
        if company.industry:
            queries.append(f"{company.company_name} {company.industry}")
        
        # Add company name with location context if available
        if company.headquarters_country:
            location = company.headquarters_country
            if company.headquarters_region:
                location = f"{company.headquarters_region}, {location}"
            queries.append(f"{company.company_name} {location}")
        
        # Add company name with "about" for general information
        queries.append(f"{company.company_name} about company")
        
        # Add website-based query if available
        if company.website:
            queries.append(f"site:{company.website} OR {company.company_name}")
        
        # Limit to 5 queries to keep research bounded
        return queries[:5]
    
    def conduct_research(self, company: CompanyResponse) -> ResearchRunResponse:
        """
        Conduct research for a company.
        
        This is a synchronous, bounded research operation that:
        1. Creates a research run record
        2. Generates search queries
        3. Executes searches via Tavily
        4. Saves source evidence
        5. Updates run status
        
        Args:
            company: Company to research
            
        Returns:
            Completed research run
            
        Raises:
            TavilyConfigurationError: If Tavily API is not configured
        """
        # Create initial research run
        research_run = create_research_run(company.id)
        
        # Update status to running
        research_run = update_research_run(research_run.id, status="running")
        
        queries = []
        sources_found = 0
        sources_saved = 0
        errors = []
        
        try:
            # Generate queries
            queries = self.generate_search_queries(company)
            
            # Execute searches
            for query in queries:
                try:
                    # Search via Tavily
                    results = tavily_service.search(query)
                    
                    # Process results
                    if results and "results" in results:
                        for result in results["results"]:
                            sources_found += 1
                            
                            # Extract source information
                            url = result.get("url", "")
                            title = result.get("title", "Untitled")
                            snippet = result.get("content", "")
                            
                            if not url or not snippet:
                                continue
                            
                            # Published date if available
                            published_at = result.get("published_date")
                            
                            # Save source evidence (returns None if duplicate)
                            saved = save_source_evidence(
                                research_run_id=research_run.id,
                                company_id=company.id,
                                source_url=url,
                                title=title,
                                snippet=snippet,
                                published_at=published_at
                            )
                            
                            if saved:
                                sources_saved += 1
                
                except TavilySearchError as e:
                    logger.warning(f"Search failed for query '{query}': {e}")
                    errors.append(f"Search failed: {str(e)}")
                    continue
            
            # Determine final status
            if sources_saved > 0:
                if errors:
                    status = "partial"
                    error_summary = f"{len(errors)} search(es) failed"
                else:
                    status = "completed"
                    error_summary = None
            else:
                status = "failed"
                error_summary = "No sources collected" if not errors else "; ".join(errors[:2])
            
            # Update research run with final results
            research_run = update_research_run(
                research_run.id,
                status=status,
                queries_executed=len(queries),
                sources_found=sources_found,
                sources_saved=sources_saved,
                error_summary=error_summary
            )
            
        except TavilyConfigurationError:
            # Configuration error - mark as failed
            research_run = update_research_run(
                research_run.id,
                status="failed",
                error_summary="Tavily API not configured"
            )
            raise
        
        except Exception as e:
            # Unexpected error - mark as failed
            logger.error(f"Research failed for company {company.id}: {e}")
            research_run = update_research_run(
                research_run.id,
                status="failed",
                queries_executed=len(queries),
                sources_found=sources_found,
                sources_saved=sources_saved,
                error_summary=f"Research failed: {type(e).__name__}"
            )
            raise
        
        return research_run


# Global service instance
research_service = ResearchService()
