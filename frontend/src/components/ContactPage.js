import React from 'react';
import styled from 'styled-components';

const ContactContainer = styled.div`
  padding: 20px;
  text-align: center;
`;

const ContactPage = () => (
  <ContactContainer>
    <h1>Contact Us</h1>
    <p>Feel free to reach out to us with any questions or concerns.</p>
  </ContactContainer>
);

export default ContactPage;