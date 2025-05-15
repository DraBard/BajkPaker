import React from 'react';
import { useParams } from 'react-router-dom';
import { fetchRevivedBike } from '../api';
import BikeDetails from './BikeDetails';

const RevivedDetailsPage = () => {
  const { id } = useParams();
  return (
    <BikeDetails
      bikeId={id}
      fetchBikeFn={fetchRevivedBike}
      allowAddToCart={false}
      boughtMessage="Ten rower został już kupiony."
    />
  );
};

export default RevivedDetailsPage;
