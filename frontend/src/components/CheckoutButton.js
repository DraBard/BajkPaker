import React from 'react';
import axios from 'axios';

function CheckoutButton({ orderId }) {
  const handleCheckout = async () => {
    try {
      const response = await axios.post('http://localhost:8002/api/payments/create-checkout-session', { order_id: orderId });
      window.location.href = response.data.checkoutUrl;
    } catch (err) {
      alert('Failed to initiate payment');
    }
  };

  return <button onClick={handleCheckout}>Checkout with Stripe</button>;
}

export default CheckoutButton;