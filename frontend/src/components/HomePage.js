import React from 'react';
import styled from 'styled-components';

const HomeContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 80vh;
  text-align: center;
  padding: 20px;
`;

const HomePage = () => (
  <HomeContainer>
    <h1>Witaj w BajkPakerze</h1>
    <p>Rowery rzemieślnicze pod projekt własny</p>
  </HomeContainer>
);

export default HomePage;