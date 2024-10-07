import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from './api';


function App() {
  const [bikes, setBikes] = useState([]);

  useEffect(() => {
    axios.get(`${API_BASE_URL}/api/bikes`).then(response => {
      setBikes(response.data);
    }).catch(error => {
      console.error('There was an error fetching the bikes!', error);
    });
  }, []);

  return (
    <div>
      <h1>Custom Bikes Shop</h1>
      <ul>
        {bikes.map(bike => (
          <li key={bike.id}>{bike.name} - ${bike.price}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;