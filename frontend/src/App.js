import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { ThemeProvider } from 'styled-components';
import Header from './components/Header';
import Footer from './components/Footer';
import HomePage from './components/HomePage';
import ShopPage from './components/ShopPage';
import AboutPage from './components/AboutPage';
import ContactPage from './components/ContactPage';
import BikePage from './components/BikePage';
import CartPage from './components/CartPage';
import RevivedPage from './components/RevivedPage';  // New import
import GlobalStyle from './styles/GlobalStyle';
import theme from './styles/theme';
import { CartProvider } from './CartContext';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CartProvider>
        <Router>
          <GlobalStyle />
          <Header />
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/shop" element={<ShopPage />} />
            <Route path="/shop/:bikeId" element={<BikePage />} />
            <Route path="/cart" element={<CartPage />} />
            <Route path="/revived" element={<RevivedPage />} />  {/* New route */}
            <Route path="/about" element={<AboutPage />} />
            <Route path="/contact" element={<ContactPage />} />
          </Routes>
          <Footer />
        </Router>
      </CartProvider>
    </ThemeProvider>
  );
}

export default App;