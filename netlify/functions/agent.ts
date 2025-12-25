import { Handler } from "@netlify/functions";

const API_BASE_URL = process.env.BACKEND_API_URL || "http://localhost:7777";

interface AgentRequest {
  prompt: string;
  max_steps?: number;
}

const handler: Handler = async (event, context) => {
  // Only allow POST requests
  if (event.httpMethod !== "POST") {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: "Method not allowed" }),
    };
  }

  try {
    const body: AgentRequest = JSON.parse(event.body || "{}");

    if (!body.prompt) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: "prompt is required" }),
      };
    }

    // Forward request to backend API
    const response = await fetch(`${API_BASE_URL}/agent`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        prompt: body.prompt,
        max_steps: body.max_steps || 10,
      }),
    });

    const data = await response.json();

    return {
      statusCode: response.status,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
      body: JSON.stringify(data),
    };
  } catch (error) {
    console.error("Error:", error);
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: "Internal server error",
        message: error instanceof Error ? error.message : String(error),
      }),
    };
  }
};

export { handler };
