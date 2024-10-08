import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const fetchBikes = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/bikes`);
    return response.data;
  } catch (error) {
    console.error('Error fetching bikes:', error);
    throw error;
  }
};
