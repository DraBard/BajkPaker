import React, { useState } from 'react';
import styled from 'styled-components';
import { submitCustomBikeOrder } from '../api';

const PageContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: ${(props) => props.theme.spacing.medium};
  background-color: ${(props) => props.theme.colors.light};
  border-radius: ${(props) => props.theme.borderRadius};
  box-shadow: ${(props) => props.theme.boxShadow};
`;

const SectionTitle = styled.h1`
  margin-bottom: ${(props) => props.theme.spacing.medium};
  color: ${(props) => props.theme.colors.primary};
`;

const Description = styled.div`
  margin-bottom: ${(props) => props.theme.spacing.large};
  line-height: 1.6;
  
  p {
    margin-bottom: 1rem;
  }
  
  ul {
    padding-left: 2rem;
    margin-bottom: 1rem;
  }
`;

const CustomBikeForm = styled.form`
  margin-top: ${(props) => props.theme.spacing.large};
`;

const FormGroup = styled.div`
  margin-bottom: ${(props) => props.theme.spacing.medium};
`;

const Label = styled.label`
  display: block;
  margin-bottom: ${(props) => props.theme.spacing.small};
  font-weight: 600;
`;

const Input = styled.input`
  width: 100%;
  padding: ${(props) => props.theme.spacing.small};
  border: 1px solid #ddd;
  border-radius: ${(props) => props.theme.borderRadius};
  font-size: 1rem;
  margin-bottom: 4px;
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: ${(props) => props.theme.spacing.small};
  border: 1px solid #ddd;
  border-radius: ${(props) => props.theme.borderRadius};
  font-size: 1rem;
  min-height: 150px;
  margin-bottom: 4px;
`;

const Select = styled.select`
  width: 100%;
  padding: ${(props) => props.theme.spacing.small};
  border: 1px solid #ddd;
  border-radius: ${(props) => props.theme.borderRadius};
  font-size: 1rem;
  margin-bottom: 4px;
`;

const ErrorText = styled.span`
  color: #d32f2f;
  font-size: 0.8rem;
  display: block;
  margin-top: 4px;
`;

const SubmitButton = styled.button`
  background-color: ${(props) => props.theme.colors.primary};
  color: #fff;
  border: none;
  padding: ${(props) => props.theme.spacing.medium};
  border-radius: ${(props) => props.theme.borderRadius};
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  width: 100%;
  margin-top: ${(props) => props.theme.spacing.medium};
  transition: background-color 0.3s ease, transform 0.3s ease;

  &:hover {
    background-color: ${(props) => props.theme.colors.secondary};
    transform: translateY(-2px);
  }

  &:disabled {
    background-color: ${(props) => props.theme.colors.disabled};
    cursor: not-allowed;
  }
`;

const SuccessMessage = styled.div`
  padding: ${(props) => props.theme.spacing.medium};
  background-color: #e8f5e9;
  color: #2e7d32;
  border-radius: ${(props) => props.theme.borderRadius};
  margin-top: ${(props) => props.theme.spacing.medium};
  text-align: center;
  font-weight: 600;
`;

const ErrorMessage = styled.div`
  padding: ${(props) => props.theme.spacing.medium};
  background-color: #ffebee;
  color: #d32f2f;
  border-radius: ${(props) => props.theme.borderRadius};
  margin-top: ${(props) => props.theme.spacing.medium};
  text-align: center;
