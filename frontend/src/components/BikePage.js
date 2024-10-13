import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { fetchBike } from '../api';
import bikeStyles from '../bikeStyles';

const BikeContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
  background-color: ${(props) => props.backgroundColor || '#fff'};
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
`;

const BikeImage = styled.img`
  width: 100%;
  height: auto;
  margin: 10px 0;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
`;

const Description = styled.p`
  font-style: italic;
  color: ${(props) => props.color || '#333'};
`;

const BikePage = () => {
  const { bikeId } = useParams();
  const [bike, setBike] = useState(null);

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
    </BikeContainer>
  );
};

export default BikePage;