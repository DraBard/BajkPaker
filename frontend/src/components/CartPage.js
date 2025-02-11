// frontend/src/components/CartPage.js

import React, { useContext, useEffect, useState } from 'react';
import styled from 'styled-components';
import { CartContext } from '../CartContext';
import { fetchCart, createOrder, createCheckoutSession } from '../api';

const CartContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: ${(props) => props.theme.spacing.medium};
  background-color: ${(props) => props.theme.colors.light};
  border-radius: ${(props) => props.theme.borderRadius};
  box-shadow: ${(props) => props.theme.boxShadow};
`;

const CartItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${(props) => props.theme.spacing.small} 0;
  border-bottom: 1px solid ${(props) => props.theme.colors.dark};
`;

const RemoveButton = styled.button`
  background-color: ${(props) => props.theme.colors.accent};
  color: #fff;
  border: none;
  padding: ${(props) => props.theme.spacing.small};
  border-radius: ${(props) => props.theme.borderRadius};
  cursor: pointer;

  &:hover {
    background-color: ${(props) => props.theme.colors.dark};
  }
`;

const CheckoutButtonContainer = styled.div`
  display: flex;
  justify-content: center;
  margin-top: ${(props) => props.theme.spacing.large};
`;

const CheckoutButton = styled.button`
  background-color: ${(props) => props.theme.colors.primary};
  color: #fff;
  border: none;
  padding: ${(props) => props.theme.spacing.medium};
  border-radius: ${(props) => props.theme.borderRadius};
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  width: 50%;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s ease, transform 0.3s ease;

  &:hover {
    background-color: ${(props) => props.theme.colors.secondary};
    transform: translateY(-2px);
  }

  &:disabled {
    background-color: ${(props) => props.theme.colors.disabled};
    cursor: not-allowed;
  }
`;

const CartPage = () => {
  const { cart, setCart, removeFromCart } = useContext(CartContext);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getCart = async () => {
      try {
        const data = await fetchCart();
        setCart(data);
      } catch (error) {
        console.error('Failed to fetch cart:', error);
        setError('Failed to load cart items');
      }
    };

    getCart();
  }, [setCart]);

  const handleRemoveFromCart = async (itemId) => {
    setIsLoading(true);
    try {
      await removeFromCart(itemId);
    } catch (error) {
      setError('Failed to remove item from cart');
      console.error('Failed to remove item:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCheckout = async () => {
    try {
      const orderItems = cart.map((item) => ({
        bike_id: item.bike.id,
        quantity: item.quantity,
      }));
      const totalPrice = cart.reduce((total, item) => total + item.bike.price * item.quantity, 0);
      const order = { total_price: totalPrice, items: orderItems };

      const createdOrder = await createOrder(order);
      const checkoutUrl = await createCheckoutSession(createdOrder.id);
      window.location.href = checkoutUrl; // Redirect to Stripe Checkout
    } catch (error) {
      console.error('Checkout error:', error);
    }
  };

  const totalPrice = cart.reduce((total, item) => total + item.bike.price * item.quantity, 0);

  if (error) {
    return <p>Error: {error}</p>;
  }

  return (
    <CartContainer>
      <h1>Your Cart</h1>
      {cart.length === 0 ? (
        <p>Your cart is empty</p>
      ) : (
        <>
          {cart.map((item) => (
            <CartItem key={item.id}>
              <div>
                <h3>{item.bike.name}</h3>
                <p>Quantity: {item.quantity}</p>
                <p>Price: ${item.bike.price}</p>
              </div>
              <RemoveButton 
                onClick={() => handleRemoveFromCart(item.id)}
                disabled={isLoading}
              >
                {isLoading ? 'Removing...' : 'Remove'}
              </RemoveButton>
            </CartItem>
          ))}
          <h2>Total: ${totalPrice.toFixed(2)}</h2>
          {cart.length > 0 && (
            <CheckoutButtonContainer>
              <CheckoutButton onClick={handleCheckout} disabled={isLoading}>
                {isLoading ? 'Processing...' : 'Checkout'}
              </CheckoutButton>
            </CheckoutButtonContainer>
          )}
        </>
      )}
    </CartContainer>
  );
};

export default CartPage;