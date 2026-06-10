import google.auth
from google.auth.transport import requests as google_auth_requests
import os
from google.adk.agents import SequentialAgent, LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset 
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

import vertexai
from google.adk.sessions import VertexAiSessionService
from google.adk.memory import VertexAiMemoryBankService
from google.adk import Runner 
from google.adk.agents import Agent
from google.adk.tools.preload_memory_tool import PreloadMemoryTool


# Configuration
GEMINI_MODEL = "gemini-3.5-flash"
BIGQUERY_MCP_URL = "https://bigquery.googleapis.com/mcp" 
MODEL_LOCATION = "global"
os.environ["GOOGLE_CLOUD_LOCATION"] = MODEL_LOCATION
project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'raniamoh-1119-20260602104032')
product_details=""

print (f"PROJECT_ID = {project_id}")
# Helper function to get BigQuery MCP Toolset
def get_bigquery_mcp_headers(context) -> dict[str, str]:
    credentials, project_id = google.auth.default(
        scopes=["https://www.googleapis.com/auth/bigquery"]
    )
    if not credentials.valid:
        credentials.refresh(google_auth_requests.Request())
    return {
        "Authorization": f"Bearer {credentials.token}",
        "x-goog-user-project": project_id
    }


def get_bigquery_mcp_toolset():
    credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/bigquery"]
    )
    credentials.refresh(google_auth_requests.Request())
    oauth_token = credentials.token
        
    HEADERS_WITH_OAUTH = {
        "Authorization": f"Bearer {oauth_token}",
        "x-goog-user-project": project_id
    }

    tools = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=BIGQUERY_MCP_URL,
            headers=HEADERS_WITH_OAUTH,
            timeout=30.0,          
            sse_read_timeout=300.0
        ),
        header_provider=get_bigquery_mcp_headers
    )
    print("BigQuery MCP Toolset configured.")
    return tools


# 1. Product Search Agent (using BigQuery MCP)
bigquery_tools = get_bigquery_mcp_toolset()
product_search_agent = LlmAgent(
    model=GEMINI_MODEL,

    name="product_search_agent",
    description="Searches product information from BigQuery.",
    instruction=f"""You are an expert at querying product databases in BigQuery in the chocolate_ai database in project {project_id}. Use the available tools to 
                    find product details based on the input criteria.
                    Use the BigQuery toolset to query the product data.  also use the model to think what can be enriched for the product details. Return the enriched product details as a json""",
    tools=[bigquery_tools, PreloadMemoryTool()]
)


# 2. Audience & Category Agent
audience_agent = LlmAgent(
    model=GEMINI_MODEL,
    name="audience_agent",
    description="Identifies target audience and product categories.",
    instruction=f"""Based on the product information and marketing goals, 
                identify the key target audience demographics and relevant product categories in BigQuery in the chocolate_ai database in project {project_id} .
                Use the BigQuery toolset to query the target audience data. Also use the model to be able to identify the categories and the grouping based on the insights and use this categry for the generation of the content later """,
    tools=[bigquery_tools, PreloadMemoryTool()]
)

# 3. Content Generation Agent
#TODO: Add Creative Studio and creative studio mcp for generating the vidoes and placing it on GCS
content_gen_agent = LlmAgent(
    model=GEMINI_MODEL,
    name="content_gen_agent",
    description="Generates marketing campaign content.",
    instruction="""Create compelling marketing copy, ad slogans, and content ideas tailored to the target 
                      audience  category and product details provided. also generate short videos""",
    tools=[bigquery_tools, PreloadMemoryTool()]
)


# 4. Marketing Campaign Orchestrator Agent
root_agent = SequentialAgent(
    name="marketing_campaign_orchestrator",
    description="Orchestrates agents for a marketing campaign.",
    sub_agents=[
        product_search_agent,
        audience_agent,
        content_gen_agent,
    ],
)


def session_service_builder():
  import os
  from google.adk.sessions import VertexAiSessionService

  return VertexAiSessionService(
      project=os.getenv('GOOGLE_CLOUD_PROJECT'),
      location=os.getenv('GOOGLE_CLOUD_LOCATION_RUN', 'us-central1'),
  )


def memory_service_builder():
  import os
  from google.adk.memory import VertexAiMemoryBankService

  return VertexAiMemoryBankService(
      project=os.getenv('GOOGLE_CLOUD_PROJECT'),
      location=os.getenv('GOOGLE_CLOUD_LOCATION_RUN', 'us-central1'),
  )


from vertexai.agent_engines.templates.adk import AdkApp

app = AdkApp(
    agent=root_agent,
    app_name="marketing_campaign_agent",
    session_service_builder=session_service_builder,
    memory_service_builder=memory_service_builder,
    enable_tracing=True,
)
app.name = "marketing_campaign_agent"
app.root_agent = root_agent
app.plugins = []
app.events_compaction_config = None
app.context_cache_config = None
app.resumability_config = None




