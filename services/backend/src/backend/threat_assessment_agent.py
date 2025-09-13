import time
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from threat_models import (
    ThreatAnalysisRequest, ThreatAnalysisResult, ThreatAnalysis, ThreatLevel, 
    ThreatType, ThreatIndicator, WeatherData, GridData, DataSourceStatus, 
    APIError, MockDataConfig
)
from api_clients import (
    OpenWeatherMapClient, EIAClient, PerplexityClient, MockDataClient
)


class ThreatAssessmentAgent:
    """
    The Threat Assessment Agent (The Oracle) - Agent 1 in the AURA system.
    
    Functions as a data-fusion oracle that receives a location, autonomously 
    gathers data from multiple environmental and grid sources, synthesizes them 
    with an LLM, and returns a structured, machine-readable threat assessment.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, mock_config: Optional[MockDataConfig] = None):
        self.openai_api_key = openai_api_key
        self.mock_config = mock_config or MockDataConfig()
        
        # Initialize LLM for data synthesis
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=openai_api_key
        ) if openai_api_key else None
        
        # Initialize API clients
        self.weather_client = OpenWeatherMapClient()
        self.grid_client = EIAClient()
        self.research_client = PerplexityClient()
        self.mock_client = MockDataClient()
        
        # Initialize data source status
        self.data_source_status = DataSourceStatus()
    
    async def analyze_threats(self, request: ThreatAnalysisRequest) -> ThreatAnalysisResult:
        """
        Main entry point for threat analysis.
        Executes the complete data-fusion pipeline.
        """
        start_time = time.time()
        raw_data = {}
        errors = []
        
        try:
            # Step 1: Gather data from all sources
            weather_data = None
            grid_data = None
            research_data = None
            
            # Gather weather data
            if request.include_weather:
                try:
                    if self.mock_config.use_mock_weather:
                        weather_data = self.mock_client.load_mock_weather(self.mock_config.mock_weather_file)
                    else:
                        async with self.weather_client as client:
                            weather_data = await client.get_current_weather(request.location)
                    raw_data["weather"] = weather_data.dict()
                except Exception as e:
                    error = APIError(api_name="weather", error_message=str(e))
                    errors.append(error)
                    self.data_source_status.weather_api = False
            
            # Gather grid data
            if request.include_grid:
                try:
                    if self.mock_config.use_mock_grid:
                        grid_data = self.mock_client.load_mock_grid(self.mock_config.mock_grid_file)
                    else:
                        async with self.grid_client as client:
                            grid_data = await self.grid_client.get_grid_data("ERCOT")
                    raw_data["grid"] = grid_data.dict()
                except Exception as e:
                    error = APIError(api_name="grid", error_message=str(e))
                    errors.append(error)
                    self.data_source_status.grid_api = False
            
            # Gather research data
            if request.include_research and self.llm:
                try:
                    context = self._build_research_context(weather_data, grid_data)
                    async with self.research_client as client:
                        research_data = await client.research_threats(request.location, context)
                    raw_data["research"] = research_data
                except Exception as e:
                    error = APIError(api_name="research", error_message=str(e))
                    errors.append(error)
                    self.data_source_status.research_api = False
            
            # Step 2: Synthesize data using LLM
            analysis = await self._synthesize_threat_analysis(
                weather_data, grid_data, research_data, request.location
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            return ThreatAnalysisResult(
                success=True,
                message=f"Threat analysis completed for {request.location}",
                analysis=analysis,
                raw_data=raw_data,
                request_id=request.request_id,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return ThreatAnalysisResult(
                success=False,
                message=f"Threat analysis failed: {str(e)}",
                analysis=None,
                raw_data=raw_data,
                request_id=request.request_id,
                processing_time_ms=processing_time
            )
    
    async def _synthesize_threat_analysis(
        self, 
        weather_data: Optional[WeatherData], 
        grid_data: Optional[GridData], 
        research_data: Optional[str],
        location: str
    ) -> ThreatAnalysis:
        """
        Synthesize all data sources into a comprehensive threat analysis using LLM.
        """
        if not self.llm:
            # Fallback to rule-based analysis if no LLM
            return self._rule_based_analysis(weather_data, grid_data, location)
        
        # Build context for LLM
        context = self._build_analysis_context(weather_data, grid_data, research_data, location)
        
        # Create system prompt for threat analysis
        system_prompt = """You are a threat assessment oracle for smart home energy management systems.

Your task is to analyze environmental and grid data to assess threats to home energy systems and provide actionable recommendations.

