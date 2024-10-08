import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { fetchBikes } from '../api';

const ShopContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  padding: 20px;
`;

const ProductCard = styled.div`
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 10px;
  text-align: center;
`;

const ShopPage = () => {
  const [bikes, setBikes] = useState([]);

  useEffect(() => {
    const getBikes = async () => {
      try {
        const data = await fetchBikes();
        setBikes(data);
      } catch (error) {
        console.error('Failed to fetch bikes:', error);
      }
    };

    getBikes();
  }, []);

  return (
    <ShopContainer>
      {bikes.map(bike => (
        <ProductCard key={bike.id}>
          <img src="/path/to/placeholder-image.jpg" alt={bike.name} />
          <h3>{bike.name}</h3>
          <p>{bike.description}</p>
          <p>${bike.price}</p>
        </ProductCard>
      ))}
    </ShopContainer>
  );
};

export default ShopPage;