import React, { createContext, useState, useEffect, useCallback } from 'react';
import { addToCart as apiAddToCart, fetchCart as apiFetchCart, removeFromCart as apiRemoveFromCart } from './api';

export const CartContext = createContext();

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const maxRetries = 3;

  // Fetch cart with retry mechanism
  const getCart = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await apiFetchCart();
      
      // If the API returns undefined or null, use empty array
      setCart(Array.isArray(data) ? data : []);
      setError(null);
    } catch (error) {
      console.error('Failed to fetch cart:', error);
      setError('Unable to load your cart. Please try again later.');
      
      // Handle retry logic if needed
      if (retryCount < maxRetries) {
        console.log(`Retrying cart fetch (${retryCount + 1}/${maxRetries})...`);
        setRetryCount(prevCount => prevCount + 1);
        // Retry after a delay that increases with each retry
        setTimeout(() => getCart(), 1000 * (retryCount + 1));
      }
    } finally {
      setIsLoading(false);
    }
  }, [retryCount]);

  useEffect(() => {
    getCart();
  }, [getCart]);

  const addToCart = async (bike) => {
    try {
      console.log('CartContext received for adding:', bike);
      
      // If we receive a cartItem object (with bike_id), use it directly
      if (bike.bike_id) {
        console.log('Adding item with bike_id directly:', bike);
        const newCartItem = await apiAddToCart(bike);
        console.log('Added to cart response:', newCartItem);
        setCart((prevCart) => [...prevCart, newCartItem]);
        return;
      }

      // Otherwise handle as a complete bike object
      const existingItem = cart.find((item) => item.bike && item.bike.id === bike.id);
      if (existingItem) {
        console.log('Item already exists in cart:', bike.id);
        alert('This item is already in the cart.');
        return;
      }

      const cartItem = { bike_id: bike.id, quantity: 1 };
      console.log('Sending to API:', cartItem);
      try {
        const newCartItem = await apiAddToCart(cartItem);
        console.log('Added to cart response:', newCartItem);
        setCart((prevCart) => [...prevCart, newCartItem]);
      } catch (apiError) {
        console.error('API Error:', apiError);
        console.error('API Error details:', apiError.response?.data);
        throw apiError;
      }
    } catch (error) {
      console.error('Failed to add to cart:', error);
      
      // More user-friendly error message
      const errorMessage = error.response?.data?.message || error.message || 'Unknown error';
      alert(`Unable to add item to cart: ${errorMessage}`);
      throw error;
    }
  };

  const removeFromCart = async (cartItemId) => {
    try {
      await apiRemoveFromCart(cartItemId);
      setCart((prevCart) => prevCart.filter((item) => item.id !== cartItemId));
      return true;
    } catch (error) {
      console.error('Failed to remove from cart:', error);
      alert('Unable to remove item from cart. Please try again.');
      throw error;
    }
  };

  // Refresh cart method that can be called from components
  const refreshCart = () => {
    getCart();
  };

  return (
    <CartContext.Provider value={{ 
      cart, 
      setCart, 
      addToCart, 
      removeFromCart, 
      refreshCart,
      isLoading,
      error 
    }}>
      {children}
    </CartContext.Provider>
  );
};