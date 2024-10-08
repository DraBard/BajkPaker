import React from 'react';
import styled from 'styled-components';

const AboutContainer = styled.div`
  padding: 20px;
  font-family: 'Roboto', sans-serif;
`;

const AboutPage = () => (
  <AboutContainer>
    <h2>About Us</h2>
    <p>Our story began in a small garage...</p>
    {/* Add more content as needed */}
  </AboutContainer>
);

export default AboutPage;