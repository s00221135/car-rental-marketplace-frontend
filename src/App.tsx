import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import SearchCars from './SearchCars.tsx';
import ShoppingCart from './ShoppingCart.tsx';
import Checkout from './Checkout.tsx';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="App" style={{ fontFamily: "Arial, sans-serif", margin: "20px" }}>
        <header>
          <h1>Car Rental Marketplace</h1>
          <nav style={{ marginBottom: "20px" }}>
            <Link style={{ marginRight: "15px" }} to="/search">Search Cars</Link>
            <Link style={{ marginRight: "15px" }} to="/cart">Shopping Cart</Link>
            <Link to="/checkout">Checkout</Link>
          </nav>
        </header>
        <main>
          <Routes>
            <Route path="/search" element={<SearchCars />} />
            <Route path="/cart" element={<ShoppingCart />} />
            <Route path="/checkout" element={<Checkout />} />
            <Route path="/" element={<SearchCars />} />
          </Routes>
        </main>
        <footer style={{ marginTop: "20px" }}>
          <p>&copy; 2025 Car Rental Marketplace</p>
        </footer>
      </div>
    </BrowserRouter>
  );
};

export default App;
