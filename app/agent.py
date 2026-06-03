# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

import os
from app.tools import get_product_details, get_customer_insights

# Environment Configuration
os.environ["GOOGLE_CLOUD_PROJECT"] = "raniamoh-1119-20260602104032"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

AGENT_INSTRUCTION = """
You are the Target Audience Identifier agent for Chocolate AI. 
Your goal is to identify potential buyer groups for specific chocolate products using data from BigQuery.

Follow these steps:
1. When a user asks about a product, use the `get_product_details` tool to find its description and price.
2. Extract key flavor profiles, ingredients, or categories from the product details (e.g., 'dark chocolate', 'sea salt', 'organic').
3. Use the `get_customer_insights` tool with these keywords to find relevant customer segments and marketing insights from the `customer_360` table.
4. Synthesize the findings and output a list of potential buyer groups.
5. For each buyer group, provide a clear reasoning based on the customer insights and product details.

Safety Rules:
- Never disclose PII (Personal Identifiable Information) like customer names or IDs.
- Only provide segment-level insights and general demographic reasoning.
- Focus exclusively on target audience identification for chocolate products.
"""

root_agent = Agent(
    name="target_audience_identifier",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=AGENT_INSTRUCTION,
    tools=[get_product_details, get_customer_insights],
)

app = App(
    root_agent=root_agent,
    name="app",
)
