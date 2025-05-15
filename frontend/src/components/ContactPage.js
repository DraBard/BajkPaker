import React from 'react';
import styled from 'styled-components';

const ContactContainer = styled.div`
  padding: 20px;
  text-align: center;
`;

const ContactInfo = styled.div`
  margin-top: 20px;
  font-size: 18px;
`;

const ContactPage = () => (
  <ContactContainer>
    <h1>Kontakt</h1>
    <p>Kontaktujcie się śmiało w razie wątpliwości co do naszych bajków!</p>
    <ContactInfo>
      <p>Telefon: 501 325 559</p>
      <p>ul. Styczyńskiego 10/1</p>
    </ContactInfo>
  </ContactContainer>
);

export default ContactPage;