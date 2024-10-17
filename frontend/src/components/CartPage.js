// frontend/src/components/CartPage.js

import React, { useContext, useEffect } from 'react';
import styled from 'styled-components';
import { CartContext } from '../CartContext';
import { fetchCart } from '../api';

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

const CartPage = () => {
  const { cart, setCart, removeFromCart } = useContext(CartContext);

  useEffect(() => {
    const getCart = async () => {
      try {
        const data = await fetchCart();
        setCart(data);
      } catch (error) {
        console.error('Failed to fetch cart:', error);
      }
    };

    getCart();
  }, [setCart]);

  const totalPrice = cart.reduce((total, item) => total + item.bike.price * item.quantity, 0);

  return (
    <CartContainer>
      <h1>Your Cart</h1>
      {cart.map((item) => (
        <CartItem key={item.id}>
          <div>
            <h3>{item.bike.name}</h3>
            <p>Quantity: {item.quantity}</p>
            <p>Price: ${item.bike.price}</p>
          </div>
          <RemoveButton onClick={() => removeFromCart(item.bike_id)}>Remove</RemoveButton>
        </CartItem>
      ))}
      <h2>Total: ${totalPrice.toFixed(2)}</h2>
    </CartContainer>
  );
};

export default CartPage;