import React from 'react';
import { useParams } from 'react-router-dom';
import { fetchBike } from '../api';
import BikeDetails from './BikeDetails';

const BikePage = () => {
  const { bikeId } = useParams();
  return (
    <BikeDetails
      bikeId={bikeId}
      fetchBikeFn={fetchBike}
      allowAddToCart={true}
    />
  );
};

export default BikePage;