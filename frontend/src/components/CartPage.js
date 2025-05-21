// frontend/src/components/CartPage.js

import React, { useContext, useEffect, useState } from 'react';
import styled from 'styled-components';
import { CartContext } from '../CartContext';
import { createOrder, createCheckoutSession } from '../api';

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

const ErrorMessage = styled.div`
  color: #d32f2f;
  background-color: #ffebee;
  padding: ${(props) => props.theme.spacing.small};
  border-radius: ${(props) => props.theme.borderRadius};
  margin: ${(props) => props.theme.spacing.medium} 0;
  text-align: center;
`;

const RetryButton = styled.button`
  background-color: ${(props) => props.theme.colors.secondary};
  color: #fff;
  border: none;
  padding: ${(props) => props.theme.spacing.small};
  border-radius: ${(props) => props.theme.borderRadius};
  margin-top: ${(props) => props.theme.spacing.small};
  cursor: pointer;

  &:hover {
    background-color: ${(props) => props.theme.colors.primary};
  }
`;

const LoadingSpinner = styled.div`
  margin: 40px auto;
  text-align: center;
  font-style: italic;
  color: ${(props) => props.theme.colors.secondary};
`;

const InfoMessage = styled.div`
  background-color: #e3f2fd;
  color: #0d47a1;
  padding: ${(props) => props.theme.spacing.medium};
  border-radius: ${(props) => props.theme.borderRadius};
  margin: ${(props) => props.theme.spacing.medium} 0;
  text-align: center;
`;

const ContactInfo = styled.div`
  margin-top: ${(props) => props.theme.spacing.large};
  padding: ${(props) => props.theme.spacing.medium};
  background-color: #f5f5f5;
  border-radius: ${(props) => props.theme.borderRadius};
  text-align: center;
`;

const ContactFormModal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const ContactForm = styled.div`
  background-color: white;
  padding: 30px;
  border-radius: ${(props) => props.theme.borderRadius};
  max-width: 500px;
  width: 90%;
  box-shadow: ${(props) => props.theme.boxShadow};
`;

const FormField = styled.div`
  margin-bottom: 15px;

  label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
  }

  input {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
  }

  .error {
    color: red;
    font-size: 0.8rem;
    margin-top: 5px;
  }
`;

const FormButtons = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: 20px;

  button {
    padding: 10px 15px;
    border-radius: 4px;
    border: none;
    cursor: pointer;

    &.cancel {
      background-color: #f5f5f5;
      color: #333;
    }

    &.submit {
      background-color: ${(props) => props.theme.colors.primary};
      color: white;
    }
  }
