const BASE_URL = "http://localhost:8000";

async function parseResponse(response) {
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || data.message || "Request failed.");
  }

  return data;
}

export async function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${BASE_URL}/ingest`, {
    method: "POST",
    body: formData,
  });

  return parseResponse(response);
}

export async function queryRAG(question) {
  const response = await fetch(`${BASE_URL}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query: question }),
  });

  return parseResponse(response);
}

export async function getStatus() {
  const response = await fetch(`${BASE_URL}/status`);
  return parseResponse(response);
}

export async function resetIndex() {
  const response = await fetch(`${BASE_URL}/reset`, {
    method: "DELETE",
  });

  return parseResponse(response);
}