Analyze the provided data and return a structured threat assessment with:
1. Overall threat level (low, moderate, high, critical)
2. Specific threat types identified
3. Primary concerns
4. Recommended actions
5. Confidence score (0.0 to 1.0)
6. Individual threat indicators with severity levels

Focus on threats that could impact:
- Home cooling/heating systems
- Battery backup systems
- Solar panel efficiency
- Grid connectivity and power availability
- Energy costs and trading opportunities

Be specific, actionable, and prioritize based on potential impact and urgency."""

        human_prompt = f"""Location: {location}

{context}

Please provide a comprehensive threat analysis that follows this JSON format, noting this is an example output:
{{
    "overall_threat_level": "low|moderate|high|critical",
    "threat_types": ["heat_wave", "grid_strain", "power_outage", "energy_shortage", "combined"],
    "primary_concerns": ["list of main concerns"],
    "recommended_actions": ["list of specific actions"],
    "confidence_score": 0.85,
    "analysis_summary": "Brief summary of the analysis",
    "indicators": [
        {{
            "indicator_type": "temperature",
            "value": 102.5,
            "threshold": 95.0,
            "severity": "high",
            "description": "Temperature exceeds heat wave threshold",
            "confidence": 0.9
        }}
    ]
}}"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse LLM response
            analysis_dict = self._parse_llm_response(response.content)
            return ThreatAnalysis(**analysis_dict)
            
        except Exception as e:
            print(f"LLM synthesis failed: {e}")
            # Fallback to rule-based analysis
            return self._rule_based_analysis(weather_data, grid_data, location)
    
    def _rule_based_analysis(
        self, 
        weather_data: Optional[WeatherData], 
        grid_data: Optional[GridData], 
        location: str
    ) -> ThreatAnalysis:
        """
        Fallback rule-based threat analysis when LLM is not available.
        """
        indicators = []
        threat_types = []
        primary_concerns = []
        recommended_actions = []
        
        # Analyze weather data
        if weather_data:
            temp = weather_data.temperature_f
            if temp > 100:
                indicators.append(ThreatIndicator(
                    indicator_type="temperature",
                    value=temp,
                    threshold=95.0,
                    severity=ThreatLevel.CRITICAL,
                    description=f"Extreme heat: {temp}°F",
                    confidence=0.95
                ))
                threat_types.append(ThreatType.HEAT_WAVE)
                primary_concerns.append("Extreme heat poses health and energy risks")
                recommended_actions.append("Pre-cool home to 68°F")
                recommended_actions.append("Charge battery to 100%")
            elif temp > 90:
                indicators.append(ThreatIndicator(
                    indicator_type="temperature",
                    value=temp,
                    threshold=85.0,
                    severity=ThreatLevel.HIGH,
                    description=f"High temperature: {temp}°F",
                    confidence=0.85
                ))
                threat_types.append(ThreatType.HEAT_WAVE)
                primary_concerns.append("High temperatures increase cooling demand")
                recommended_actions.append("Optimize thermostat settings")
            elif temp > 80:
                indicators.append(ThreatIndicator(
                    indicator_type="temperature",
                    value=temp,
                    threshold=75.0,
                    severity=ThreatLevel.MODERATE,
                    description=f"Warm temperature: {temp}°F",
                    confidence=0.75
                ))
                threat_types.append(ThreatType.HEAT_WAVE)
                primary_concerns.append("Elevated temperatures may increase cooling demand")
                recommended_actions.append("Monitor cooling systems")
        
        # Analyze grid data
        if grid_data:
            demand = grid_data.current_demand_mw
            if demand > 80000:
                indicators.append(ThreatIndicator(
                    indicator_type="grid_demand",
                    value=demand,
                    threshold=75000,
                    severity=ThreatLevel.CRITICAL,
                    description=f"Critical grid demand: {demand} MW",
                    confidence=0.9
                ))
                threat_types.append(ThreatType.GRID_STRAIN)
                primary_concerns.append("Critical grid demand - emergency conservation needed")
                recommended_actions.append("Maximize battery backup")
                recommended_actions.append("Prepare for potential outages")
            elif demand > 75000:
                indicators.append(ThreatIndicator(
                    indicator_type="grid_demand",
                    value=demand,
                    threshold=70000,
                    severity=ThreatLevel.HIGH,
                    description=f"High grid demand: {demand} MW",
                    confidence=0.8
                ))
                threat_types.append(ThreatType.GRID_STRAIN)
                primary_concerns.append("High grid demand may cause strain")
                recommended_actions.append("Prepare for potential grid issues")
                recommended_actions.append("Consider energy trading opportunities")
            elif demand > 60000:
                indicators.append(ThreatIndicator(
                    indicator_type="grid_demand",
                    value=demand,
                    threshold=50000,
                    severity=ThreatLevel.MODERATE,
                    description=f"Elevated grid demand: {demand} MW",
                    confidence=0.7
                ))
                threat_types.append(ThreatType.GRID_STRAIN)
                primary_concerns.append("Elevated grid demand - monitor for strain")
                recommended_actions.append("Monitor grid stability")
        
        # Determine overall threat level
        if any(ind.severity == ThreatLevel.CRITICAL for ind in indicators):
            overall_threat_level = ThreatLevel.CRITICAL
        elif any(ind.severity == ThreatLevel.HIGH for ind in indicators):
            overall_threat_level = ThreatLevel.HIGH
        elif any(ind.severity == ThreatLevel.MODERATE for ind in indicators):
            overall_threat_level = ThreatLevel.MODERATE
        else:
            overall_threat_level = ThreatLevel.LOW
        
        # Create analysis summary
        if threat_types:
            analysis_summary = f"Identified {len(threat_types)} threat types: {', '.join(threat_types)}"
        else:
            analysis_summary = "No significant threats identified"
        
        return ThreatAnalysis(
            overall_threat_level=overall_threat_level,
            threat_types=threat_types,
            primary_concerns=primary_concerns,
            recommended_actions=recommended_actions,
            confidence_score=0.7,
            analysis_summary=analysis_summary,
            indicators=indicators
        )
    
    def _build_research_context(
        self, 
        weather_data: Optional[WeatherData], 
        grid_data: Optional[GridData]
    ) -> str:
        """Build context string for research API"""
        context_parts = []
        
        if weather_data:
            context_parts.append(f"Weather: {weather_data.temperature_f}°F, {weather_data.condition}")
            if weather_data.nws_alert:
                context_parts.append(f"Alert: {weather_data.nws_alert}")
        
        if grid_data:
            context_parts.append(f"Grid: {grid_data.balancing_authority}, {grid_data.current_demand_mw} MW demand")
            context_parts.append(f"Status: {grid_data.status}")
        
        return "; ".join(context_parts)
    
    def _build_analysis_context(
        self, 
        weather_data: Optional[WeatherData], 
        grid_data: Optional[GridData], 
        research_data: Optional[str],
        location: str
    ) -> str:
        """Build comprehensive context for LLM analysis"""
        context_parts = [f"Location: {location}"]
        
        if weather_data:
            context_parts.append(f"""
Weather Data:
- Temperature: {weather_data.temperature_f}°F
- Condition: {weather_data.condition}
- Humidity: {weather_data.humidity_percent}%
- Wind Speed: {weather_data.wind_speed_mph} mph
- Alert: {weather_data.nws_alert or 'None'}
- Source: {weather_data.source}
- Timestamp: {weather_data.timestamp}
""")
        
        if grid_data:
            context_parts.append(f"""
Grid Data:
- Balancing Authority: {grid_data.balancing_authority}
- Current Demand: {grid_data.current_demand_mw} MW
- Frequency: {grid_data.frequency_hz} Hz
- Status: {grid_data.status}
- Reserve Margin: {grid_data.reserve_margin_mw} MW
- Source: {grid_data.source}
- Timestamp: {grid_data.timestamp_utc}
""")
        
        if research_data:
            context_parts.append(f"""
Research Data:
{research_data}
""")
        
        return "\n".join(context_parts)
    
    def _parse_llm_response(self, response_content: str) -> Dict[str, Any]:
        """Parse LLM response into analysis dictionary"""
        try:
            import json
            # Try to extract JSON from response
            start_idx = response_content.find('{')
            end_idx = response_content.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response_content[start_idx:end_idx]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback: return basic structure
        return {
            "overall_threat_level": "moderate",
            "threat_types": [],
            "primary_concerns": ["Unable to parse LLM response"],
            "recommended_actions": ["Review data manually"],
            "confidence_score": 0.3,
            "analysis_summary": "LLM response parsing failed",
            "indicators": []
        }
    
    def get_data_source_status(self) -> DataSourceStatus:
        """Get current status of all data sources"""
        return self.data_source_status
    
    def update_mock_config(self, config: MockDataConfig):
        """Update mock data configuration"""
        self.mock_config = config
