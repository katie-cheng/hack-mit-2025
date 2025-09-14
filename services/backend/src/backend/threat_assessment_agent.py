import os
import time
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

try:
    from .threat_models import (
        ThreatAnalysisRequest, ThreatAnalysisResult, ThreatAnalysis, ThreatLevel, 
        ThreatType, ThreatIndicator, WeatherData, GridData, DataSourceStatus, 
        APIError, MockDataConfig
    )
    from .api_clients import (
        OpenWeatherMapClient, EIAClient, PerplexityMCPClient, MockDataClient
    )
except ImportError:
    from threat_models import (
        ThreatAnalysisRequest, ThreatAnalysisResult, ThreatAnalysis, ThreatLevel, 
        ThreatType, ThreatIndicator, WeatherData, GridData, DataSourceStatus, 
        APIError, MockDataConfig
    )
    from api_clients import (
        OpenWeatherMapClient, EIAClient, PerplexityMCPClient, MockDataClient
    )


class ThreatAssessmentAgent:
    """
    The Threat Assessment Agent (The Oracle) - Agent 1 in the AURA system.
    
    Functions as a data-fusion oracle that receives a location, autonomously 
    gathers data from multiple environmental and grid sources, synthesizes them 
    with an LLM, and returns a structured, machine-readable threat assessment.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, mock_config: Optional[MockDataConfig] = None):
        # Mock data configuration (default to using real APIs)
        self.mock_config = mock_config or MockDataConfig(
            use_mock_weather=False,
            use_mock_grid=False
        )
        self.openai_api_key = openai_api_key
        
        # Initialize LLM for data synthesis
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",  # Use GPT-3.5-turbo instead of GPT-4 for broader access
            temperature=0.1,
            api_key=openai_api_key
        ) if openai_api_key else None
        
        # Initialize API clients
        self.weather_client = OpenWeatherMapClient()
        self.grid_client = EIAClient()
        
        # Only initialize Perplexity MCP client if both API keys are available
        perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        if perplexity_key and anthropic_key:
            self.research_client = PerplexityMCPClient(
                api_key=perplexity_key,
                anthropic_api_key=anthropic_key
            )
        else:
            self.research_client = None
            if not perplexity_key:
                print("⚠️ PERPLEXITY_API_KEY not found - research capabilities disabled")
            if not anthropic_key:
                print("⚠️ ANTHROPIC_API_KEY not found - research capabilities disabled")
        
        self.mock_client = MockDataClient()
        
        # Initialize data source status
        self.data_source_status = DataSourceStatus()

    def update_mock_config(self, mock_config: MockDataConfig):
        """Dynamically update the mock data configuration."""
        self.mock_config = mock_config
        print(f"Threat agent mock config updated: weather={self.mock_config.use_mock_weather}, grid={self.mock_config.use_mock_grid}")
    
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
            
            # Gather weather data - prioritize real APIs, fallback to mock only if real API fails
            if request.include_weather:
                try:
                    # Always try real API first
                    async with self.weather_client as client:
                        weather_data = await client.get_current_weather(request.location)
                    raw_data["weather"] = weather_data.dict()
                    print(f"✅ Real weather data retrieved for {request.location}")
                except Exception as e:
                    print(f"⚠️ Real weather API failed: {e}")
                    # Fallback to mock data only if real API fails
                    try:
                        weather_data = self.mock_client.load_mock_weather(self.mock_config.mock_weather_file)
                        raw_data["weather"] = weather_data.dict()
                        print(f"📊 Using mock weather data as fallback")
                    except Exception as mock_e:
                        print(f"❌ Mock weather data also failed: {mock_e}")
                        error = APIError(api_name="weather", error_message=f"Real API: {str(e)}, Mock: {str(mock_e)}")
                        errors.append(error)
                        self.data_source_status.weather_api = False
            
            # Gather grid data - prioritize real APIs, fallback to mock only if real API fails
            if request.include_grid:
                try:
                    # Always try real API first
                    async with self.grid_client as client:
                        grid_data = await self.grid_client.get_grid_data("ERCOT")
                    raw_data["grid"] = grid_data.dict()
                    print(f"✅ Real grid data retrieved for ERCOT")
                except Exception as e:
                    print(f"⚠️ Real grid API failed: {e}")
                    # Fallback to mock data only if real API fails
                    try:
                        grid_data = self.mock_client.load_mock_grid(self.mock_config.mock_grid_file)
                        raw_data["grid"] = grid_data.dict()
                        print(f"📊 Using mock grid data as fallback")
                    except Exception as mock_e:
                        print(f"❌ Mock grid data also failed: {mock_e}")
                        error = APIError(api_name="grid", error_message=f"Real API: {str(e)}, Mock: {str(mock_e)}")
                        errors.append(error)
                        self.data_source_status.grid_api = False
            
            # Gather research data
            if request.include_research and self.llm and self.research_client:
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
        system_prompt = """You are a threat assessment oracle for smart home energy management systems in Austin, TX.