`;

const CustomBikePage = () => {
  const [formData, setFormData] = useState({
    name: '',
    surname: '',
    phone: '',
    additionalInfo: ''
  });
  
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState({
    success: false,
    message: ''
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when field is edited
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    // Required fields
    if (!formData.name.trim()) newErrors.name = "Imię jest wymagane";
    if (!formData.surname.trim()) newErrors.surname = "Nazwisko jest wymagane";
    
    if (!formData.phone.trim()) {
      newErrors.phone = "Numer telefonu jest wymagany";
    } else if (!/^\d{9,12}$/.test(formData.phone.replace(/\s+/g, ''))) {
      newErrors.phone = "Nieprawidłowy format numeru telefonu";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      window.scrollTo(0, 0); // Scroll to top to show errors
      return;
    }
    
    try {
      setIsSubmitting(true);
      
      await submitCustomBikeOrder({
        customer: {
          name: `${formData.name} ${formData.surname}`,
          email: "not_provided@example.com", // Backend requires email but we don't collect it
          phone: formData.phone
        },
        bikeDetails: {
          frameType: "city", // Default to city bikes
          frameSize: "",
          color: "",
          components: "",
          budget: "",
          additionalInfo: formData.additionalInfo
        }
      });
      
      setSubmitResult({
        success: true,
        message: 'Dziękujemy! Zamówienie na projekt indywidualnego roweru zostało wysłane. Skontaktujemy się z Tobą wkrótce.'
      });
      
      // Reset form
      setFormData({
        name: '',
        surname: '',
        phone: '',
        additionalInfo: ''
      });
      
    } catch (error) {
      console.error('Error submitting custom bike order:', error);
      setSubmitResult({
        success: false,
        message: 'Wystąpił błąd podczas wysyłania zamówienia. Prosimy spróbować ponownie lub skontaktować się z nami bezpośrednio.'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

return (
    <PageContainer>
        <SectionTitle>Twój Projekt</SectionTitle>
        
        <Description>
            <p>Marzysz o unikalnym rowerze miejskim, który będzie odzwierciedlał Twoją osobowość? Jesteśmy tutaj, aby spełnić Twoje marzenia!</p>
            
            <p>W BajkPaker specjalizujemy się w tworzeniu wyjątkowych rowerów miejskich z tematycznymi motywami według Twojego wyboru:</p>
            <ul>
                <li><strong>Miłośnik wina?</strong> Wyobraź sobie rower w głębokich burgundowych odcieniach, z bagażnikiem na trunki</li>
                <li><strong>Pasjonat grzybobrania?</strong> Stwórzmy rower w leśnych kolorach, z subtelnymi akcentami grzybów na ramie i akcesoriach oraz koszykiem na zbiory</li>
                <li><strong>Fan militariów?</strong> Matowe wykończenie w stylu moro, mocna konstrukcja i detale inspirowane sprzętem wojskowym.</li>
                <li><strong>Marzyciel o światach fantasy?</strong> Rower z elementami inspirowanymi smokami, elfami czy magicznymi stworzeniami.</li>
            </ul>
            
            <p><strong>Dwie drogi do Twojego wymarzonego roweru:</strong></p>
            <ul>
                <li><strong>Odnowa Twojego roweru</strong> - Możesz dostarczyć nam swój stary rower, a my odnowimy go według Twojego pomysłu. Jeśli potrzebujesz pomocy w opracowaniu koncepcji, chętnie służymy radą i kreatywnymi rozwiązaniami.</li>
                <li><strong>Projekt od podstaw</strong> - Jeśli nie posiadasz własnego roweru, nie martw się! My zajmiemy się pozyskaniem odpowiedniego modelu i stworzymy projekt od zera, kierując się Twoją wizją.</li>
            </ul>
            
            <p><strong>Jak tworzymy nasze rowery:</strong></p>
            <ul>
                <li>Starannie wybieramy i odrestaurowujemy używane ramy rowerowe, nadając im nowe życie</li>
                <li>Części, które oceniamy jako sprawne, przechodzą proces renowacji i są ponownie wykorzystane</li>
                <li>Pozostałe elementy wymieniamy na nowe, wysokiej jakości komponenty</li>
                <li>Każdy rower jest ręcznie malowany i wykańczany zgodnie z wybranym motywem</li>
            </ul>
            <br></br>
            <p>Wypełnij poniższy formularz, podając swoje dane kontaktowe oraz pomysł na wymarzony rower, a my skontaktujemy się z Tobą, aby omówić szczegóły!</p>
        </Description>
        
        {submitResult.message && (
            submitResult.success ? 
                <SuccessMessage>{submitResult.message}</SuccessMessage> : 
                <ErrorMessage>{submitResult.message}</ErrorMessage>
        )}
        
        <CustomBikeForm onSubmit={handleSubmit}>
            <FormGroup>
                <Label htmlFor="name">Imię*:</Label>
                <Input 
                    type="text" 
                    id="name" 
                    name="name" 
                    value={formData.name}
                    onChange={handleInputChange}
                />
                {errors.name && <ErrorText>{errors.name}</ErrorText>}
            </FormGroup>
            
            <FormGroup>
                <Label htmlFor="surname">Nazwisko*:</Label>
                <Input 
                    type="text" 
                    id="surname" 
                    name="surname" 
                    value={formData.surname}
                    onChange={handleInputChange}
                />
                {errors.surname && <ErrorText>{errors.surname}</ErrorText>}
            </FormGroup>
            
            <FormGroup>
                <Label htmlFor="phone">Telefon*:</Label>
                <Input 
                    type="tel" 
                    id="phone" 
                    name="phone" 
                    value={formData.phone}
                    onChange={handleInputChange}
                />
                {errors.phone && <ErrorText>{errors.phone}</ErrorText>}
            </FormGroup>
            
            <FormGroup>
                <Label htmlFor="additionalInfo">Powiedz nam o swoim wymarzonym rowerze:</Label>
                <TextArea 
                    id="additionalInfo" 
                    name="additionalInfo" 
                    value={formData.additionalInfo}
                    onChange={handleInputChange}
                    placeholder="Opisz swój wymarzony motyw roweru, preferowane kolory, styl, konkretne elementy, które chciałbyś/chciałabyś mieć, lub cokolwiek innego, co pomoże nam zrozumieć Twoją wizję."
                />
            </FormGroup>
            
            <SubmitButton type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Wysyłanie...' : 'Wyślij zapytanie'}
            </SubmitButton>
            
            <p style={{ fontSize: '0.8rem', margin: '10px 0' }}>* Pola wymagane</p>
        </CustomBikeForm>
    </PageContainer>
);
};

export default CustomBikePage;
