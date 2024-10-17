import { createGlobalStyle } from 'styled-components';

const GlobalStyle = createGlobalStyle`
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: ${(props) => props.theme.fonts.main};
    background-color: ${(props) => props.theme.colors.background};
    color: ${(props) => props.theme.colors.text};
    line-height: 1.6;
  }

  a {
    text-decoration: none;
    color: ${(props) => props.theme.colors.primary};
  }

  img {
    display: block;
    max-width: 100%;
  }
`;

export default GlobalStyle;