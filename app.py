from fastapi import FastAPI
import pandas as pd
import sqlite3
from pydantic import BaseModel
from llm import generate_sql, is_valid_query

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ✅ FIX thread issue
conn = sqlite3.connect("data.db", check_same_thread=False)

# ✅ Request model
class QueryRequest(BaseModel):
    user_query: str


# ✅ Clean SQL
def clean_sql(raw_sql: str) -> str:
    raw_sql = raw_sql.replace("```sql", "").replace("```", "")

    idx = raw_sql.upper().find("SELECT")
    if idx != -1:
        raw_sql = raw_sql[idx:]

    if ";" in raw_sql:
        raw_sql = raw_sql[:raw_sql.rfind(";") + 1]

    return raw_sql.strip()


# ✅ Validate SQL
def validate_sql(sql: str) -> bool:
    invalid_patterns = [
        "i.product_id",
        "quantity",
        "delivered",
        "received"
    ]
    return not any(pattern in sql for pattern in invalid_patterns)


# ✅ Fallback SQL
def fallback_sql(user_query: str) -> str:
    if "highest" in user_query.lower() and "billing" in user_query.lower():
        return """
        SELECT ii.product_id, SUM(i.amount) AS total_billing
        FROM invoice_items ii
        JOIN invoices i ON ii.invoice_id = i.invoice_id
        GROUP BY ii.product_id
        ORDER BY total_billing DESC;
        """
    return "SELECT * FROM invoices LIMIT 10;"


# ✅ API
@app.post("/query")
def query_data(req: QueryRequest):

    user_query = req.user_query
    print("User Query:", user_query)

    # Guardrail
    if not is_valid_query(user_query):
        return {"error": "Only dataset-related queries allowed"}

    try:
        # 🔥 Try LLM
        try:
            raw_sql = generate_sql(user_query)
        except:
            print("Using fallback SQL...")
            raw_sql = fallback_sql(user_query)

        print("Raw SQL:", raw_sql)

        sql = clean_sql(raw_sql)
        print("Clean SQL:", sql)

        # Validate
        if not validate_sql(sql):
            print("Invalid SQL → using fallback")
            sql = fallback_sql(user_query)

        # Execute
        result = pd.read_sql(sql, conn)

        return {
            "sql": sql,
            "data": result.to_dict(orient="records")
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "error": str(e),
            "hint": "Check SQL or LLM output"
        }