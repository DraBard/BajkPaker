import { createGlobalStyle } from 'styled-components';

const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    -webkit-tap-highlight-color: transparent;
  }

  html {
    font-size: 16px;
    ${props => props.theme.mediaQueries.mobile} {
      font-size: 14px;
    }
  }

  body {
    font-family: ${props => props.theme.typography.fontFamily};
    background-color: ${props => props.theme.colors.background};
    color: ${props => props.theme.colors.text};
    line-height: 1.6;
    min-height: 100vh;
    position: relative;
    padding-bottom: 60px; /* Space for footer */
  }

  h1, h2, h3, h4, h5, h6 {
    font-family: ${props => props.theme.typography.headingFamily};
    font-weight: 600;
    margin-bottom: ${props => props.theme.spacing.medium};
    
    ${props => props.theme.mediaQueries.mobile} {
      margin-bottom: ${props => props.theme.spacing.small};
    }
  }

  h1 {
    font-size: ${props => props.theme.typography.sizes.xxlarge};
    ${props => props.theme.mediaQueries.mobile} {
      font-size: ${props => props.theme.typography.mobileSizes.xxlarge};
    }
  }

  h2 {
    font-size: ${props => props.theme.typography.sizes.xlarge};
    ${props => props.theme.mediaQueries.mobile} {
      font-size: ${props => props.theme.typography.mobileSizes.xlarge};
    }
  }

  a {
    text-decoration: none;
    color: inherit;
    transition: ${props => props.theme.transitions.default};
  }

  button {
    font-family: ${props => props.theme.typography.fontFamily};
    transition: ${props => props.theme.transitions.default};
    cursor: pointer;
    font-size: 1rem;
    
    ${props => props.theme.mediaQueries.mobile} {
      font-size: 1.1rem;
      padding: 8px 12px; /* Larger touch targets for mobile */
    }
  }

  input, select, textarea {
    font-family: ${props => props.theme.typography.fontFamily};
    font-size: 1rem;
    
    ${props => props.theme.mediaQueries.mobile} {
      font-size: 16px; /* Prevent zoom on iOS */
      padding: 10px;
    }
  }

  img {
    max-width: 100%;
    height: auto;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;

export default GlobalStyle;