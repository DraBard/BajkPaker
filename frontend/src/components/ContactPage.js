import React from 'react';
import styled from 'styled-components';

const ContactForm = styled.form`
  display: flex;
  flex-direction: column;
  padding: 20px;
  font-family: 'Roboto', sans-serif;

  label {
    margin-bottom: 5px;
  }

  input, textarea {
    margin-bottom: 10px;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
  }
`;

const ContactPage = () => (
  <ContactForm>
    <label htmlFor="name">Name</label>
    <input type="text" id="name" name="name" />
    <label htmlFor="email">Email</label>
    <input type="email" id="email" name="email" />
    <label htmlFor="message">Message</label>
    <textarea id="message" name="message" rows="4"></textarea>
    <button type="submit">Send</button>
  </ContactForm>
);

export default ContactPage;