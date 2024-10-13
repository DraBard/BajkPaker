import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { fetchBike } from '../api';

const BikeContainer = styled.div`
  padding: 20px;
  text-align: center;
`;

const BikeImage = styled.img`
  max-width: 100%;
  height: auto;
  cursor: zoom-in;
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

  return (
    <BikeContainer>
      <h1>{bike.name}</h1>
      <p>{bike.description}</p>
      <p>${bike.price}</p>
      {bike.images.map((image) => (
        <BikeImage key={image.id} src={image.image_url} alt={bike.name} />
      ))}
    </BikeContainer>
  );
};

export default BikePage;