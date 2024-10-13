import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

const NavBar = styled.nav`
  background-color: #ff6347;
  padding: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const NavLinks = styled.div`
  a {
    color: #fff;
    margin: 0 10px;
    text-decoration: none;
    font-family: 'Permanent Marker', cursive;

    &:hover {
      text-decoration: underline;
    }
  }
`;

const Header = () => (
  <NavBar>
    <h1>BajkPaker</h1>
    <NavLinks>
      <Link to="/">Home</Link>
      <Link to="/shop">Shop</Link>
      <Link to="/about">About Us</Link>
      <Link to="/contact">Contact</Link>
    </NavLinks>
  </NavBar>
);

export default Header;