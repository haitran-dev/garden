import type { APIRoute } from 'astro';
import EPub from 'epub-gen';
import { tmpdir } from 'os';
import { join } from 'path';
import { readFile } from 'fs/promises';

interface EPubRequest {
  content: string;
  title?: string;
  url?: string;
}

export const POST: APIRoute = async ({ request }) => {
  try {
    const { content, title = 'Article', url = '' }: EPubRequest = await request.json();
    const outputPath = join(tmpdir(), `article-${Date.now()}.epub`);

    await new EPub({
      title: title,
      author: 'Web Article',
      publisher: url,
      content: [{
        title: title,
        data: content
      }],
      output: outputPath
    }).promise;

    const epubFile = await readFile(outputPath);
    
    return new Response(epubFile, {
      headers: {
        'Content-Type': 'application/epub+zip',
        'Content-Disposition': `attachment; filename="${title.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.epub"`
      }
    });
  } catch (error) {
    console.error('Error generating EPUB:', error);
    return new Response(
      JSON.stringify({ error: 'Error generating EPUB' }), 
      { 
        status: 500,
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
  }
}; 