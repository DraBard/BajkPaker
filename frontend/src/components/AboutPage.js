import React from 'react';
import styled from 'styled-components';

const AboutContainer = styled.div`
  padding: 20px;
  text-align: center;
`;

const AboutPage = () => (
  <AboutContainer>
    <h1>About Us</h1>
    <p>We are passionate about custom bikes and providing the best service to our customers.</p>
  </AboutContainer>
);

export default AboutPage;