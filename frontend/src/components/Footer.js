import React from 'react';
import styled from 'styled-components';

const FooterContainer = styled.footer`
  background-color: #333;
  color: #fff;
  text-align: center;
  padding: 20px;
  position: fixed;
  bottom: 0;
  width: 100%;
`;

const TermsLink = styled.span`
  color: #fff;
  text-decoration: underline;
  cursor: pointer;
  margin-left: 10px;
`;

const Footer = ({ onOpenTerms }) => (
  <FooterContainer>
    <p>
      &copy; {new Date().getFullYear()} BajkPaker. All rights reserved.
      {onOpenTerms && <TermsLink onClick={onOpenTerms}>Regulamin</TermsLink>}
    </p>
  </FooterContainer>
);

export default Footer;