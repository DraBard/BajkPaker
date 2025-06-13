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
  z-index: 10;

  ${props => props.theme.mediaQueries.mobile} {
    padding: 15px 10px;
  }
`;

const TermsLink = styled.span`
  color: #fff;
  text-decoration: underline;
  cursor: pointer;
  margin-left: 10px;

  ${props => props.theme.mediaQueries.mobile} {
    display: block;
    margin-top: 5px;
    margin-left: 0;
  }
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