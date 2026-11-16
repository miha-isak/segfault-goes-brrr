// Small wrapper around fetch for our backend: sends/receives JSON and turns
// error responses into Error objects with a readable message.
export async function api(path, { method = "GET", body } = {}) {
  const res = await fetch(path, {
    method,
    headers: body === undefined ? {} : { "content-type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const data = res.status === 204 ? null : await res.json().catch(() => null);
  if (!res.ok) {
    const error = new Error(errorMessage(data) ?? `HTTP ${res.status}`);
    error.status = res.status;
    throw error;
  }
  return data;
}

// FastAPI answers {detail: "text"} or, for validation errors, {detail: [{loc, msg}, ...]}.
function errorMessage(data) {
  const detail = data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => `${d.loc?.at(-1) ?? "field"}: ${d.msg}`).join("; ");
  }
  return null;
}

// The logged-in user ({id, username}) or null.
export async function currentUser() {
  try {
    return await api("/api/auth/me");
  } catch (err) {
    if (err.status === 401) return null;
    throw err;
  }
}
