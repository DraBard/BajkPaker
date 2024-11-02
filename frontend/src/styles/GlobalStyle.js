import { createGlobalStyle } from 'styled-components';

const GlobalStyle = createGlobalStyle`
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@500;600;700&display=swap');

  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: ${props => props.theme.typography.fontFamily};
    background-color: ${props => props.theme.colors.background};
    color: ${props => props.theme.colors.text};
    line-height: 1.6;
  }

  h1, h2, h3, h4, h5, h6 {
    font-family: ${props => props.theme.typography.headingFamily};
    font-weight: 600;
    margin-bottom: ${props => props.theme.spacing.medium};
  }

  a {
    text-decoration: none;
    color: inherit;
    transition: ${props => props.theme.transitions.default};
  }

  button {
    font-family: ${props => props.theme.typography.fontFamily};
    transition: ${props => props.theme.transitions.default};
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