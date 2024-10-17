import React, { createContext, useState } from 'react';

export const CartContext = createContext();

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState([]);

  const addToCart = (bike) => {
    setCart((prevCart) => {
      const existingItem = prevCart.find((item) => item.id === bike.id);
      if (existingItem) {
        return prevCart.map((item) =>
          item.id === bike.id ? { ...item, quantity: item.quantity + 1 } : item
        );
      } else {
        return [...prevCart, { ...bike, quantity: 1 }];
      }
    });
  };

  const removeFromCart = (bikeId) => {
    setCart((prevCart) => prevCart.filter((item) => item.id !== bikeId));
  };

  return (
    <CartContext.Provider value={{ cart, addToCart, removeFromCart }}>
      {children}
    </CartContext.Provider>
  );
};