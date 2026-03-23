from groq import Groq

# 🔑 PUT YOUR API KEY HERE
client = Groq(api_key="GROQ_API_KEY")


def generate_sql(user_query: str) -> str:
    print("Calling LLM...")

    prompt = f"""
You are a SQL expert.

Use ONLY these tables and columns:

Table: invoices
- invoice_id
- customer_id
- amount

Table: invoice_items
- invoice_id
- product_id
- netAmount
- billingQuantity

Table: deliveries
- delivery_id

Table: payments
- invoice_id
- amount

Rules:
- Only generate SELECT queries
- product_id exists ONLY in invoice_items
- Do NOT assume columns not listed
- Use JOIN properly
- Return ONLY SQL

User Query: {user_query}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            timeout=10  # 🔥 prevents infinite loading
        )

        print("LLM response received")

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("LLM ERROR:", e)
        raise e


# ✅ Guardrails
def is_valid_query(query: str) -> bool:
    query = query.lower()

    blocked = ["drop", "delete", "truncate", "alter", "insert"]
    if any(word in query for word in blocked):
        return False

    return True
