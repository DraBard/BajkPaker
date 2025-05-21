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

// Enhanced logging function with method and data parameters
const logRequest = (url, method = 'GET', data = null) => {
  console.log(`Making API ${method} request to: ${url}`);
  if (data) console.log('Request data:', data);
};

export const fetchBikes = async () => {
  const url = `${PRODUCT_API_URL}/bikes`;
  logRequest(url);
  const response = await axios.get(url);
  return response.data;
};

export const fetchRevivedBikes = async () => {
  const url = `${PRODUCT_API_URL}/bikes/revived`;
  logRequest(url);
  const response = await axios.get(url);
  return response.data;
};

export const fetchRevivedBike = async (bikeId) => {
  const url = `${PRODUCT_API_URL}/bikes/revived/${bikeId}`;
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
  try {
    const url = `${ORDER_API_URL}/cart`;
    logRequest(url, 'POST', cartItem);
    console.log('API sending to cart:', cartItem);
    console.log('Full URL:', url);
    
    // Check server availability before making actual request
    try {
      await axios.options(ORDER_API_URL, { timeout: 2000 });
    } catch (healthError) {
      console.error('Order service health check failed:', healthError);
      alert('Order service appears to be unavailable. Please try again later.');
      throw new Error('Order service unavailable');
    }
    
    const response = await axios.post(url, cartItem, {
      withCredentials: true,
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 10000 // 10 second timeout
    });
    
    console.log('Cart API response status:', response.status);
    console.log('Cart API response data:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error adding to cart:', error);
    if (error.response) {
      console.error('Error response data:', error.response.data);
      console.error('Error response status:', error.response.status);
      console.error('Error response headers:', error.response.headers);
    } else if (error.request) {
      console.error('Error request (no response received):', error.request);
      alert('Unable to reach order service. Please check your connection and try again.');
    } else {
      console.error('Error message:', error.message);
    }
    throw error;
  }
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

