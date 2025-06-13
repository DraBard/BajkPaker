const theme = {
  colors: {
    primary: '#FF4B4B',
    secondary: '#2D3436',
    accent: '#00B894',
    light: '#FFFFFF',
    dark: '#1E272E',
    background: '#F5F6FA',
    text: '#2D3436',
    error: '#FF7675',
    success: '#00B894',
    hamburger: '#333333'
  },
  spacing: {
    small: '0.5rem',
    medium: '1rem',
    large: '2rem',
    xlarge: '4rem'
  },
  typography: {
    fontFamily: "'Inter', sans-serif",
    headingFamily: "'Montserrat', sans-serif",
    sizes: {
      small: '0.875rem',
      medium: '1rem',
      large: '1.25rem',
      xlarge: '1.5rem',
      xxlarge: '2rem'
    },
    mobileSizes: {
      small: '0.75rem',
      medium: '0.9rem',
      large: '1.125rem',
      xlarge: '1.35rem',
      xxlarge: '1.75rem'
    }
  },
  borderRadius: '8px',
  boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
  transitions: {
    default: '0.3s ease',
    fast: '0.15s ease',
    slow: '0.5s ease'
  },
  breakpoints: {
    mobile: '320px',
    tablet: '768px',
    desktop: '1024px',
    wide: '1280px'
  },
  mediaQueries: {
    mobile: '@media (max-width: 767px)',
    tablet: '@media (min-width: 768px) and (max-width: 1023px)',
    desktop: '@media (min-width: 1024px)',
    touch: '@media (max-width: 1023px)'
  }
};

export default theme;