import React, { useContext, useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { FaShoppingCart, FaHome, FaStore, FaInfoCircle, FaEnvelope, FaRecycle, FaUserPlus, FaBars, FaTimes, FaTools } from 'react-icons/fa';
import { CartContext } from '../CartContext';

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
  position: relative;
`;

const Logo = styled(Link)`
  font-family: ${props => props.theme.typography.headingFamily};
  font-size: ${props => props.theme.typography.sizes.xlarge};
  font-weight: 700;
  color: ${props => props.theme.colors.primary};
  
  &:hover {
    transform: scale(1.05);
  }

  ${props => props.theme.mediaQueries.mobile} {
    font-size: 2.2rem; /* Further increased size for better visibility on mobile */
    z-index: 1001; // Ensure logo stays above the menu
  }
`;

const NavLinks = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.medium};
  align-items: center;

  ${props => props.theme.mediaQueries.touch} {
    flex-direction: column;
    position: fixed;
    top: 0;
    right: ${props => (props.isOpen ? '0' : '-100%')};
    width: 85%; /* Increased width for better visibility */
    max-width: 350px; /* Increased max-width */
    height: 100vh;
    background-color: ${props => props.theme.colors.light};
    padding-top: 80px; /* Increased padding */
    padding-bottom: 30px;
    transition: right 0.3s ease-in-out;
    box-shadow: ${props => (props.isOpen ? '-8px 0 15px rgba(0, 0, 0, 0.2)' : 'none')}; /* Enhanced shadow */
    gap: ${props => props.theme.spacing.large};
    overflow-y: auto;
    z-index: 1000;
  }
`;

const NavLink = styled(Link)`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.small};
  color: ${props => props.isActive ? props.theme.colors.primary : props.theme.colors.text};
  font-weight: ${props => props.isActive ? '700' : '500'};
  padding: ${props => props.theme.spacing.small};
  border-radius: ${props => props.theme.borderRadius};
  transition: all ${props => props.theme.transitions.fast};

  &:hover {
    background-color: ${props => props.theme.colors.background};
    color: ${props => props.theme.colors.primary};
    transform: translateY(-2px);
  }

  svg {
    font-size: 1.2em;
  }

  ${props => props.theme.mediaQueries.touch} {
    width: 100%;
    padding: ${props => props.theme.spacing.large} ${props => props.theme.spacing.medium}; /* Significantly increased padding for touch targets */
    font-size: 1.2rem; /* Larger font size */
    justify-content: flex-start;
    border-bottom: 1px solid rgba(0,0,0,0.07); /* Visual separator */
    margin-bottom: 5px;
    
    svg {
      font-size: 1.8em; /* Larger icons */
      margin-right: 15px; /* More space between icon and text */
    }
    
    &:active {
      background-color: ${props => props.theme.colors.background};
    }
  }
`;

const CartIconContainer = styled.div`
  position: relative;
  display: inline-block;
  margin-right: 5px;
`;

const CartBadge = styled.span`
  position: absolute;
  top: -10px;
  right: -10px;
  background-color: red;
  color: white;
  border-radius: 50%;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  font-weight: bold;

  ${props => props.theme.mediaQueries.touch} {
    top: -5px;
    right: -5px;
    padding: 0.2rem 0.4rem;
  }
`;

const HamburgerButton = styled.button`
  display: none;
  background: none;
  border: none;
  color: ${props => props.theme.colors.hamburger};
  font-size: 2rem; /* Larger icon */
  cursor: pointer;
  z-index: 1001;
  padding: 10px; /* Increased touch target */
  
  ${props => props.theme.mediaQueries.touch} {
    display: block;
    font-size: 3rem; /* Increased from 2rem for better visibility */
    padding: 15px; /* Increased from 10px for larger touch target */
  }
`;

const Overlay = styled.div`
  display: none;
  
  ${props => props.theme.mediaQueries.touch} {
    display: ${props => props.isOpen ? 'block' : 'none'};
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.6); /* Darker overlay for better contrast */
    z-index: 999;
  }
`;

const Header = () => {
  const { cart } = useContext(CartContext);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const cartItemCount = cart.reduce((total, item) => total + item.quantity, 0);
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path;
  };

  // Close menu when route changes
  useEffect(() => {
    setIsMenuOpen(false);
  }, [location]);

  // Prevent body scroll when menu is open
  useEffect(() => {
    if (isMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'visible';
    }
    
    return () => {
      document.body.style.overflow = 'visible';
    };
  }, [isMenuOpen]);

  return (
    <NavBar>
      <NavContent>
        <Logo to="/">BajkPaker</Logo>
        
        <HamburgerButton onClick={() => setIsMenuOpen(!isMenuOpen)} aria-label="Toggle menu">
          {isMenuOpen ? <FaTimes /> : <FaBars />}
        </HamburgerButton>
        
        <Overlay isOpen={isMenuOpen} onClick={() => setIsMenuOpen(false)} />
        
        <NavLinks isOpen={isMenuOpen}>
          <NavLink to="/" isActive={isActive('/')} onClick={() => setIsMenuOpen(false)}>
            <FaHome />Strona Główna
          </NavLink>
          <NavLink to="/shop" isActive={isActive('/shop')} onClick={() => setIsMenuOpen(false)}>
            <FaStore />Sklep
          </NavLink>
          <NavLink to="/revived" isActive={isActive('/revived')} onClick={() => setIsMenuOpen(false)}>
            <FaRecycle />Wskrzeszone
          </NavLink>
          <NavLink to="/custom-bike" isActive={isActive('/custom-bike')} onClick={() => setIsMenuOpen(false)}>
            <FaTools />Twój Projekt
          </NavLink>
          <NavLink to="/about" isActive={isActive('/about')} onClick={() => setIsMenuOpen(false)}>
            <FaInfoCircle />O nas
          </NavLink>
          <NavLink to="/contact" isActive={isActive('/contact')} onClick={() => setIsMenuOpen(false)}>
            <FaEnvelope />Kontakt
          </NavLink>
          <NavLink to="/cart" isActive={isActive('/cart')} onClick={() => setIsMenuOpen(false)}>
            <CartIconContainer>
              <FaShoppingCart />
              {cartItemCount > 0 && <CartBadge>{cartItemCount}</CartBadge>}
            </CartIconContainer>
            Koszyk
          </NavLink>
          {/* <NavLink to="/auth" isActive={isActive('/auth')} onClick={() => setIsMenuOpen(false)}>
            <FaUserPlus /> Login
          </NavLink> */}
        </NavLinks>
      </NavContent>
    </NavBar>
  );
};

export default Header;