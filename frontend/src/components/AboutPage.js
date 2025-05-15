import React from 'react';
import styled from 'styled-components';

const AboutContainer = styled.div`
  padding: 20px;
  text-align: center;
`;

const AboutPage = () => (
  <AboutContainer>
    <h1>O Nas</h1>
    <p>Jesteśmy firmą, która tworzy rowery rzemieślnicze, jedyne w swoim rodzaju. Mamy pasję do tworzenia oryginalnych, tematycznych rowerów z sakwami.</p>
  </AboutContainer>
);

export default AboutPage;