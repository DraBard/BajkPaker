import axios from 'axios';

// Define API URLs based on environment
const isProduction = process.env.NODE_ENV === 'production';

const PRODUCT_API_URL = isProduction
  ? 'https://product-service.fly.dev/api'
  : 'http://localhost:8001/api';

const ORDER_API_URL = isProduction
  ? 'https://order-service.fly.dev/api'
  : 'http://localhost:8002/api';

const USER_API_URL = isProduction
  ? 'https://user-service.fly.dev/api'
  : 'http://localhost:8003/api';

// Set up axios defaults for cookies
axios.defaults.withCredentials = true;

// Add console logging for debugging in production
const logRequest = (url) => {
  if (isProduction) {
    console.log(`Making API request to: ${url}`);
  }
};

export const fetchBikes = async () => {
  const url = `${PRODUCT_API_URL}/bikes`;
  logRequest(url);
  const response = await axios.get(url);
  return response.data;
};

export const fetchBike = async (bikeId) => {
  const url = `${PRODUCT_API_URL}/bikes/${bikeId}`;
  logRequest(url);
  const response = await axios.get(url);
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

export const uploadBikeImage = async (bikeId, imageFile, isMain = false) => {
  const formData = new FormData();
  formData.append('file', imageFile);
  formData.append('is_main', isMain);
  
  const url = `${PRODUCT_API_URL}/bikes/${bikeId}/images`;
  logRequest(url);
  
  const response = await axios.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    withCredentials: true,
  });
  
  return response.data;
};
