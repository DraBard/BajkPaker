import axios from 'axios';

const PRODUCT_API_URL = 'https://product-service.fly.dev:8001/api';  // Updated port to 8001
const ORDER_API_URL = 'https://order-service.fly.dev:8002/api';    // Updated port to 8002
const USER_API_URL = 'http://localhost:8003/api';

export const fetchBikes = async () => {
  const response = await axios.get(`${PRODUCT_API_URL}/bikes`);
  return response.data;
};

export const fetchBike = async (bikeId) => {
  const response = await axios.get(`${PRODUCT_API_URL}/bikes/${bikeId}`);
  return response.data;
};

export const addToCart = async (cartItem) => {
  const response = await axios.post(`${ORDER_API_URL}/cart`, cartItem, { withCredentials: true });
  return response.data;
};

export const fetchCart = async () => {
  const response = await axios.get(`${ORDER_API_URL}/cart`, { withCredentials: true });
  return response.data;
};

export const removeFromCart = async (cartItemId) => {
  const response = await axios.delete(`${ORDER_API_URL}/cart/${cartItemId}`, { withCredentials: true });
  return response.data;
};

export const createOrder = async (order) => {
  const response = await axios.post(`${ORDER_API_URL}/orders`, order, { withCredentials: true });
  return response.data;
};

export const registerUser = async (userData) => {
  const response = await axios.post(`${USER_API_URL}/users`, userData);
  return response.data;
};

export const loginUser = async (userData) => {
  const response = await axios.post(`${USER_API_URL}/users/login`, userData);
  return response.data;
};

export async function createCheckoutSession(orderId) {
  const response = await axios.post(`${ORDER_API_URL}/payments/create-checkout-session`, {
    order_id: orderId,
  }, { withCredentials: true });
  return response.data.checkoutUrl; // Access the data directly
}
