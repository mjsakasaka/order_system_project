import React, { useEffect, useMemo, useState } from "react";
import {
  getProducts,
  createOrder,
  listOrders,
  getOrder,
  payOrder,
  shipOrder,
  cancelOrder,
} from "./api";

type Product = { id: number; sku: string; name: string; price: number; stock: number };
type OrderListItem = { id: number; status: string; total_amount: number; created_at: string };

export default function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [quantities, setQuantities] = useState<Record<number, number>>({});
  const [orders, setOrders] = useState<OrderListItem[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [selectedOrderId, setSelectedOrderId] = useState<number | null>(null);
  const [orderDetail, setOrderDetail] = useState<any>(null);
  const [message, setMessage] = useState<string>("");

  async function refreshProducts() {
    setProducts(await getProducts());
  }
  async function refreshOrders() {
    setOrders(await listOrders(statusFilter || undefined));
  }
  async function refreshOrderDetail(id: number) {
    setOrderDetail(await getOrder(id));
  }

  useEffect(() => {
    refreshProducts();
    refreshOrders();
  }, []);

  useEffect(() => {
    refreshOrders();
  }, [statusFilter]);

  const selectedItems = useMemo(() => {
    return Object.entries(quantities)
      .map(([pid, qty]) => ({ product_id: Number(pid), quantity: qty }))
      .filter((x) => x.quantity > 0);
  }, [quantities]);

  async function onCreateOrder() {
    setMessage("");
    const res = await createOrder(selectedItems);
    if (res.error) {
      setMessage(`${res.error}: ${res.message}`);
      return;
    }
    setMessage(`Order #${res.id} created`);
    setQuantities({});
    await refreshProducts();
    await refreshOrders();
    setSelectedOrderId(res.id);
    setOrderDetail(res);
  }

  async function act(fn: (id: number) => Promise<any>) {
    if (!selectedOrderId) return;
    setMessage("");
    const res = await fn(selectedOrderId);
    if (res.error) {
      setMessage(`${res.error}: ${res.message}`);
      return;
    }
    setOrderDetail(res);
    await refreshProducts();
    await refreshOrders();
  }

  return (
    <div style={{ fontFamily: "sans-serif", padding: 16, maxWidth: 1100, margin: "0 auto" }}>
      <h2>Order Management System (MVP)</h2>

      {message && (
        <div style={{ padding: 12, border: "1px solid #ccc", marginBottom: 12 }}>
          {message}
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {/* Left: Products + Create Order */}
        <div style={{ border: "1px solid #ddd", padding: 12 }}>
          <h3>Products</h3>
          <table width="100%" cellPadding={6} style={{ borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th align="left">Name</th>
                <th align="right">Price</th>
                <th align="right">Stock</th>
                <th align="right">Qty</th>
              </tr>
            </thead>
            <tbody>
              {products.map((p) => (
                <tr key={p.id} style={{ borderTop: "1px solid #eee" }}>
                  <td>{p.name}</td>
                  <td align="right">{(p.price / 100).toFixed(2)}</td>
                  <td align="right">{p.stock}</td>
                  <td align="right">
                    <input
                      type="number"
                      min={0}
                      value={quantities[p.id] ?? 0}
                      onChange={(e) =>
                        setQuantities((q) => ({ ...q, [p.id]: Number(e.target.value) }))
                      }
                      style={{ width: 70 }}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <button
            onClick={onCreateOrder}
            disabled={selectedItems.length === 0}
            style={{ marginTop: 12, padding: "8px 12px" }}
          >
            Create Order
          </button>
        </div>

        {/* Right: Orders + Detail */}
        <div style={{ border: "1px solid #ddd", padding: 12 }}>
          <h3>Orders</h3>

          <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">All</option>
              <option value="CREATED">CREATED</option>
              <option value="PAID">PAID</option>
              <option value="SHIPPED">SHIPPED</option>
              <option value="CANCELLED">CANCELLED</option>
            </select>
            <button onClick={refreshOrders}>Refresh</button>
          </div>

          <table width="100%" cellPadding={6} style={{ borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th align="left">ID</th>
                <th align="left">Status</th>
                <th align="right">Total</th>
                <th align="left">Action</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((o) => (
                <tr key={o.id} style={{ borderTop: "1px solid #eee" }}>
                  <td>#{o.id}</td>
                  <td>{o.status}</td>
                  <td align="right">{(o.total_amount / 100).toFixed(2)}</td>
                  <td>
                    <button
                      onClick={async () => {
                        setSelectedOrderId(o.id);
                        await refreshOrderDetail(o.id);
                      }}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div style={{ marginTop: 12, borderTop: "1px solid #eee", paddingTop: 12 }}>
            <h4>Order Detail</h4>
            {!orderDetail ? (
              <div>Select an order to view</div>
            ) : (
              <>
                <div>
                  <b>#{orderDetail.id}</b> | Status: <b>{orderDetail.status}</b> | Total:{" "}
                  <b>{(orderDetail.total_amount / 100).toFixed(2)}</b>
                </div>

                <ul>
                  {orderDetail.items?.map((it: any, idx: number) => (
                    <li key={idx}>
                      {it.product_name} x {it.quantity} @ {(it.unit_price / 100).toFixed(2)}
                    </li>
                  ))}
                </ul>

                <div style={{ display: "flex", gap: 8 }}>
                  <button onClick={() => act(payOrder)}>Pay</button>
                  <button onClick={() => act(shipOrder)}>Ship</button>
                  <button onClick={() => act(cancelOrder)}>Cancel</button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      <div style={{ marginTop: 16, fontSize: 12, color: "#666" }}>
        Tip: MySQL seeded with 3 products on backend startup.
      </div>
    </div>
  );
}
