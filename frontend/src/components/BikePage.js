import React, { useEffect, useState, useContext } from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { fetchBike } from '../api';
import bikeStyles from '../bikeStyles';
import { CartContext } from '../CartContext';

const BikeContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: ${(props) => props.theme.spacing.medium};
  text-align: center;
  background-color: ${(props) => props.backgroundColor || props.theme.colors.light};
  border-radius: ${(props) => props.theme.borderRadius};
  box-shadow: ${(props) => props.theme.boxShadow};
`;

const BikeImage = styled.img`
  width: 100%;
  height: auto;
  margin: ${(props) => props.theme.spacing.small} 0;
  border-radius: ${(props) => props.theme.borderRadius};
  box-shadow: ${(props) => props.theme.boxShadow};
`;

const Description = styled.p`
  font-style: italic;
  color: ${(props) => props.color || props.theme.colors.text};
`;

const AddToCartButton = styled.button`
  background-color: ${(props) => props.theme.colors.primary};
  color: #fff;
  border: none;
  padding: ${(props) => props.theme.spacing.small};
  border-radius: ${(props) => props.theme.borderRadius};
  cursor: pointer;
  margin-top: ${(props) => props.theme.spacing.medium};

  &:hover {
    background-color: ${(props) => props.theme.colors.secondary};
  }
`;

const BikePage = () => {
  const { bikeId } = useParams();
  const [bike, setBike] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [addedToCart, setAddedToCart] = useState(false);
  const { addToCart } = useContext(CartContext);

  useEffect(() => {
    const getBike = async () => {
      try {
        const data = await fetchBike(bikeId);
        setBike(data);
        setAddedToCart(false);
      } catch (error) {
        console.error('Failed to fetch bike:', error);
        setError('Failed to load bike details');
      }
    };

    getBike();
  }, [bikeId]);

  const handleAddToCart = async () => {
    if (addedToCart) {
      alert('This item is already in the cart.');
      return;
    }

    setIsLoading(true);
    try {
      await addToCart(bike);
      setAddedToCart(true);
    } catch (error) {
      console.error('Failed to add to cart:', error);
      setError('Failed to add bike to cart');
    } finally {
      setIsLoading(false);
    }
  };

  // Helper function to generate correct image URLs
  const getImageUrl = (imagePath) => {
    if (!imagePath) return '/path/to/default-image.jpg';
    
    // For fully qualified URLs, use as-is
    if (imagePath.startsWith('http')) return imagePath;
    
    // For relative paths, ensure they start with a slash
    const path = imagePath.startsWith('/') ? imagePath : `/${imagePath}`;
    
    // Use the backend service URL without port number
    return `https://product-service.fly.dev${path}`;
  };

  if (error) {
    return <p>{error}</p>;
  }

  if (!bike) {
    return <p>Loading...</p>;
  }

  const bikeStyle = bikeStyles[bike.name.toLowerCase().replace(/\s+/g, '')] || {};

  return (
    <BikeContainer backgroundColor={bikeStyle.backgroundColor}>
      <h1>{bike.name}</h1>
      <p>{bike.description}</p>
      <p>${bike.price}</p>
      <AddToCartButton 
        onClick={handleAddToCart} 
        disabled={isLoading || addedToCart}
      >
        {isLoading ? 'Adding to Cart...' : addedToCart ? 'Added to Cart' : 'Add to Cart'}
      </AddToCartButton>
      {bikeStyle.additionalContent && (
        <Description color={bikeStyle.descriptionColor}>
          {bikeStyle.additionalContent}
        </Description>
      )}
      {bike.images.map((image) => (
        <BikeImage 
          key={image.id} 
          src={getImageUrl(image.image_url)} 
          alt={bike.name} 
        />
      ))}
    </BikeContainer>
  );
};

export default BikePage;