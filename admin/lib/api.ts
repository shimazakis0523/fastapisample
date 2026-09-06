import { auth0 } from "@/lib/auth0";

const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000";

export interface Item {
  id: number;
  name: string;
  description: string | null;
  price: number;
  created_at: string;
  updated_at: string;
}

export interface ItemInput {
  name: string;
  description: string | null;
  price: number;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const fetcher = await auth0.createFetcher(undefined, { baseUrl: API_BASE_URL });

  const res = await fetcher.fetchWithAuth(path, {
    cache: "no-store",
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${init?.method ?? "GET"} ${path} failed: ${res.status} ${body}`);
  }

  return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
}

export function listItems(): Promise<Item[]> {
  return request<Item[]>("/api/v1/items");
}

export function getItem(id: number): Promise<Item> {
  return request<Item>(`/api/v1/items/${id}`);
}

export function createItem(data: ItemInput): Promise<Item> {
  return request<Item>("/api/v1/items", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateItem(id: number, data: Partial<ItemInput>): Promise<Item> {
  return request<Item>(`/api/v1/items/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export function deleteItem(id: number): Promise<void> {
  return request<void>(`/api/v1/items/${id}`, { method: "DELETE" });
}
