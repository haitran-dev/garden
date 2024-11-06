import type { APIRoute } from "astro";

export const GET: APIRoute = async ({ request }) => {
  const url = new URL(request.url);
  console.log("Received request URL:", url.toString());

  const targetUrl = url.searchParams.get("url");

  if (!targetUrl) {
    console.log("No URL parameter found");
    return new Response("URL parameter is required", {
      status: 400,
      headers: {
        "Content-Type": "text/plain",
      },
    });
  }

  try {
    const response = await fetch(targetUrl, {
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const html = await response.text();
    return new Response(html, {
      headers: {
        "Content-Type": "text/html",
        "Access-Control-Allow-Origin": "*",
      },
    });
  } catch (error) {
    console.error("Error fetching URL:", error);
    return new Response(JSON.stringify({ error: "Error fetching URL" }), {
      status: 500,
      headers: {
        "Content-Type": "application/json",
      },
    });
  }
};
