from groq import Groq

client = Groq(api_key="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")

# Allowed schema
TABLES = {
    "invoices": ["invoice_id", "customer_id", "amount"],
    "invoice_items": ["invoice_id", "product_id", "netAmount", "billingQuantity"],
    "deliveries": ["delivery_id"],
    "payments": ["invoice_id", "amount"]
}

# Allowed SQL keywords for safety
BLOCKED_KEYWORDS = ["drop", "delete", "truncate", "alter", "insert", "update", "merge", "exec", "call", ";"]

def is_valid_query(query: str) -> bool:
    """Check query safety: no blocked keywords and only allowed tables."""
    q_lower = query.lower()
    
    # Block dangerous keywords
    if any(word in q_lower for word in BLOCKED_KEYWORDS):
        return False

    # Block references to tables not in schema
    for word in q_lower.split():
        if word.isidentifier() and word not in TABLES.keys() and word not in ["select", "from", "join", "on", "where", "group", "by", "having", "order", "desc", "asc", "as", "and", "or", "sum", "max", "min", "count"]:
            return False

    return True

def generate_sql(user_query: str) -> str:
    """Generate safe SQL using Groq LLM with explicit schema and guardrails."""
    prompt = f"""
You are a SQL expert.

Only use these tables and columns:
{chr(10).join(f"- {table}: {', '.join(cols)}" for table, cols in TABLES.items())}

Rules:
- Only generate SELECT queries
- Use proper JOINs when necessary
- Return ONLY one valid SQL statement
- Do NOT reference any table or column not listed above
- Do NOT include any text explanation

User Query: {user_query}
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            timeout=10
        )

        sql = response.choices[0].message.content.strip()

        # Extract only the first SELECT statement
        if "select" in sql.lower():
            sql = sql[sql.lower().index("select"):].split("\n")[0]
        else:
            raise ValueError("LLM did not return a SELECT statement")

        if not is_valid_query(sql):
            raise ValueError("Generated query is unsafe or references invalid tables/columns")

        return sql

    except Exception as e:
        print("LLM ERROR:", e)
        raise e