IMPORTANT: Only identify threats when data clearly exceeds these thresholds:
- HEAT_WAVE: Temperature > 95°F (not 71°F!)
- GRID_STRAIN: Demand > 75,000 MW for moderate, > 80,000 MW for high
- POWER_OUTAGE: Only when grid demand > 85,000 MW (near ERCOT's peak)
- ENERGY_SHORTAGE: Only when multiple critical indicators are present

For Austin, TX in September, 71°F is NORMAL COOL WEATHER, not a heat wave.
For ERCOT, 72,962 MW is NORMAL DEMAND, not grid strain.

Be conservative and only identify genuine threats. Most conditions should result in "low" threat level.

Analyze the provided data and return a structured threat assessment with:
1. Overall threat level (low, moderate, high, critical)
2. Specific threat types identified (ONLY if thresholds are exceeded)
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
            # Enhanced synthesis using both LangChain LLM and Perplexity MCP research
            
            # Step 1: Get real-time threat intelligence from Perplexity MCP
            research_intelligence = None
            if research_data:
                # Use existing research data if available
                research_intelligence = research_data
                print(f"🔍 Using provided research data: {research_data[:200]}...")
            else:
                # Gather fresh threat intelligence using MCP client
                try:
                    context = self._build_research_context(weather_data, grid_data)
                    async with self.research_client as client:
                        research_intelligence = await client.research_threats(location, context)
                    print(f"🔍 Perplexity MCP research results: {research_intelligence[:500]}...")
                except Exception as e:
                    print(f"⚠️ Failed to gather threat intelligence: {e}")
                    research_intelligence = "No real-time threat intelligence available"
            
            # Step 2: Enhanced context with real-time intelligence
            enhanced_context = self._build_analysis_context(weather_data, grid_data, research_intelligence, location)
            print(f"🔍 Enhanced context for LLM: {enhanced_context[:300]}...")
            
            # Step 3: Use LangChain LLM for structured analysis
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"""Location: {location}

{enhanced_context}

Please provide a comprehensive threat analysis that follows this JSON format:
{{
    "overall_threat_level": "low|moderate|high|critical",
    "threat_types": ["heat_wave", "grid_strain", "power_outage", "energy_shortage", "combined"],
    "primary_concerns": ["list of main concerns"],
    "recommended_actions": ["list of specific actions"],
    "confidence_score": 0.85,
    "analysis_summary": "Brief summary incorporating real-time intelligence",
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
}}""")
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse LLM response into structured analysis
            analysis_dict = self._parse_llm_response(response.content)
            print(f"🔍 LLM raw response: {response.content[:500]}...")
            print(f"🔍 Parsed analysis dict: {analysis_dict}")
            
            # Enhance analysis with real-time intelligence summary
            if research_intelligence and research_intelligence != "No real-time threat intelligence available":
                analysis_dict["analysis_summary"] = f"{analysis_dict.get('analysis_summary', '')} | Real-time Intelligence: {research_intelligence[:200]}..."
            
            return ThreatAnalysis(**analysis_dict)
            
        except Exception as e:
            print(f"Enhanced LLM synthesis failed: {e}")
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
        
        # Analyze weather data - use more realistic thresholds
        if weather_data:
            temp = weather_data.temperature_f
            if temp > 105:
                indicators.append(ThreatIndicator(
                    indicator_type="temperature",
                    value=temp,
                    threshold=105.0,
                    severity=ThreatLevel.CRITICAL,
                    description=f"Extreme heat: {temp}°F",
                    confidence=0.95
                ))
                threat_types.append(ThreatType.HEAT_WAVE)
                primary_concerns.append("Extreme heat poses health and energy risks")
                recommended_actions.append("Pre-cool home to 68°F")
                recommended_actions.append("Charge battery to 100%")
            elif temp > 100:
                indicators.append(ThreatIndicator(
                    indicator_type="temperature",
                    value=temp,
                    threshold=100.0,
                    severity=ThreatLevel.HIGH,
                    description=f"High temperature: {temp}°F",
                    confidence=0.85
                ))
                threat_types.append(ThreatType.HEAT_WAVE)
                primary_concerns.append("High temperatures increase cooling demand")
                recommended_actions.append("Optimize thermostat settings")
            elif temp > 95:
                indicators.append(ThreatIndicator(
                    indicator_type="temperature",
                    value=temp,
                    threshold=95.0,
                    severity=ThreatLevel.MODERATE,
                    description=f"Warm temperature: {temp}°F",
                    confidence=0.75
                ))
                # Only add heat wave threat for moderate+ temperatures (95°F+)
                threat_types.append(ThreatType.HEAT_WAVE)
                primary_concerns.append("Elevated temperatures may increase cooling demand")
                recommended_actions.append("Monitor cooling systems")
        
        # Analyze grid data - use more realistic thresholds for ERCOT
        if grid_data:
            demand = grid_data.current_demand_mw
            if demand > 85000:  # Near ERCOT's historical peak of ~85,000 MW
                indicators.append(ThreatIndicator(
                    indicator_type="grid_demand",
                    value=demand,
                    threshold=85000,
                    severity=ThreatLevel.CRITICAL,
                    description=f"Critical grid demand: {demand} MW",
                    confidence=0.9
                ))
                threat_types.append(ThreatType.GRID_STRAIN)
                threat_types.append(ThreatType.POWER_OUTAGE)  # High risk of outages at peak demand
                primary_concerns.append("Critical grid demand - emergency conservation needed")
                recommended_actions.append("Maximize battery backup")
                recommended_actions.append("Prepare for potential outages")
            elif demand > 80000:  # High demand threshold
                indicators.append(ThreatIndicator(
                    indicator_type="grid_demand",
                    value=demand,
                    threshold=80000,
                    severity=ThreatLevel.HIGH,
                    description=f"High grid demand: {demand} MW",
                    confidence=0.8
                ))
                threat_types.append(ThreatType.GRID_STRAIN)
                primary_concerns.append("High grid demand may cause strain")
                recommended_actions.append("Prepare for potential grid issues")
                recommended_actions.append("Consider energy trading opportunities")
            elif demand > 75000:  # Moderate demand threshold
                indicators.append(ThreatIndicator(
                    indicator_type="grid_demand",
                    value=demand,
                    threshold=75000,
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
        
        # Remove duplicate threat types and limit to most severe
        threat_types = list(set(threat_types))  # Remove duplicates
        
        # Prioritize threats - only keep the most severe ones
        if len(threat_types) > 2:
            # Sort by severity and keep only top 2
            threat_priority = {
                ThreatType.POWER_OUTAGE: 4,
                ThreatType.GRID_STRAIN: 3, 
                ThreatType.HEAT_WAVE: 2,
                ThreatType.AIR_QUALITY: 1
            }
            threat_types = sorted(threat_types, key=lambda x: threat_priority.get(x, 0), reverse=True)[:2]
        
        # Create analysis summary
        if threat_types:
            analysis_summary = f"Identified {len(threat_types)} threat types: {', '.join([t.value for t in threat_types])}"
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
        """Parse LLM response into analysis dictionary with validation"""
        try:
            import json
            # Try to extract JSON from response
            start_idx = response_content.find('{')
            end_idx = response_content.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response_content[start_idx:end_idx]
                parsed_data = json.loads(json_str)
                
                # Validate and clean the parsed data
                return self._validate_and_clean_analysis(parsed_data)
        except Exception as e:
            print(f"JSON parsing failed: {e}")
        
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
    
    def _validate_and_clean_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean analysis data to match schema"""
        # Valid threat types from enum
        valid_threat_types = {
            "heat_wave", "grid_strain", "power_outage", "energy_shortage", 
            "combined", "wildfire_risk", "air_quality"
        }
        
        # Valid threat levels
        valid_threat_levels = {"low", "moderate", "high", "critical"}
        
        # Clean threat_types
        if "threat_types" in data and isinstance(data["threat_types"], list):
            data["threat_types"] = [
                t for t in data["threat_types"] 
                if isinstance(t, str) and t in valid_threat_types
            ]
        else:
            data["threat_types"] = []
        
        # Clean overall_threat_level
        if "overall_threat_level" not in data or data["overall_threat_level"] not in valid_threat_levels:
            data["overall_threat_level"] = "moderate"
        
        # Clean indicators
        if "indicators" in data and isinstance(data["indicators"], list):
            cleaned_indicators = []
            for indicator in data["indicators"]:
                if isinstance(indicator, dict):
                    cleaned_indicator = self._clean_indicator(indicator)
                    if cleaned_indicator:
                        cleaned_indicators.append(cleaned_indicator)
            data["indicators"] = cleaned_indicators
        else:
            data["indicators"] = []
        
        # Ensure required fields exist with defaults
        data.setdefault("primary_concerns", [])
        data.setdefault("recommended_actions", [])
        data.setdefault("confidence_score", 0.5)
        data.setdefault("analysis_summary", "Analysis completed")
        
        return data
    
    def _clean_indicator(self, indicator: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Clean and validate a single indicator"""
        try:
            # Ensure required fields exist
            if not all(key in indicator for key in ["indicator_type", "value", "threshold", "severity", "description"]):
                return None
            
            # Clean numeric fields
            try:
                value = float(indicator["value"])
                threshold = float(indicator["threshold"])
            except (ValueError, TypeError):
                # Skip indicators with non-numeric values
                return None
            
            # Clean severity
            valid_severities = {"low", "moderate", "high", "critical"}
            severity = indicator.get("severity", "moderate")
            if severity not in valid_severities:
                severity = "moderate"
            
            # Clean confidence
            try:
                confidence = float(indicator.get("confidence", 0.5))
                confidence = max(0.0, min(1.0, confidence))  # Clamp to [0,1]
            except (ValueError, TypeError):
                confidence = 0.5
            
            return {
                "indicator_type": str(indicator["indicator_type"]),
                "value": value,
                "threshold": threshold,
                "severity": severity,
                "description": str(indicator["description"]),
                "confidence": confidence
            }
        except Exception:
            return None
    
    def get_data_source_status(self) -> DataSourceStatus:
        """Get current status of all data sources"""
        return self.data_source_status
    
    def update_mock_config(self, config: MockDataConfig):
        """Update mock data configuration"""
        self.mock_config = config
