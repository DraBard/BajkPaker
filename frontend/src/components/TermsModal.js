import React from 'react';
import styled from 'styled-components';

const ModalOverlay = styled.div`
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: #fff;
  padding: 30px;
  max-width: 800px;
  width: 90%;
  max-height: 85vh;
  overflow-y: auto;
  border-radius: ${props => props.theme.borderRadius};
  box-shadow: ${props => props.theme.boxShadow};
  position: relative;

  h2 {
    font-size: 1.8rem;
    margin-bottom: 1.5rem;
    color: #333;
  }

  h3 {
    font-size: 1.2rem;
    margin: 1.5rem 0 1rem;
    color: #444;
  }

  p {
    margin-bottom: 1rem;
    line-height: 1.6;
  }

  ul {
    margin: 1rem 0;
    padding-left: 2rem;
  }

  li {
    margin-bottom: 0.5rem;
    line-height: 1.4;
  }
`;

const Section = styled.section`
  margin-bottom: 2rem;
`;

const CloseButton = styled.button`
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
`;

export const TermsModal = ({ open, onClose }) => {
  if (!open) return null;
  
  const termsText = `
Regulamin sklepu internetowego z ręcznie wykonanymi rowerami

Postanowienia ogólne

    Sprzedawca: Osoba fizyczna – Szymon Pałus, ul. Styczyńskiego 10/1, 44-100 Gliwice, e-mail: bajkpaker@gmail.com, tel. 574513493. Sklep prowadzi sprzedaż okazjonalną rowerów rzemieślniczych i nie jest zarejestrowany jako działalność gospodarcza.

    Oferta skierowana jest wyłącznie do konsumentów: osoby fizycznej dokonującej zakupu niezwiązanego bezpośrednio z działalnością zawodową lub gospodarczą
    rzetelnyregulamin.pl
    . Umowa sprzedaży zawierana jest z takim kupującym na podstawie niniejszego Regulaminu.

    Produkty: Rower wykonany z używanej, odrestaurowanej ramy oraz z nowych lub odnowionych komponentów. Kupujący akceptuje, że ramy i części mogą nosić ślady wcześniejszej eksploatacji, które nie stanowią wady towaru. Sprzedawca informuje, że rowery są dostępne w stanie „odnowionym” (w pełni sprawne mechanicznie, jednak dopuszcza się widoczne ślady użytkowania).

    Brak płatności online i wysyłki: Sklep nie obsługuje płatności internetowych ani usług kurierskich. Towar opłacany jest gotówką przy odbiorze lub tradycyjnym przelewem bankowym przed odbiorem. Zakupione rowery mogą być odebrane wyłącznie osobiście w siedzibie Sprzedawcy pod adresem podanym powyżej (po uprzednim uzgodnieniu terminu odbioru).

Procedura zakupu

    Składanie zamówienia: Kupujący wybiera model roweru i składa zamówienie przez stronę internetową sklepu lub kontaktując się bezpośrednio ze Sprzedawcą (e-mail, telefon). Zamówienie powinno zawierać dane Kupującego, wybrany produkt oraz preferowaną formę płatności i wstępny termin odbioru. W przypadku problemów technicznych z formularzem zamówienia, prosimy o bezpośredni kontakt telefoniczny lub mailowy.

    Potwierdzenie i zawarcie umowy: Sprzedawca potwierdza przyjęcie zamówienia (telefonicznie lub mailowo) w ciągu kilku dni od jego otrzymania. Po potwierdzeniu dostępności towaru i uzgodnieniu warunków następuje zawarcie umowy sprzedaży. Umowę uważa się za zawartą z chwilą potwierdzenia zamówienia przez Sprzedawcę.

    Płatność i odbiór: Kupujący uiszcza należność za towar przelewem na rachunek Sprzedawcy przed odbiorem lub gotówką przy odbiorze w ustalonym terminie. Po zaksięgowaniu płatności Sprzedawca przygotowuje rower do wydania. Odbiór osobisty odbywa się w umówionym miejscu i terminie, przy okazaniu dowodu zakupu (np. potwierdzenia przelewu lub wydruku zamówienia).

Prawo odstąpienia od umowy

    Konsument może odstąpić od umowy kupna zawartej na odległość (przez Internet) w terminie 14 dni od dnia jej zawarcia
    prawakonsumenta.uokik.gov.pl
    . Termin ten biegnie od dnia otrzymania towaru przez Kupującego. Nie trzeba podawać przyczyny odstąpienia.

    Aby skorzystać z prawa odstąpienia, Kupujący składa Sprzedawcy oświadczenie (np. na piśmie lub e-mailem) w terminie 14 dni od dnia odbioru towaru. Dobrowolny wzór takiego oświadczenia można znaleźć na stronach organów ochrony praw konsumenta.

    Zwrot towaru: Po złożeniu oświadczenia Kupujący odsyła lub zwraca towar Sprzedawcy niezwłocznie, nie później niż w ciągu kolejnych 14 dni. Koszt zwrotu towaru ponosi Kupujący
    prawakonsumenta.uokik.gov.pl
    . Rower powinien zostać zwrócony w stanie niepogorszonym (z uwzględnieniem zwykłego zużycia); w przypadku zmniejszenia jego wartości z winy Kupującego Sprzedawca może potrącić odpowiednią kwotę z zwracanych pieniędzy.

    Po otrzymaniu zwróconego towaru Sprzedawca zwraca Kupującemu wszystkie otrzymane płatności (w tym koszty dostawy, o ile były naliczone) niezwłocznie, nie później niż 14 dni od dnia otrzymania oświadczenia o odstąpieniu i zwrotu towaru. W razie odstąpienia umowa jest uznana za rozwiązana.

Rękojmia (odpowiedzialność za wady)

    Sprzedawca odpowiada względem Kupującego będącego konsumentem za niezgodność towaru z umową (wadę fizyczną lub prawną) na zasadach określonych w Kodeksie cywilnym (art. 556–576 KC)
    . Okres rękojmi wynosi 2 lata od wydania roweru Kupującemu
    konsument.gov.pl
    .

    W ramach rękojmi Kupujący może żądać bezpłatnej naprawy towaru lub jego wymiany na wolny od wad, zmniejszenia ceny albo odstąpienia od umowy (w przypadku istotnej wady)
    rzetelnyregulamin.pl
    . Sprzedawca może najpierw naprawić towar lub wymienić go, a przy istotnej wadzie Kupujący może odstąpić od umowy.

    Sprzedawca rozpatruje reklamację niezwłocznie, maksymalnie w ciągu 14 dni od jej zgłoszenia. Jeżeli nie odpowie w tym terminie, reklamacja jest uznana za uzasadnioną. Kupujący składa reklamację poprzez kontakt ze Sprzedawcą (osobiście, mailowo lub listownie) i opisuje zauważoną wadę oraz żądane rozwiązanie.

    Obowiązkowy przegląd: Po upływie 12 miesięcy od zakupu Kupujący zobowiązany jest wykonać bezpłatny przegląd serwisowy roweru w warsztacie Sprzedawcy (do 13. miesiąca od daty zakupu). Brak wykonania takiego przeglądu może skutkować ograniczeniem lub utratą uprawnień z tytułu rękojmi na wady ujawnione po roku.

Ograniczenie odpowiedzialności Sprzedawcy

    Sprzedawca nie udziela dodatkowej gwarancji na sprzedawane rowery – obowiązuje wyłącznie ustawowa rękojmia opisana powyżej. Przed odbiorem Kupujący powinien sprawdzić stan roweru; ewentualne uwagi co do jego stanu technicznego należy zgłaszać niezwłocznie przy odbiorze.

    Sprzedawca nie ponosi odpowiedzialności za szkody powstałe z winy Kupującego (np. wynikłe z niewłaściwego użytkowania, montażu lub modyfikacji roweru przez Kupującego lub osoby trzecie). Nie odpowiada także za szkody pośrednie ani za utratę korzyści związanych z użytkowaniem roweru.

Dane Sprzedawcy

    Nazwa i adres: Szymon Pałus, ul. Styczyńskiego 10/1, 44-100 Gliwice

    Telefon: 574 513 493

    E-mail: bajkpaker@gmail.com

Postanowienia końcowe

    Regulamin obowiązuje od dnia jego opublikowania w sklepie internetowym. Sprzedawca zastrzega możliwość wprowadzania zmian w Regulaminie (ogłaszanych na stronie sklepu); zmiany nie będą dotyczyć zamówień już złożonych.

    Złożenie zamówienia i odebranie towaru oznacza, że Kupujący zapoznał się z Regulaminem i akceptuje jego postanowienia.
  `;
  
  const sections = [
    {
      title: "Postanowienia ogólne",
      content: termsText.split("Postanowienia ogólne")[1].split("Procedura zakupu")[0]
    },
    {
      title: "Procedura zakupu",
      content: termsText.split("Procedura zakupu")[1].split("Prawo odstąpienia od umowy")[0]
    },
    {
      title: "Prawo odstąpienia od umowy",
      content: termsText.split("Prawo odstąpienia od umowy")[1].split("Rękojmia (odpowiedzialność za wady)")[0]
    },
    {
      title: "Rękojmia (odpowiedzialność za wady)",
      content: termsText.split("Rękojmia (odpowiedzialność za wady)")[1].split("Ograniczenie odpowiedzialności Sprzedawcy")[0]
    },
    {
      title: "Ograniczenie odpowiedzialności Sprzedawcy",
      content: termsText.split("Ograniczenie odpowiedzialności Sprzedawcy")[1].split("Dane Sprzedawcy")[0]
    },
    {
      title: "Dane Sprzedawcy",
      content: termsText.split("Dane Sprzedawcy")[1].split("Postanowienia końcowe")[0]
    },
    {
      title: "Postanowienia końcowe",
      content: termsText.split("Postanowienia końcowe")[1]
    }
  ];
  
  return (
    <ModalOverlay onClick={onClose}>
      <ModalContent onClick={e => e.stopPropagation()}>
        <CloseButton onClick={onClose}>&times;</CloseButton>
        <h2>Regulamin</h2>
        {sections.map((section, index) => (
          <Section key={index}>
            <h3>{section.title}</h3>
            <div style={{ whiteSpace: 'pre-line' }}>{section.content}</div>
          </Section>
        ))}
      </ModalContent>
    </ModalOverlay>
  );
};
