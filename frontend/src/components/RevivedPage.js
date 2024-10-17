// frontend/src/components/RevivedPage.js

import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { fetchBikes } from '../api';

const RevivedContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 20px;
  padding: 20px;
`;

const ProductCard = styled.div`
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 10px;
  text-align: center;
  transition: transform 0.2s;

  &:hover {
    transform: scale(1.05);
  }

  img {
    max-width: 100%;
    height: auto;
    border-bottom: 1px solid #ddd;
    margin-bottom: 10px;
  }

  h3 {
    font-size: 1.2em;
    margin: 10px 0;
  }

  p {
    margin: 5px 0;
  }
`;

const RevivedPage = () => {
  const [bike, setBike] = useState(null);

  useEffect(() => {
    const getBikes = async () => {
      try {
        const data = await fetchBikes();
        if (data.length > 0) {
          setBike(data[0]);
        }
      } catch (error) {
        console.error('Failed to fetch bikes:', error);
      }
    };

    getBikes();
  }, []);

  if (!bike) {
    return <p>No bike available in the revived section.</p>;
  }

  const mainImage = bike.images.find(image => image.is_main);

  return (
    <RevivedContainer>
      <ProductCard>
        <img src={mainImage ? `http://localhost:8000${mainImage.image_url}` : '/path/to/default-image.jpg'} alt={bike.name} />
        <h3>{bike.name}</h3>
        <p>${bike.price}</p>
      </ProductCard>
    </RevivedContainer>
  );
};

export default RevivedPage;