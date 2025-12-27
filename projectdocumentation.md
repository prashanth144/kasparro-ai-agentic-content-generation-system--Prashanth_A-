# Project Documentation: Kasparro Agentic Content System

**Author:** Prashanth A  
**Project:** Multi-Agent Content Generation System  




## 1. Problem Statement
The challenge is to design a modular, agentic automation system capable of ingesting raw product data (specifically "GlowBoost Vitamin C Serum") and autonomously generating three distinct, machine-readable content pages:
1.  **Product Page** (Structured details, formatted price, safety warnings).
2.  **FAQ Page** (At least 15 categorized Q&A pairs derived from product context).
3.  **Comparison Page** (A comparison between the source product and a generated fictional competitor).

The system must avoid being a simple "GPT Wrapper" script. Instead, it must demonstrate engineering maturity through clear agent boundaries, a custom template engine, reusable logic blocks, and an orchestration graph.



## 2. Solution Overview
I implemented a **Sequential Agentic Pipeline** architecture using Python. The solution moves beyond simple prompting by introducing a strict separation of concerns:

* **Agents** are responsible for "Soft Logic" (reasoning, creativity, drafting).
* **Logic Blocks** are responsible for "Hard Logic" (formatting, safety rules, math).
* **Template Engine** is responsible for "Structure" (assembling the final JSON output).

The orchestrator (`main.py`) coordinates these components, ensuring data flows through a validation layer (Pydantic) before reaching the generative agents, minimizing errors and hallucinations.



## 3. Scopes & Assumptions

### Scopes
* **Input Handling:** The system is optimized for the provided `GlowBoost` dataset schema but uses flexible Pydantic models to allow for future extensibility.
* **Output Format:** All outputs are strictly valid JSON files (`product_page.json`, `faq.json`, `comparison_page.json`).
* **Agent Roles:** Agents are restricted to specific tasks (e.g., The *ContentWriter* cannot generate new facts, only format existing ones).

### Assumptions
* **LLM Availability:** The system assumes access to an OpenAI-compatible API (GPT-4o). A "Mock Mode" is implemented to ensure the pipeline runs successfully even if API keys are missing (returning placeholder text for structural validation).
* **Data Validity:** While the system performs parsing, it assumes the input JSON contains at least the core fields (`Product Name`, `Price`) required for the logic blocks to function.



## 4. System Design (Mandatory)

The system is architected as a **Modular Object-Oriented Pipeline**.

### 4.1 High-Level Architecture
The system follows a linear orchestration flow:
`Ingestion` → `Reasoning & Generation` → `Data Transformation` → `Templating` → `Persistence`

### 4.2 Core Components

#### **A. The Agents (`src/agents.py`)**
These are the autonomous workers, each with a single responsibility:
1.  **`DataIngestionAgent`**:
    * **Responsibility**: Parsing raw, unstructured dictionaries into strict Python objects (`Product` model).
    * **Input**: Raw JSON.
    * **Output**: Validated Pydantic Object.
2.  **`QuestionGenerationAgent`**:
    * **Responsibility**: Creative brainstorming. It analyzes the product features to generate 15 distinct user questions categorized by usage, safety, etc.
3.  **`ContentWriterAgent`**:
    * **Responsibility**: Content drafting. It answers the generated questions using *only* the provided product context (RAG-lite approach).
4.  **`ComparisonAgent`**:
    * **Responsibility**: Competitive analysis. It generates a structured fictional competitor ("Product B") for comparison purposes.

#### **B. Custom Template Engine (`src/engine.py`)**
A custom-built recursive renderer that enforces structure over free-text generation.
* **Variable Injection**: Replaces `{{ name }}` with actual data.
* **Logic Injection**: Detects `{{ BLOCK:function_name }}` tags and executes Python code during rendering. This allows the template to request "formatted prices" or "safety warnings" dynamically.

#### **C. Logic Blocks (`src/logic_blocks.py`)**
Reusable, deterministic functions that run outside the LLM to ensure accuracy.
* `format_currency_block`: Standardizes price strings (e.g., "₹699" → "INR 699").
* `extract_safety_warning_block`: Scans side effects for keywords (e.g., "tingling") to automatically append safety disclaimers.

#### **D. Data Models (`src/models.py`)**
Uses **Pydantic** to define the "Clean Internal Model." This ensures strong typing across the system and prevents "stringly typed" errors.



### 4.3 Automation Flow (Sequence)

mermaid
sequenceDiagram
    participant Main as Orchestrator
    participant Ingest as DataIngestionAgent
    participant QGen as QuestionGenerationAgent
    participant Writer as ContentWriterAgent
    participant Comp as ComparisonAgent
    participant Engine as TemplateEngine

    Main->>Ingest: Parse raw input_data.json
    Ingest-->>Main: Return <Product> Object

    Main->>QGen: Generate 15 Questions(<Product>)
    QGen-->>Main: Return [List of Questions]

    Main->>Writer: Answer FAQs(<Product>, Questions)
    Writer-->>Main: Return [List of Q&A Pairs]

    Main->>Comp: Create Competitor(<Product>)
    Comp-->>Main: Return <CompetitorDict>

    Note over Main, Engine: Final Assembly Phase
    Main->>Engine: Render "Product Page" + Logic Blocks
    Engine-->>Main: Return JSON Structure
    
    Main->>Engine: Render "Comparison Page" + Logic Blocks
    Engine-->>Main: Return JSON Structure

    Main->>FileSystem: Save .json files