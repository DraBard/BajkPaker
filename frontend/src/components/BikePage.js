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
  const { addToCart } = useContext(CartContext);

  useEffect(() => {
    const getBike = async () => {
      try {
        const data = await fetchBike(bikeId);
        setBike(data);
      } catch (error) {
        console.error('Failed to fetch bike:', error);
      }
    };

    getBike();
  }, [bikeId]);

  if (!bike) {
    return <p>Loading...</p>;
  }

  const bikeStyle = bikeStyles[bike.name.toLowerCase().replace(/\s+/g, '')] || {};

  return (
    <BikeContainer backgroundColor={bikeStyle.backgroundColor}>
      <h1>{bike.name}</h1>
      <p>{bike.description}</p>
      <p>${bike.price}</p>
      {bikeStyle.additionalContent && (
        <Description color={bikeStyle.descriptionColor}>
          {bikeStyle.additionalContent}
        </Description>
      )}
      {bike.images.map((image) => (
        <BikeImage key={image.id} src={`http://localhost:8000${image.image_url}`} alt={bike.name} />
      ))}
      <AddToCartButton onClick={() => addToCart(bike)}>Add to Cart</AddToCartButton>
    </BikeContainer>
  );
};

export default BikePage;