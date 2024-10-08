import React from 'react';
import styled from 'styled-components';

const FooterContainer = styled.footer`
  background-color: #333;
  color: #fff;
  padding: 20px;
  text-align: center;
  font-family: 'Roboto', sans-serif;
`;

const Footer = () => (
  <FooterContainer>
    <p>Follow us on social media!</p>
    <p>Newsletter Signup Placeholder</p>
  </FooterContainer>
);

export default Footer;