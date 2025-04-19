import React, { useEffect, useState } from "react";

interface CartItem {
  CarId: string;
  make: string;
  model: string;
  year: string;
  price: number;
  Quantity: number;
}

const Checkout: React.FC = () => {
  const [userId] = useState("user123");
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [checkoutStatus, setCheckoutStatus] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const BASE = process.env.REACT_APP_API_BASE_URL!;
  const API_KEY = process.env.REACT_APP_API_KEY!;
  const AUTH_TOKEN = process.env.REACT_APP_AUTH_TOKEN!;

  const fetchCart = async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await fetch(`${BASE}/cart?UserId=${encodeURIComponent(userId)}`, {
        method: "GET",
        headers: {
          "x-api-key": API_KEY,
          "Authorization": `Bearer ${AUTH_TOKEN}`,
        },
      });
      if (!resp.ok) throw new Error(resp.statusText);
      const data = await resp.json();
      setCartItems(data.cartItems || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCart();
  }, []);

  const handleCheckoutAll = () => {
    setError(null);
    setCheckoutStatus("✅ Thanks! Check your email for confirmation shortly.");

    cartItems.forEach((item) => {
      fetch(`${BASE}/checkoutWorkflow`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": API_KEY,
          "Authorization": `Bearer ${AUTH_TOKEN}`,
        },
        body: JSON.stringify({
          UserId: userId,
          CarId: item.CarId,
          Quantity: item.Quantity,
        }),
      })
        .then((res) => {
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          return res.json();
        })
        .then((data) => {
          console.debug("CheckoutWorkflow response:", data);
        })
        .catch((err) => {
          console.error("CheckoutWorkflow error:", err);
        });
    });
  };

  return (
    <div>
      <h2>Checkout</h2>

      {loading && <p>Loading your cart…</p>}
      {!loading && error && <p style={{ color: "red" }}>{error}</p>}

      <h3>Your Cart</h3>
      {cartItems.length > 0 ? (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {cartItems.map((item, i) => (
            <li key={i} style={{ marginBottom: 12 }}>
              {item.make} {item.model} ({item.Quantity} days @ ${item.price}/day)
            </li>
          ))}
        </ul>
      ) : (
        !loading && <p>Your cart is empty.</p>
      )}

      {cartItems.length > 0 && (
        <button onClick={handleCheckoutAll} style={{ padding: "8px 16px", marginTop: 16 }}>
          Checkout All
        </button>
      )}

      {checkoutStatus && (
        <div style={{ marginTop: 20 }}>
          <h3>Status</h3>
          <p>{checkoutStatus}</p>
        </div>
      )}
    </div>
  );
};

export default Checkout;
