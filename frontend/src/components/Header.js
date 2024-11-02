import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { FaShoppingCart, FaHome, FaStore, FaInfoCircle, FaEnvelope, FaRecycle } from 'react-icons/fa';

const NavBar = styled.nav`
  background-color: ${props => props.theme.colors.light};
  padding: ${props => props.theme.spacing.medium};
  box-shadow: ${props => props.theme.boxShadow};
  position: sticky;
  top: 0;
  z-index: 1000;
`;

const NavContent = styled.div`
  max-width: ${props => props.theme.breakpoints.wide};
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Logo = styled(Link)`
  font-family: ${props => props.theme.typography.headingFamily};
  font-size: ${props => props.theme.typography.sizes.xlarge};
  font-weight: 700;
  color: ${props => props.theme.colors.primary};
  
  &:hover {
    transform: scale(1.05);
  }
`;

const NavLinks = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.medium};
  align-items: center;
`;

const NavLink = styled(Link)`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.small};
  color: ${props => props.theme.colors.text};
  font-weight: 500;
  padding: ${props => props.theme.spacing.small};
  border-radius: ${props => props.theme.borderRadius};

  &:hover {
    background-color: ${props => props.theme.colors.background};
    color: ${props => props.theme.colors.primary};
    transform: translateY(-2px);
  }

  svg {
    font-size: 1.2em;
  }
`;

const Header = () => (
  <NavBar>
    <NavContent>
      <Logo to="/">BajkPaker</Logo>
      <NavLinks>
        <NavLink to="/"><FaHome /> Home</NavLink>
        <NavLink to="/shop"><FaStore /> Shop</NavLink>
        <NavLink to="/about"><FaInfoCircle /> About</NavLink>
        <NavLink to="/contact"><FaEnvelope /> Contact</NavLink>
        <NavLink to="/revived"><FaRecycle /> Revived</NavLink>
        <NavLink to="/cart"><FaShoppingCart /> Cart</NavLink>
      </NavLinks>
    </NavContent>
  </NavBar>
);

export default Header;