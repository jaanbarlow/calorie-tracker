/**
 * Thin wrapper around fetch() that:
 *  - prepends the API base URL
 *  - injects the JWT Authorization header when available
 *  - throws a descriptive error on non-2xx responses
 */

const API_BASE = "";  // CRA proxy forwards to the backend container

export async function api(endpoint, options = {}) {
  const token = localStorage.getItem("token");

  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }

  return res.json();
}
