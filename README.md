# Graph-Based Data Modeling and Query System

## Overview

This project transforms fragmented business data (orders, deliveries, invoices, payments) into a unified graph-based system with a natural language query interface powered by an LLM.

Users can explore relationships between entities and query the system using plain English.

---

## Architecture

### 1. Data Layer

* Source: JSONL files
* Processed using Pandas
* Stored in SQLite database

Tables:

* invoices
* invoice_items
* deliveries
* payments

---

### 2. Graph Modeling

* Nodes: Invoice, Product, Delivery, Customer
* Edges:

  * Invoice → Invoice Items
  * Invoice Items → Product
  * Invoice → Delivery
  * Invoice → Payment

---

### 3. Backend (FastAPI)

* `/query` endpoint
* Accepts natural language queries
* Returns structured results

---

### 4. LLM Integration

* Provider: Groq
* Model: llama-3.1-8b-instant
* Converts natural language → SQL dynamically

---

### 5. Query Pipeline

User Query → LLM → SQL → Clean SQL → Execute → Return Results

---

## Example Queries

* Which products have highest billing?
* Show invoices not linked to payments
* Trace invoice flow

---

## Guardrails

* Only dataset-related queries allowed
* Blocks destructive SQL (DROP, DELETE)
* Cleans LLM output before execution

---

## Tech Stack

* Python
* FastAPI
* SQLite
* Pandas
* Groq LLM API

---

## How to Run

```bash
pip install fastapi uvicorn pandas groq
uvicorn main:app --reload
```

Open:
http://127.0.0.1:8000/docs

---

## Future Improvements

* Graph visualization UI
* Chat interface
* Semantic search
* Conversation memory

---

## Notes

* LLM output is sanitized before execution
* System ensures data-backed responses only
"# Dodge_AI_Assesment" 
