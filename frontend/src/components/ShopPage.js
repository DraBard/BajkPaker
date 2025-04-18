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

const FallbackImage = styled.div`
  width: 100%;
  height: 200px;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-style: italic;
  margin-bottom: 10px;
`;

const ShopPage = () => {
  const [bikes, setBikes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [imageErrors, setImageErrors] = useState({});

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

  const getImageUrl = (imagePath) => {
    // Return default image if no path provided
    if (!imagePath) return DEFAULT_IMAGE_PATH;
    
    // For fully qualified URLs, use as-is
    if (imagePath.startsWith('http')) return imagePath;
    
    // For relative paths, ensure they start with a slash
    const path = imagePath.startsWith('/') ? imagePath : `/${imagePath}`;
    
    // Check for development environment using window.location
    const isDevelopment = window.location.hostname === 'localhost' || 
                          window.location.hostname === '127.0.0.1';
    
    // Extract the filename from the path
    const filename = path.split('/').pop();
    
    // Use only the filename in development, otherwise use the full URL
    return isDevelopment
      ? `/images/${filename}`
      : `https://product-service.fly.dev${path}`;
  };

  const handleImageError = (bikeId) => {
    console.error(`Failed to load image for bike ID: ${bikeId}`);
    setImageErrors(prev => ({
      ...prev,
      [bikeId]: true
    }));
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
              {imageErrors[bike.id] ? (
                <FallbackImage>Image not available</FallbackImage>
              ) : (
                <img 
                  src={imageUrl} 
                  alt={bike.name} 
                  onError={() => handleImageError(bike.id)}
                />
              )}
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