import React, { createContext, useState, useEffect, useCallback, useRef } from 'react';
import { addToCart as apiAddToCart, fetchCart as apiFetchCart, removeFromCart as apiRemoveFromCart } from './api';

export const CartContext = createContext();

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Use refs instead of state for tracking retries and request status
  const retryCount = useRef(0);
  const isFetchingRef = useRef(false);
  const maxRetries = 3;
  
  // Use ref to track component mounted state and timers
  const isMounted = useRef(true);
  const retryTimerRef = useRef(null);
  const requestCancelToken = useRef(null);

  // Fetch cart with improved retry mechanism
  const getCart = useCallback(async (force = false) => {
    // Prevent concurrent requests
    if (isFetchingRef.current && !force) {
      console.log('Cart fetch already in progress, skipping...');
      return;
    }

    // Clear any existing retry timers
    if (retryTimerRef.current) {
      clearTimeout(retryTimerRef.current);
      retryTimerRef.current = null;
    }

    try {
      if (!isMounted.current) return;
      
      isFetchingRef.current = true;
      setIsLoading(true);
      
      console.log(`Fetching cart (attempt ${retryCount.current + 1}/${maxRetries + 1})`);
      const data = await apiFetchCart();
      
      if (!isMounted.current) return;
      
      // If the API returns undefined or null, use empty array
      setCart(Array.isArray(data) ? data : []);
      setError(null);
      retryCount.current = 0; // Reset retry count on success
    } catch (error) {
      if (!isMounted.current) return;
      
      console.error('Failed to fetch cart:', error);
      setError('Unable to load your cart. Please try again later.');
      
      // Handle retry logic if needed
      if (retryCount.current < maxRetries) {
        const retryDelay = 2000 * Math.pow(2, retryCount.current); // Exponential backoff
        console.log(`Will retry cart fetch in ${retryDelay}ms...`);
        
        retryTimerRef.current = setTimeout(() => {
          if (isMounted.current) {
            retryCount.current += 1;
            getCart(true); // Force retry
          }
        }, retryDelay);
      } else {
        console.log(`Maximum retry attempts (${maxRetries}) reached, giving up.`);
      }
    } finally {
      if (isMounted.current) {
        setIsLoading(false);
        // Set a delay before allowing new requests to prevent rapid retries
        setTimeout(() => {
          isFetchingRef.current = false;
        }, 1000);
      }
    }
  }, []); // No dependencies needed as we use refs

  useEffect(() => {
    // Set mounted flag
    isMounted.current = true;
    
    // Initial fetch
    getCart();
    
    // Cleanup function
    return () => {
      isMounted.current = false;
      if (retryTimerRef.current) {
        clearTimeout(retryTimerRef.current);
      }
      if (requestCancelToken.current) {
        requestCancelToken.current();
      }
    };
  }, []); // Only run once on mount

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
      
      // Display a loading message to the user
      const loadingMessage = window.confirm('Adding to cart... Click OK to continue or Cancel to abort.');
      if (!loadingMessage) {
        console.log('User cancelled the cart addition');
        return;
      }
      
      try {
        const newCartItem = await apiAddToCart(cartItem);
        console.log('Added to cart response:', newCartItem);
        setCart((prevCart) => [...prevCart, newCartItem]);
        alert('Item added to cart successfully!');
      } catch (apiError) {
        console.error('API Error:', apiError);
        console.error('API Error details:', apiError.response?.data);
        
        // More specific error handling
        if (apiError.response?.status === 404) {
          alert('The requested bike is no longer available.');
        } else {
          alert(`Unable to add to cart: ${apiError.message || 'Server error'}`);
        }
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
    if (isMounted.current && !isFetchingRef.current) {
      console.log('Manual refresh of cart triggered');
      retryCount.current = 0; // Reset retry count before fetching
      getCart(true); // Force a refresh
    } else {
      console.log('Refresh cart called but fetch already in progress');
    }
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