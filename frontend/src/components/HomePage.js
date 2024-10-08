import React from 'react';
import styled from 'styled-components';

const HeroSection = styled.section`
  background: url('/path/to/placeholder-image.jpg') no-repeat center center;
  background-size: cover;
  height: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #fff;
  font-family: 'Permanent Marker', cursive;
  font-size: 2em;
`;

const Introduction = styled.div`
  padding: 20px;
  font-family: 'Roboto', sans-serif;
`;

const HomePage = () => (
  <>
    <HeroSection>
      <h1>Ride in Style</h1>
    </HeroSection>
    <Introduction>
      <p>Welcome to Custom Bikes Shop, where we build bikes that match your style and personality.</p>
    </Introduction>
  </>
);

export default HomePage;