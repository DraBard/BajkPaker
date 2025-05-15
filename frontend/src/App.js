import React, { useState } from 'react';
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
import RevivedPage from './components/RevivedPage';
import RevivedDetailsPage from './components/RevivedDetailsPage';
import UserAuthPage from './components/UserAuthPage';
import GlobalStyle from './styles/GlobalStyle';
import theme from './styles/theme';
import { CartProvider } from './CartContext';
import { TermsModal } from './components/TermsModal';

function App() {
  const [termsOpen, setTermsOpen] = useState(false);

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
            <Route path="/revived" element={<RevivedPage />} />
            <Route path="/revived/:id" element={<RevivedDetailsPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/contact" element={<ContactPage />} />
            <Route path="/auth" element={<UserAuthPage />} />
            <Route path="/payment-success" element={<h1>Payment Successful!</h1>} />
            <Route path="/payment-cancel" element={<h1>Payment Canceled</h1>} />
          </Routes>
          <Footer onOpenTerms={() => setTermsOpen(true)} />
          <TermsModal open={termsOpen} onClose={() => setTermsOpen(false)} />
        </Router>
      </CartProvider>
    </ThemeProvider>
  );
}

export default App;