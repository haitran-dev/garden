const urlForm = document.getElementById("url-form") as HTMLFormElement;
const urlInput = document.getElementById("url-input") as HTMLInputElement;
const preview = document.getElementById("preview");
const previewContent = document.getElementById("preview-content");
const downloadButton = document.getElementById("download-epub");

async function extractContent(url: string) {
  try {
    // First fetch the URL content
    const encodedUrl = encodeURIComponent(url);
    console.log("Attempting to fetch:", `/api/fetch-url?url=${encodedUrl}`);
    console.log("Original URL:", url);

    // Add a base URL check
    const apiUrl = new URL("/api/fetch-url", window.location.origin);
    apiUrl.searchParams.set("url", url);

    console.log("Full API URL:", apiUrl.toString());

    const response = await fetch(apiUrl);
    console.log("Response:", response);

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `HTTP error! status: ${response.status}, message: ${errorText}`,
      );
    }
    const html = await response.text();

    // Then send it to extract-content endpoint
    const extractResponse = await fetch("/api/extract-content", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ html }),
    });

    if (!extractResponse.ok) {
      throw new Error(`HTTP error! status: ${extractResponse.status}`);
    }

    const article = await extractResponse.json();
    return article;
  } catch (error) {
    console.error("Error extracting content:", error);
    throw error;
  }
}

urlForm?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const url = urlInput.value;

  try {
    const article = await extractContent(url);

    console.log({ article });

    if (previewContent && article) {
      previewContent.innerHTML = article.content;
      preview?.classList.remove("hidden");
      downloadButton?.removeAttribute("disabled");
    }
  } catch (error) {
    console.error("Error:", error);
    alert("Error extracting content. Please try again.");
  }
});

downloadButton?.addEventListener("click", async () => {
  try {
    if (!previewContent?.innerHTML) {
      throw new Error("No content available to convert");
    }

    const response = await fetch("/api/generate-epub", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        content: previewContent.innerHTML,
        title: document.title || "Article",
        url: urlInput.value,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Handle the EPUB file download
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = "article.epub";
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(downloadUrl);
    document.body.removeChild(a);
  } catch (error) {
    console.error("Error generating EPUB:", error);
    alert("Error generating EPUB. Please try again.");
  }
});
