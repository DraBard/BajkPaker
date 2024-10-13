import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import { fetchBikes } from '../api';

const ShopContainer = styled.div`
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
      {bikes.map(bike => {
        const mainImage = bike.images.find(image => image.is_main);
        return (
          <Link to={`/shop/${bike.id}`} key={bike.id}>
            <ProductCard>
              <img src={mainImage ? `http://localhost:8000${mainImage.image_url}` : '/path/to/default-image.jpg'} alt={bike.name} />
              <h3>{bike.name}</h3>
              <p>${bike.price}</p>
            </ProductCard>
          </Link>
        );
      })}
    </ShopContainer>
  );
};

export default ShopPage;