`;

const CartPage = () => {
  const { cart, refreshCart, removeFromCart, isLoading, error: contextError } = useContext(CartContext);
  const [isCheckoutLoading, setIsCheckoutLoading] = useState(false);
  const [pageError, setPageError] = useState(null);
  const [showBackupContact, setShowBackupContact] = useState(false);
  const [showContactForm, setShowContactForm] = useState(false);
  const [customerData, setCustomerData] = useState({
    name: '',
    email: '',
    phone: ''
  });
  const [formErrors, setFormErrors] = useState({});

  useEffect(() => {
    // Cart is already being fetched in the CartContext
  }, []);

  const handleRemoveFromCart = async (itemId) => {
    try {
      setPageError(null);
      await removeFromCart(itemId);
    } catch (error) {
      setPageError('Failed to remove item from cart');
      console.error('Failed to remove item:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCustomerData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error for this field when user types
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const errors = {};
    if (!customerData.name.trim()) errors.name = "Imię i nazwisko jest wymagane";
    if (!customerData.email.trim()) {
      errors.email = "Email jest wymagany";
    } else if (!/\S+@\S+\.\S+/.test(customerData.email)) {
      errors.email = "Niepoprawny format email";
    }
    if (!customerData.phone.trim()) {
      errors.phone = "Numer telefonu jest wymagany";
    } else if (!/^\d{9,12}$/.test(customerData.phone.replace(/\s+/g, ''))) {
      errors.phone = "Niepoprawny format numeru telefonu";
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleInitiateCheckout = () => {
    setShowContactForm(true);
  };

  const handleCancelCheckout = () => {
    setShowContactForm(false);
  };

  const handleCheckout = async () => {
    try {
      setIsCheckoutLoading(true);
      setPageError(null);
      
      if (!cart.length) {
        setPageError('Cannot checkout with an empty cart');
        return;
      }
      
      const orderItems = cart.map((item) => ({
        bike_id: item.bike.id,
        quantity: item.quantity,
      }));
      const totalPrice = cart.reduce((total, item) => total + item.bike.price * item.quantity, 0);
      const order = { 
        total_price: totalPrice, 
        items: orderItems,
        customer: customerData
      };

      console.log('Sending order data:', order);
      
      const createdOrder = await createOrder(order);
      console.log('Order created successfully:', createdOrder);
      
      setShowContactForm(false);
      alert('Dziękujemy za złożenie zamówienia! Skontaktujemy się z Tobą wkrótce, aby ustalić szczegóły dostawy.');
      refreshCart();
      
    } catch (error) {
      console.error('Checkout error:', error);
      setPageError('Failed to process checkout. Please try again or use the contact option below.');
      setShowBackupContact(true);
      setShowContactForm(false);
    } finally {
      setIsCheckoutLoading(false);
    }
  };

  const handleSubmitOrder = (e) => {
    e.preventDefault();
    if (validateForm()) {
      handleCheckout();
    }
  };

  const totalPrice = cart.reduce((total, item) => 
    total + (item.bike ? item.bike.price * item.quantity : 0), 0);

  if (isLoading) {
    return (
      <CartContainer>
        <h1>Your Cart</h1>
        <LoadingSpinner>Loading your cart...</LoadingSpinner>
      </CartContainer>
    );
  }

  const error = contextError || pageError;

  return (
    <CartContainer>
      <h1>Your Cart</h1>
      
      <InfoMessage>
        Narazie obsługujemy tylko płatności przy odbiorze.
        Złóż zamówienie, aby ustalić termin odbioru roweru.
      </InfoMessage>
      
      {error && (
        <ErrorMessage>
          {error}
          <div>
            <RetryButton onClick={handleRetry}>Retry</RetryButton>
          </div>
        </ErrorMessage>
      )}
      
      {!error && cart.length === 0 ? (
        <p>Your cart is empty</p>
      ) : (
        <>
          {cart.map((item) => (
            <CartItem key={item.id}>
              <div>
                <h3>{item.bike?.name || 'Unknown Product'}</h3>
                <p>Quantity: {item.quantity}</p>
                <p>Price: {item.bike?.price || 'N/A'} PLN</p>
              </div>
              <RemoveButton 
                onClick={() => handleRemoveFromCart(item.id)}
                disabled={isCheckoutLoading}
              >
                {isCheckoutLoading ? 'Please wait...' : 'Remove'}
              </RemoveButton>
            </CartItem>
          ))}
          <h2>Total: {totalPrice.toFixed(2)} PLN</h2>
          {cart.length > 0 && (
            <CheckoutButtonContainer>
              <CheckoutButton onClick={handleInitiateCheckout} disabled={isCheckoutLoading || !!error}>
                {isCheckoutLoading ? 'Processing...' : 'Complete Order'}
              </CheckoutButton>
            </CheckoutButtonContainer>
          )}
          
          {showBackupContact && (
            <ContactInfo>
              <h3>Having trouble with your order?</h3>
              <p>If you're experiencing technical issues, you can also contact us directly:</p>
              <p>Phone: 574 513 493</p>
              <p>Email: bajkpaker@gmail.com</p>
              <p>Address: ul. Styczyńskiego 10/1, 44-100 Gliwice</p>
            </ContactInfo>
          )}
        </>
      )}

      {showContactForm && (
        <ContactFormModal>
          <ContactForm>
            <h2>Twoje dane kontaktowe</h2>
            <p>Prosimy o podanie danych kontaktowych. Skontaktujemy się w celu ustalenia szczegółów odbioru roweru.</p>
            
            <form onSubmit={handleSubmitOrder}>
              <FormField>
                <label htmlFor="name">Imię i nazwisko:</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={customerData.name}
                  onChange={handleInputChange}
                />
                {formErrors.name && <div className="error">{formErrors.name}</div>}
              </FormField>
              
              <FormField>
                <label htmlFor="email">Email:</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={customerData.email}
                  onChange={handleInputChange}
                />
                {formErrors.email && <div className="error">{formErrors.email}</div>}
              </FormField>
              
              <FormField>
                <label htmlFor="phone">Telefon:</label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={customerData.phone}
                  onChange={handleInputChange}
                />
                {formErrors.phone && <div className="error">{formErrors.phone}</div>}
              </FormField>
              
              <p><small>Klikając "Wyślij zamówienie" wysyłasz do nas zamówienie, a my zadzwonimy w celu umówienia godziny i dnia odbioru roweru.</small></p>
              
              <FormButtons>
                <button type="button" className="cancel" onClick={handleCancelCheckout}>Anuluj</button>
                <button type="submit" className="submit" disabled={isCheckoutLoading}>
                  {isCheckoutLoading ? 'Przetwarzanie...' : 'Wyślij zamówienie'}
                </button>
              </FormButtons>
            </form>
          </ContactForm>
        </ContactFormModal>
      )}
    </CartContainer>
  );
};

export default CartPage;