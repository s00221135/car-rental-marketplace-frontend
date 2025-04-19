import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

interface CartItem {
  CarId: string;
  make: string;
  model: string;
  year: string;
  price: number;
  Quantity: number;
}

const ShoppingCart: React.FC = () => {
  const [userId] = useState("user123");
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();
  const BASE = process.env.REACT_APP_API_BASE_URL!;
  const API_KEY = process.env.REACT_APP_API_KEY!;
  const AUTH_TOKEN = process.env.REACT_APP_AUTH_TOKEN!;

  const fetchCart = async () => {
    const url = `${BASE}/cart?UserId=${encodeURIComponent(userId)}`;
    const opts: RequestInit = {
      method: "GET",
      headers: {
        "x-api-key": API_KEY,
        "Authorization": `Bearer ${AUTH_TOKEN}`,
        "Accept": "application/json"
      },
      cache: "no-cache"
    };

    console.group("[ShoppingCart] fetchCart");
    console.log("→ URL:", url);
    console.log("→ Options:", opts);
    console.time("ShoppingCart.fetchCart");
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(url, opts);
      console.log("← Status:", response.status, response.statusText);
      const data = await response.json();
      console.log("← JSON:", data);

      if (!response.ok) {
        throw new Error(data.message || response.statusText);
      }

      console.timeEnd("ShoppingCart.fetchCart");
      setCartItems(data.cartItems || []);
      setMessage(data.message || "");
    } catch (err: any) {
      console.error("[ShoppingCart] Error:", err);
      console.timeEnd("ShoppingCart.fetchCart");
      setError(err.message);
    } finally {
      setLoading(false);
      console.groupEnd();
    }
  };

  const removeFromCart = async (item: CartItem) => {
    const url = `${BASE}/cart?UserId=${encodeURIComponent(userId)}&CarId=${encodeURIComponent(item.CarId)}`;
    const opts: RequestInit = {
      method: "DELETE",
      headers: {
        "x-api-key": API_KEY,
        "Authorization": `Bearer ${AUTH_TOKEN}`,
        "Accept": "application/json"
      },
      cache: "no-cache"
    };

    console.group(`[ShoppingCart] removeFromCart(${item.CarId})`);
    console.log("→ URL:", url);
    console.time(`ShoppingCart.remove.${item.CarId}`);
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(url, opts);
      console.log("← Status:", response.status, response.statusText);
      const data = await response.json();
      console.log("← JSON:", data);

      if (!response.ok) {
        throw new Error(data.message || response.statusText);
      }

      console.timeEnd(`ShoppingCart.remove.${item.CarId}`);
      setMessage(data.message || "Item removed");
      setCartItems(prev => prev.filter(ci => ci.CarId !== item.CarId));
    } catch (err: any) {
      console.error("[ShoppingCart] Remove error:", err);
      console.timeEnd(`ShoppingCart.remove.${item.CarId}`);
      setError(err.message);
    } finally {
      setLoading(false);
      console.groupEnd();
    }
  };

  useEffect(() => {
    fetchCart();
  }, []);

  return (
    <div>
      <h2>Shopping Cart</h2>
      {loading && <p>Loading cart items…</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {message && <p>{message}</p>}

      {cartItems.length > 0 ? (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {cartItems.map((item, i) => (
            <li key={i} style={{ marginBottom: 20, borderBottom: "1px solid #ccc", paddingBottom: 10 }}>
              <strong>{item.make} {item.model} ({item.year})</strong>
              <div>
                Days: {item.Quantity} — Rate: ${item.price}/day — Total: ${ (item.price * item.Quantity).toFixed(2) }
              </div>
              <button onClick={() => removeFromCart(item)}>Remove</button>
            </li>
          ))}
        </ul>
      ) : (
        <p>Your cart is empty.</p>
      )}

      {cartItems.length > 0 && <button onClick={() => navigate("/checkout")}>Proceed to Checkout</button>}
    </div>
  );
};

export default ShoppingCart;
