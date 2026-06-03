import os
from google.cloud import bigquery

def _get_client():
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    return bigquery.Client(project=project_id)

def query_bigquery(query: str) -> list[dict]:
    """Executes a SQL query against BigQuery and returns results as a list of dictionaries."""
    client = _get_client()
    query_job = client.query(query)
    results = query_job.result()
    return [dict(row) for row in results]

def get_product_details(product_search: str) -> list[dict]:
    """
    Retrieves chocolate product details from the menu based on a search string.
    
    Args:
        product_search: Name or description of the product to search for.
    """
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    query = f"""
        SELECT menu_id, menu_name, menu_description, menu_price
        FROM `{project_id}.chocolate_ai.menu`
        WHERE LOWER(menu_name) LIKE LOWER('%{product_search}%')
        OR LOWER(menu_description) LIKE LOWER('%{product_search}%')
        LIMIT 5
    """
    return query_bigquery(query)

def get_customer_insights(preferences: list[str]) -> list[dict]:
    """
    Retrieves customer segments and marketing insights based on flavor preferences or product types.
    
    Args:
        preferences: A list of keywords like ['dark chocolate', 'sea salt', 'almonds'].
    """
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not preferences:
        return []
        
    # Search in both chocolate_preferences and customer_marketing_insights
    conditions = " OR ".join([
        f"(LOWER(chocolate_preferences) LIKE LOWER('%{pref}%') OR LOWER(customer_marketing_insights) LIKE LOWER('%{pref}%'))" 
        for pref in preferences
    ])
    
    query = f"""
        SELECT 
            customer_marketing_insights, 
            chocolate_preferences, 
            interests, 
            lifestyle, 
            motivations, 
            top_3_favorite_menu_items 
        FROM `{project_id}.chocolate_ai.customer_360`
        WHERE {conditions}
        LIMIT 10
    """
    return query_bigquery(query)
