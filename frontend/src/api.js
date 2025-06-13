import axios from 'axios';

// Define API URLs based on environment
const isProduction = process.env.NODE_ENV === 'production';

const PRODUCT_API_URL = isProduction
  ? 'https://product-service.fly.dev/api'
  : 'http://localhost:8001/api';

const ORDER_API_URL = isProduction
  ? 'https://order-processing-service.fly.dev/api'
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
      throw new Error('Order service appears to be unavailable. Please try again later.');
    }
    
    const response = await axios.post(url, cartItem, {
      withCredentials: true,
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 15000 // 15 second timeout (increased from 10)
    });
    
    console.log('Cart API response status:', response.status);
    console.log('Cart API response data:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error adding to cart:', error);
    
    // More detailed error logging
    if (error.response) {
      console.error('Error response data:', error.response.data);
      console.error('Error response status:', error.response.status);
      console.error('Error response headers:', error.response.headers);
      
      // If the error is due to bike not found in product service, make it clear
      if (error.response.status === 404 || 
          (error.response.data && error.response.data.detail && 
           error.response.data.detail.includes('not found in product service'))) {
        throw new Error('The requested bike is currently unavailable or out of stock.');
      }
    } else if (error.request) {
      console.error('Error request (no response received):', error.request);
      throw new Error('Unable to reach the server. Please check your connection and try again.');
    }
    
    throw error;
  }
};

export const fetchCart = async () => {
  try {
    // Create a cancel token with a unique identifier
    const source = axios.CancelToken.source();
    
    // Set a longer timeout to avoid quick retries and reduce spam
    const timeoutId = setTimeout(() => {
      source.cancel('Request timeout');
    }, 15000); // 15-second timeout
    
    console.log('Fetching cart data from API...');
    const response = await axios.get(`${ORDER_API_URL}/cart`, { 
      withCredentials: true,
      cancelToken: source.token,
      headers: {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Accept': 'application/json'
      },
      // Add retry count as a query param for debugging
      params: {
        _t: new Date().getTime() // Cache busting
      }
    });
    
    clearTimeout(timeoutId);
    console.log('Cart fetch successful:', response.data);
    return response.data;
  } catch (error) {
    // Don't throw if request was cancelled - prevents retry loops
    if (axios.isCancel(error)) {
      console.log('Request cancelled:', error.message);
      return [];
    }
    
    // For CORS or network errors, return empty array instead of throwing
    if (error.message && (error.message.includes('Network') || error.message.includes('CORS'))) {
      console.error('CORS or Network error fetching cart:', error.message);
      // Return empty array instead of throwing to prevent retry spam
      return [];
    }
    
    // Rethrow other errors
    console.error('Error in fetchCart:', error);
    throw error;
  }
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

export const submitCustomBikeOrder = async (customBikeData) => {
  const url = `${ORDER_API_URL}/custom-bikes`;
  logRequest(url, 'POST', customBikeData);
  const response = await axios.post(url, customBikeData, { 
    withCredentials: true,
    headers: {
      'Content-Type': 'application/json'
    },
  });
  return response.data;
};

