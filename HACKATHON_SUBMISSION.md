# AURA: Intelligent Home Energy Management System
*HackMIT 2025 Submission*

## Inspiration

What inspired you to create this project?

The inspiration came from a pretty straightforward observation: most smart home systems are reactive rather than predictive. We were thinking about how ERCOT's grid instability during extreme weather events could be mitigated if homes could autonomously prepare for these conditions before they become critical.

The real "aha" moment was realizing that the intersection of real-time weather data, grid telemetry, and LLM reasoning could create something genuinely useful - a system that doesn't just respond to problems but anticipates them. We wanted to build something that would actually help people during those brutal Texas heat waves where the grid gets stressed and homes need to be smart about energy consumption.

## What it does

Explain what your project does.

AURA is a multi-agent system that performs real-time threat assessment on environmental conditions and automatically manages smart home energy systems in response. It's essentially a digital twin of your home that can think ahead.

The system continuously monitors weather patterns and ERCOT grid conditions, uses LLM-based synthesis to identify potential threats (heat waves, grid strain, power outages), and then autonomously executes home automation actions like pre-cooling, battery management, and energy trading. It also proactively calls homeowners via voice to inform them of detected threats and get permission for automated responses.

The cool part is that it's not just rule-based - the LLM actually reasons about the data and generates contextually appropriate actions. So instead of "if temperature > 95°F, set AC to 68°F," it's more like "given this specific combination of temperature, humidity, grid demand, and time of day, here's the optimal energy management strategy."

## How we built it

Explain how you built your project.

The architecture is a three-agent system built on FastAPI with a Next.js frontend. The core innovation is in how we structured the agent communication and data flow.

**Threat Assessment Agent (The Oracle)**: This is our data fusion engine. It pulls live data from OpenWeatherMap and ERCOT APIs, then uses GPT-3.5-turbo to synthesize everything into structured threat assessments. The LLM prompt engineering was tricky - we had to be really specific about thresholds and context to avoid false positives.

**Home State Agent (Digital Twin)**: This maintains the complete state of all home devices and executes actions. It's built with LangChain for tool-based reasoning, so the LLM can actually control devices through structured tools rather than just generating text. The validation layer ensures we never set invalid states that could damage equipment.

**Agent Orchestrator**: This coordinates the entire pipeline. It handles the threat-to-action flow, manages registered homeowners, and triggers voice calls via VAPI.ai integration.

The frontend is a real-time dashboard built with Next.js 14 and Tailwind CSS. We implemented a custom design system called "Mercury" that gives it this clean, technical aesthetic.

For the voice integration, we're using VAPI.ai with xAI's Grok model for the actual conversations. The system can have two-way conversations with homeowners, which is pretty wild when you think about it.

## Individual Contributions

Explain how the work was divided among teammates.

We actually built this as a solo project, which meant wearing a lot of hats. The development process was pretty iterative - started with the core agent architecture, then built out the data integration, added the voice system, and finally polished the frontend.

The most time-consuming parts were getting the LLM prompt engineering right for the threat assessment and figuring out the agent communication patterns. The voice integration was surprisingly straightforward once we got the VAPI setup working.

## Challenges we ran into

Explain any challenges you ran into.

The biggest challenge was getting the LLM to be conservative enough with threat detection. Initially, it was flagging normal conditions as threats (like 71°F as a heat wave). We had to be really explicit in the prompts about realistic thresholds and context.

ERCOT's API was also... interesting. Their public endpoints mostly return metadata rather than actual data, so we had to implement a sophisticated fallback system with realistic, time-based mock data that still demonstrates the full pipeline.

The agent communication was another challenge. We experimented with several approaches - uAgents framework, direct LangChain integration, and custom message passing. The final implementation uses a hybrid approach that's both performant and maintainable.

Voice integration had its quirks too. Getting the phone number formatting right for international calls and handling the async nature of voice calls while maintaining the synchronous flow of the rest of the system required some careful orchestration.

## Accomplishments that we're proud of

Explain any accomplishments you're proud of.

The end-to-end pipeline actually works, which is always nice. We can register a homeowner, simulate a heat wave, watch the system detect the threat, generate intelligent actions, execute them on the home state, and make voice calls - all in real-time.

The LLM-based action generation is pretty cool. Instead of hardcoded rules, the system actually reasons about the current state and generates contextually appropriate actions. It's not perfect, but it's surprisingly good at making sensible decisions.

The real-time data integration is solid. We're pulling live weather data and have a robust fallback system for when APIs are unavailable. The system gracefully degrades rather than crashing.

The voice integration is probably the most impressive part. Having an AI system that can actually call people and have conversations about energy management feels like something from the future.

## What we learned

Explain what you learned.

LLM prompt engineering is an art form. Getting the right balance of specificity and flexibility in prompts is crucial for reliable performance. We learned to be very explicit about thresholds and context.

Agent communication patterns are more complex than they initially appear. The choice between synchronous and asynchronous communication, error handling, and state management between agents requires careful consideration.

Real-time data integration is harder than it looks. APIs have rate limits, they go down, they return unexpected data formats. Building robust systems requires thinking about failure modes from the beginning.

Voice AI is surprisingly accessible now. The VAPI integration was much smoother than expected, and the quality of the conversations is genuinely impressive.

## What's next for our project

Given more time, in what ways could you further expand on your project?

The obvious next step would be connecting to actual smart home devices. Right now it's all simulated, but integrating with real thermostats, batteries, and solar inverters would make it genuinely useful.

Machine learning for threat prediction would be interesting. Instead of just analyzing current conditions, we could train models on historical data to predict threats before they materialize.

The energy trading aspect could be expanded. We could integrate with actual energy markets and implement more sophisticated trading strategies based on price predictions and grid conditions.

Multi-home coordination would be cool. If multiple homes in a neighborhood are using AURA, they could coordinate their responses to grid events, potentially providing grid services as a distributed system.

The voice interface could be enhanced with more natural conversation capabilities. Right now it's pretty scripted, but with more sophisticated prompt engineering, it could handle more complex homeowner interactions.

Long-term, this could evolve into a comprehensive home energy management platform that not only responds to threats but optimizes for cost, comfort, and grid stability on an ongoing basis.

---

*Built with Python, FastAPI, Next.js, LangChain, and a healthy dose of curiosity about the future of smart homes.*
