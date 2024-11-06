import type { APIRoute } from 'astro';
import { Readability } from '@mozilla/readability';
import { JSDOM } from 'jsdom';

export const POST: APIRoute = async ({ request }) => {
  try {
    const { html } = await request.json();
    
    // Create a DOM using jsdom
    const dom = new JSDOM(html);
    const reader = new Readability(dom.window.document);
    const article = reader.parse();

    return new Response(JSON.stringify(article), {
      headers: {
        'Content-Type': 'application/json'
      }
    });
  } catch (error) {
    return new Response('Error extracting content', { status: 500 });
  }
}; 