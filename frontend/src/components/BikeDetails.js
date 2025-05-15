import React, { useEffect, useState, useContext, useRef } from 'react';
import styled from 'styled-components';
import bikeStyles from '../bikeStyles';
import { CartContext } from '../CartContext';
import { FaChevronLeft, FaChevronRight } from 'react-icons/fa';

const BikeContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: ${(props) => props.theme.spacing.medium};
  text-align: center;
  background-color: ${(props) => props.backgroundColor || props.theme.colors.light};
  border-radius: ${(props) => props.theme.borderRadius};
  box-shadow: ${(props) => props.theme.boxShadow};
`;

const BikeImage = styled.img`
  width: 100%;
  height: auto;
  margin: ${(props) => props.theme.spacing.small} 0;
  border-radius: ${(props) => props.theme.borderRadius};
  box-shadow: ${(props) => props.theme.boxShadow};
`;

const FallbackImage = styled.div`
  width: 100%;
  height: 300px;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-style: italic;
  margin: ${(props) => props.theme.spacing.small} 0;
  border-radius: ${(props) => props.theme.borderRadius};
  box-shadow: ${(props) => props.theme.boxShadow};
`;

const Description = styled.p`
  font-style: italic;
  color: ${(props) => props.color || props.theme.colors.text};
`;

const AddToCartButton = styled.button`
  background-color: ${(props) => props.theme.colors.primary};
  color: #fff;
  border: none;
  padding: ${(props) => props.theme.spacing.small};
  border-radius: ${(props) => props.theme.borderRadius};
  cursor: pointer;
  margin-top: ${(props) => props.theme.spacing.medium};

  &:hover {
    background-color: ${(props) => props.theme.colors.secondary};
  }
`;

const CarouselContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 20px 0;
`;

const ArrowButton = styled.button`
  background: none;
  border: none;
  color: #333;
  font-size: 2rem;
  cursor: pointer;
  padding: 0 10px;
  transition: color 0.2s;
  &:disabled {
    color: #ccc;
    cursor: not-allowed;
  }
`;

const Magnifier = styled.div`
  position: absolute;
  pointer-events: none;
  border: 2px solid #aaa;
  border-radius: 50%;
  width: 120px;
  height: 120px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  background-repeat: no-repeat;
  background-size: ${({ zoom, imgWidth, imgHeight }) =>
    `${imgWidth * zoom}px ${imgHeight * zoom}px`};
  background-position: ${({ bgX, bgY }) => `${bgX}px ${bgY}px`};
  left: ${({ x }) => `${x - 60}px`};
  top: ${({ y }) => `${y - 60}px`};
  z-index: 10;
  display: ${({ visible }) => (visible ? 'block' : 'none')};
`;

const BikeImageWrapper = styled.div`
  position: relative;
  display: inline-block;
  width: 100%;
  max-width: 500px;
`;

const ModalOverlay = styled.div`
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const ModalContent = styled.div`
  position: relative;
  background: #fff;
  border-radius: ${(props) => props.theme.borderRadius};
  padding: 24px;
  max-width: 90vw;
  max-height: 90vh;
  box-shadow: ${(props) => props.theme.boxShadow};
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const ModalClose = styled.button`
  position: absolute;
  top: 8px;
  right: 8px;
  background: #eee;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  font-size: 1.5rem;
  cursor: pointer;
  z-index: 10;
`;

const DEFAULT_IMAGE_PATH = '/placeholder-bike.jpg';

