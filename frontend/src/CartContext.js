import React, { createContext, useState, useEffect } from 'react';
import { addToCart as apiAddToCart, fetchCart as apiFetchCart, removeFromCart as apiRemoveFromCart } from './api';

export const CartContext = createContext();

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState([]);

  useEffect(() => {
    const getCart = async () => {
      try {
        const data = await apiFetchCart();
        setCart(data);
      } catch (error) {
        console.error('Failed to fetch cart:', error);
      }
    };

    getCart();
  }, []);

  const addToCart = async (bike) => {
    try {
      const cartItem = { bike_id: bike.id, quantity: 1 };
      const newCartItem = await apiAddToCart(cartItem);
      setCart((prevCart) => {
        const existingItem = prevCart.find((item) => item.bike_id === newCartItem.bike_id);
        if (existingItem) {
          return prevCart.map((item) =>
            item.bike_id === newCartItem.bike_id ? { ...item, quantity: item.quantity + 1 } : item
          );
        } else {
          return [...prevCart, newCartItem];
        }
      });
    } catch (error) {
      console.error('Failed to add to cart:', error);
    }
  };

  const removeFromCart = async (cartItemId) => {
    try {
      await apiRemoveFromCart(cartItemId);
      setCart((prevCart) => prevCart.filter((item) => item.id !== cartItemId));
      return true;
    } catch (error) {
      console.error('Failed to remove from cart:', error);
      throw error;
    }
  };

  return (
    <CartContext.Provider value={{ cart, setCart, addToCart, removeFromCart }}>
      {children}
    </CartContext.Provider>
  );
};