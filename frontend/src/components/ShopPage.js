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
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getBikes = async () => {
      try {
        setIsLoading(true);
        const data = await fetchBikes();
        setBikes(data);
      } catch (error) {
        console.error('Failed to fetch bikes:', error);
        setError('Failed to load bikes. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    getBikes();
  }, []);

  if (isLoading) {
    return <p>Loading bikes...</p>;
  }

  if (error) {
    return <p>{error}</p>;
  }

  if (bikes.length === 0) {
    return <p>No bikes available for purchase.</p>;
  }

  // Helper function to generate correct image URLs
  const getImageUrl = (imagePath) => {
    // Remove any port number from the URL and handle relative paths
    return imagePath.startsWith('http') 
      ? imagePath 
      : `https://product-service.fly.dev${imagePath}`;
  };

  return (
    <ShopContainer>
      {bikes.map((bike) => {
        const mainImage = bike.images.find(image => image.is_main);
        const imageUrl = mainImage 
          ? getImageUrl(mainImage.image_url)
          : '/path/to/default-image.jpg';
        
        return (
          <Link to={`/shop/${bike.id}`} key={bike.id}>
            <ProductCard>
              <img src={imageUrl} alt={bike.name} />
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