const BikeDetails = ({
  bikeId,
  fetchBikeFn,
  allowAddToCart = true,
  boughtMessage = null,
}) => {
  const [bike, setBike] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [addedToCart, setAddedToCart] = useState(false);
  const [imageErrors, setImageErrors] = useState({});
  const [currentImageIdx, setCurrentImageIdx] = useState(0);
  const { addToCart } = useContext(CartContext);

  const [modalOpen, setModalOpen] = useState(false);
  const [modalMagnifierVisible, setModalMagnifierVisible] = useState(false);
  const [modalMagnifierPos, setModalMagnifierPos] = useState({ x: 0, y: 0 });
  const [modalImgSize, setModalImgSize] = useState({ width: 0, height: 0 });
  const modalImgRef = useRef(null);
  const MAGNIFIER_ZOOM = 2;

  useEffect(() => {
    const getBike = async () => {
      try {
        setIsLoading(true);
        const data = await fetchBikeFn(bikeId);
        setBike(data);
        setAddedToCart(false);
        setCurrentImageIdx(0);
      } catch (error) {
        console.error('Failed to fetch bike:', error);
        setError('Failed to load bike details');
      } finally {
        setIsLoading(false);
      }
    };

    getBike();
  }, [bikeId, fetchBikeFn]);

  const handleAddToCart = async () => {
    if (addedToCart) {
      alert('This item is already in the cart.');
      return;
    }

    setIsLoading(true);
    try {
      await addToCart(bike);
      setAddedToCart(true);
    } catch (error) {
      console.error('Failed to add to cart:', error);
      setError('Failed to add bike to cart');
    } finally {
      setIsLoading(false);
    }
  };

  const getImageUrl = (imagePath) => {
    if (!imagePath) return DEFAULT_IMAGE_PATH;
    if (imagePath.startsWith('http')) return imagePath;
    const path = imagePath.startsWith('/') ? imagePath : `/${imagePath}`;
    const isDevelopment = window.location.hostname === 'localhost' || 
                           window.location.hostname === '127.0.0.1';
    const filename = path.split('/').pop();
    return isDevelopment 
      ? `/images/${filename}` 
      : `https://product-service.fly.dev${path}`;
  };
  
  const handleImageError = (imageId) => {
    setImageErrors(prev => ({
      ...prev,
      [imageId]: true
    }));
  };

  const handleModalMouseMove = (e) => {
    if (!modalImgRef.current) return;
    const rect = modalImgRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setModalMagnifierPos({ x, y });
  };

  const handleModalImageLoad = (e) => {
    setModalImgSize({
      width: e.target.offsetWidth,
      height: e.target.offsetHeight,
    });
  };

  const closeModal = () => {
    setModalOpen(false);
    setModalMagnifierVisible(false);
  };

  if (error) {
    return <p>{error}</p>;
  }

  if (!bike) {
    return <p>Loading...</p>;
  }

  const bikeStyle = bikeStyles[bike.name.toLowerCase().replace(/\s+/g, '')] || {};
  const images = bike.images || [];
  const showImage = images[currentImageIdx];

  return (
    <BikeContainer backgroundColor={bikeStyle.backgroundColor}>
      <h1>{bike.name}</h1>
      <p>{bike.description}</p>
      <p>{bike.price} PLN</p>
      {allowAddToCart && (
        <AddToCartButton 
          onClick={handleAddToCart} 
          disabled={isLoading || addedToCart}
        >
          {isLoading ? 'Adding to Cart...' : addedToCart ? 'Added to Cart' : 'Add to Cart'}
        </AddToCartButton>
      )}
        {!allowAddToCart && boughtMessage && (
        <p><strong>{boughtMessage}</strong></p>
        )}
      {bikeStyle.additionalContent && (
        <Description color={bikeStyle.descriptionColor}>
          {bikeStyle.additionalContent}
        </Description>
      )}
      {images.length > 0 && (
        <CarouselContainer>
          <ArrowButton
            onClick={() => setCurrentImageIdx((idx) => Math.max(idx - 1, 0))}
            disabled={currentImageIdx === 0}
            aria-label="Previous image"
          >
            <FaChevronLeft />
          </ArrowButton>
          <BikeImageWrapper>
            {imageErrors[showImage.id] ? (
              <img
                src={DEFAULT_IMAGE_PATH}
                alt="placeholder"
                style={{ width: '100%', height: '300px', objectFit: 'cover' }}
              />
            ) : (
              <>
                <BikeImage
                  key={showImage.id}
                  src={getImageUrl(showImage.image_url)}
                  alt={bike.name}
                  onError={() => handleImageError(showImage.id)}
                  style={{ cursor: 'default' }}
                  onClick={() => setModalOpen(true)}
                />
              </>
            )}
          </BikeImageWrapper>
          <ArrowButton
            onClick={() => setCurrentImageIdx((idx) => Math.min(idx + 1, images.length - 1))}
            disabled={currentImageIdx === images.length - 1}
            aria-label="Next image"
          >
            <FaChevronRight />
          </ArrowButton>
        </CarouselContainer>
      )}
      {modalOpen && (
        <ModalOverlay onClick={closeModal}>
          <ModalContent onClick={e => e.stopPropagation()}>
            <ModalClose onClick={closeModal} aria-label="Close">&times;</ModalClose>
            <BikeImageWrapper style={{ maxWidth: '80vw', maxHeight: '80vh' }}>
              <BikeImage
                ref={modalImgRef}
                src={getImageUrl(showImage.image_url)}
                alt={bike.name}
                onLoad={handleModalImageLoad}
                onMouseEnter={() => setModalMagnifierVisible(true)}
                onMouseLeave={() => setModalMagnifierVisible(false)}
                onMouseMove={handleModalMouseMove}
                style={{
                  width: '100%',
                  maxWidth: '700px',
                  maxHeight: '70vh',
                  cursor: 'zoom-in'
                }}
              />
              <Magnifier
                visible={modalMagnifierVisible}
                x={modalMagnifierPos.x}
                y={modalMagnifierPos.y}
                zoom={MAGNIFIER_ZOOM}
                imgWidth={modalImgSize.width}
                imgHeight={modalImgSize.height}
                bgX={-modalMagnifierPos.x * MAGNIFIER_ZOOM + 60}
                bgY={-modalMagnifierPos.y * MAGNIFIER_ZOOM + 60}
                style={{
                  backgroundImage: `url(${getImageUrl(showImage.image_url)})`,
                }}
              />
            </BikeImageWrapper>
          </ModalContent>
        </ModalOverlay>
      )}
    </BikeContainer>
  );
};

export default BikeDetails;