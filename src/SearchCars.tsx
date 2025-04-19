import React, { useState, useEffect } from "react";

interface Car {
  CarId: string;
  make: string;
  model: string;
  year?: string;
  price: number;
  days?: number;
}

const SearchCars: React.FC = () => {
  const [query, setQuery] = useState("");
  const [cars, setCars] = useState<Car[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cartMessage, setCartMessage] = useState<string>("");

  const userId = "user123";
  const BASE = process.env.REACT_APP_API_BASE_URL!;
  const API_KEY = process.env.REACT_APP_API_KEY!;
  const AUTH_TOKEN = process.env.REACT_APP_AUTH_TOKEN!;

  const fetchCars = async (q = "") => {
    setLoading(true);
    setError(null);

    try {
      const resp = await fetch(`${BASE}/search?q=${encodeURIComponent(q)}`, {
        method: "GET",
        cache: "no-cache",
        headers: {
          "x-api-key": API_KEY,
          "Authorization": `Bearer ${AUTH_TOKEN}`
        }
      });
      if (!resp.ok) throw new Error(resp.statusText);
      const data = await resp.json();
      setCars(data.cars.map((c: Car) => ({ ...c, days: c.days || 1 })));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCars();
  }, []);

  const addToCart = async (carId: string, days: number) => {
    setCartMessage("");
    try {
      const resp = await fetch(`${BASE}/cart`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": API_KEY,
          "Authorization": `Bearer ${AUTH_TOKEN}`
        },
        body: JSON.stringify({ UserId: userId, CarId: carId, Quantity: days })
      });
      if (!resp.ok) throw new Error(resp.statusText);
      setCartMessage(`✅ Added ${carId} to cart`);
    } catch (err: any) {
      setCartMessage(`❌ Failed to add: ${err.message}`);
    }
  };

  return (
    <div>
      <h2>Search for Rental Cars</h2>
      <input
        type="text"
        placeholder="Make or model…"
        value={query}
        onChange={e => setQuery(e.target.value)}
      />
      <button onClick={() => fetchCars(query)} disabled={loading}>
        {loading ? "Searching…" : "Search"}
      </button>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {cartMessage && <p>{cartMessage}</p>}

      <ul style={{ listStyle: "none", padding: 0 }}>
        {cars.map(car => (
          <li key={car.CarId} style={{ margin: 20, borderBottom: "1px solid #ccc" }}>
            <strong>{car.make} {car.model} {car.year && `(${car.year})`}</strong>
            <div>Rate: ${car.price}/day</div>
            <label>
              Days:
              <input
                type="number"
                value={car.days}
                min={1}
                onChange={e => {
                  const days = parseInt(e.target.value, 10) || 1;
                  setCars(cs => cs.map(c => c.CarId === car.CarId ? { ...c, days } : c));
                }}
              />
            </label>
            <button onClick={() => addToCart(car.CarId, car.days!)}>Add to Cart</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default SearchCars;
