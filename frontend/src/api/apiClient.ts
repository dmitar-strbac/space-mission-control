const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const TOKEN_STORAGE_KEY = "smc_access_token";

export function getWebSocketBaseUrl(): string {
  const url = new URL(API_BASE_URL);

  url.protocol =
    url.protocol === "https:" ? "wss:" : "ws:";

  return url.toString();
}

export class ApiError extends Error {
  status: number;
  detail?: unknown;

  constructor(status: number, message: string, detail?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

export function getStoredAccessToken(): string | null {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function storeAccessToken(token: string): void {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearStoredAccessToken(): void {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

interface ApiRequestOptions extends RequestInit {
  authenticated?: boolean;
}

export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  const {
    authenticated = true,
    headers: providedHeaders,
    ...requestOptions
  } = options;

  const headers = new Headers(providedHeaders);

  if (!headers.has("Content-Type") && requestOptions.body) {
    headers.set("Content-Type", "application/json");
  }

  if (authenticated) {
    const token = getStoredAccessToken();

    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...requestOptions,
    headers,
  });

  if (!response.ok) {
    let detail: unknown;

    try {
      detail = await response.json();
    } catch {
      detail = undefined;
    }

    throw new ApiError(
      response.status,
      `Request failed with status ${response.status}.`,
      detail,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}
