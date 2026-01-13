const BASE_URL = "http://localhost:8000";

export async function getProducts() {
  const r = await fetch(`${BASE_URL}/products`);
  return r.json();
}

export async function createOrder(items: { product_id: number; quantity: number }[]) {
  const r = await fetch(`${BASE_URL}/orders`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ items }),
  });
  return r.json();
}

export async function listOrders(status?: string) {
  const qs = status ? `?status=${encodeURIComponent(status)}` : "";
  const r = await fetch(`${BASE_URL}/orders${qs}`);
  return r.json();
}

export async function getOrder(id: number) {
  const r = await fetch(`${BASE_URL}/orders/${id}`);
  return r.json();
}

export async function payOrder(id: number) {
  const r = await fetch(`${BASE_URL}/orders/${id}/pay`, { method: "POST" });
  return r.json();
}

export async function shipOrder(id: number) {
  const r = await fetch(`${BASE_URL}/orders/${id}/ship`, { method: "POST" });
  return r.json();
}

export async function cancelOrder(id: number) {
  const r = await fetch(`${BASE_URL}/orders/${id}/cancel`, { method: "POST" });
  return r.json();
}
