from mistralai.client import Mistral
from dotenv import load_dotenv
import os
import json
import time
from tools import query_data, execute_code, plot_chart, plot_code
from logger import log_tool_call

load_dotenv()
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

SYSTEM_PROMPT = """You are an expert advertising data analyst.

## Dataset structure
Each row represents a single ad campaign summary with these columns:
- Campaign_ID, Company, Campaign_Type, Target_Audience
- Duration (e.g. "30 days") — the length of the campaign
- Channel_Used — the platform (Facebook, Google Ads, YouTube, Instagram, Email, Website)
- Conversion_Rate, Acquisition_Cost, ROI
- Location — city (Chicago, Houston, Los Angeles, Miami, New York)
- Language, Clicks, Impressions, Engagement_Score, Customer_Segment
- Date — the campaign START date (not a daily measurement)

## What this dataset CAN answer
- Comparisons between platforms, cities, campaign types, audiences
- Trends over time based on campaign start dates
- ROI, CTR (Clicks/Impressions), CPM (Acquisition_Cost/Impressions * 1000), CPC (Acquisition_Cost/Clicks)
- Which segments, languages, or customer types perform best

## What this dataset CANNOT answer
- Time of day or hour analysis (no hourly data)
- Day of week performance (campaigns span multiple days)
- Daily evolution within a single campaign
- Real-time or live metrics

## Rules
1. If a question requires data that doesn't exist in the dataset, say so clearly and suggest what can be answered instead.
2. Always ground your answer in retrieved data — never guess numbers.
3. Use query_data to fetch relevant data first.
4. Use execute_code for statistical analysis or custom calculations.
5. Use plot_code to create interactive plotly charts — always prefer HTML over PNG.
6. Summarise findings clearly in plain English with concrete numbers.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "inspect_dataset",
            "description": (
                "Use this FIRST before any analysis to understand the dataset. "
                "Returns column names, data types, shape, and 3 sample rows. "
                "Do NOT use this to fetch specific data or answer questions — use execute_code for that."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Plain-English description of the data you want."
                    }
                },
                "required": ["question"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_code",
            "description": (
                "Execute Python code for statistical analysis. The dataframe is available as `df`. Assign your final result to `result`."
                "Use this for any calculations, groupings, or data manipulations needed to answer the question. "
                "If more than 20 it will save the full result to a JSON file and return a preview instead. "
                "Don't be afraid to use more times to provide better answers, e.g. one code execution to filter data, then another to calculate stats."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute. Must assign output to `result`."
                    }
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "plot_chart",
            "description": "Create a chart from data and save it as a PNG.",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "List of dicts to plot."
                    },
                    "chart_type": {
                        "type": "string",
                        "enum": ["bar", "line", "scatter", "pie"]
                    },
                    "x": {"type": "string", "description": "Key for x-axis."},
                    "y": {"type": "string", "description": "Key for y-axis."},
                    "title": {"type": "string", "description": "Chart title."}
                },
                "required": ["data", "chart_type", "x", "y", "title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "plot_code",
            "description": (
                "Create an interactive or static chart by writing Python code. "
                "Prefer plotly (px, go) for interactive HTML charts with zoom and hover. "
                "Fallback to seaborn (sns) or matplotlib (plt) for static PNG charts. "

                "The dataframe is available as `df`. "

                "IMPORTANT: If `queried_data_path` is provided, the JSON file is automatically loaded "
                "before code execution and made available as `saved_data`. "
                "To use it, convert with `pd.DataFrame(saved_data)`. "
                "NEVER load files manually. NEVER use open(). "

                "For plotly figures: use `fig.write_html(filepath)`. "
                "For matplotlib: use `plt.savefig(filepath_png, dpi=150, bbox_inches='tight'); plt.close()`. "
                "For custom HTML dashboards: build the HTML as a string and save with "
                "`filepath.write_text(html_string, encoding='utf-8')`. "

                "The variables `filepath` and `filepath_png` are already defined — do NOT redefine them. "
                "Always add legend, title, axis labels, and distinct colors per series. "
                "Do NOT use open(), os., subprocess, or hardcoded file paths."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": (
                            "Python code to generate the plot. "
                            "Must save to `filepath` or `filepath_png`. "
                            "If `saved_data` is available, use it directly with "
                            "`pd.DataFrame(saved_data)`. NEVER use open()."
                        )
                    },
                    "queried_data_path": {
                        "type": "string",
                        "description": (
                            "Optional path returned from a previous execute_code call. "
                            "The file will be automatically loaded and exposed in code "
                            "as `saved_data`."
                        )
                    }
                },
                "required": ["code"]
            }
        }
    }
]

def dispatch_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "inspect_dataset":
        result = query_data(tool_input["question"])
    elif tool_name == "execute_code":
        result = execute_code(tool_input["code"])
    elif tool_name == "plot_chart":
        result = plot_chart(
            data=tool_input["data"],
            chart_type=tool_input["chart_type"],
            x=tool_input["x"],
            y=tool_input["y"],
            title=tool_input["title"]
        )
    elif tool_name == "plot_code":
        result = plot_code(tool_input["code"])
    else:
        result = {"error": f"Ukendt tool: {tool_name}"}

    log_tool_call(tool_name, tool_input, result)
    return json.dumps(result, default=str)

def run_agent(user_query: str, verbose: bool = True) -> str:
    messages = [{"role": "user", "content": user_query}]
    log_tool_call("user_query", {"query": user_query}, {})
    if verbose:
        print(f"\nSpørgsmål: {user_query}")

    while True:
        for attempt in range(5):
            try:
                response = client.chat.complete(
                    model="mistral-large-latest",
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
                    tools=TOOLS,
                    tool_choice="auto"
                )
                break
            except Exception as e:
                if "429" in str(e):
                    wait = 10 * (attempt + 1)
                    print(f"  ⏳ Rate limit — venter {wait} sekunder...")
                    time.sleep(wait)
                else:
                    raise

        msg = response.choices[0].message
        messages.append({"role": "assistant", "content": msg.content, "tool_calls": msg.tool_calls})

        if not msg.tool_calls:
            if verbose:
                print(f"\nSvar: {msg.content}\n")
            log_tool_call("final_answer", {"query": user_query}, {"answer": msg.content})
            return msg.content

        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            if verbose:
                print(f"  → Kalder tool: {name}")

            result = dispatch_tool(name, args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

if __name__ == "__main__":
    user_input = input("Stil et spørgsmål om ad data: ")
    run_agent(user_input)