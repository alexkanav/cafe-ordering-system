import telegram from '../../assets/images/teleg.png';
import whatsapp from '../../assets/images/whatsapp.png';
import { useScrollAnimation } from '../../hooks/useScrollAnimation';


export default function Contacts({ contacts, weekdays, openingHours}) {
  const elementRef = useScrollAnimation();

  return (
    <>
      <div
      className="element-animation"
      ref={(el) => (elementRef.current[0] = el)}
      >
        <div className="contacts-menu">
          <div className="main-block-wrap">
            <p>Всі питання та пропозиції вирішуються з адміністратором</p>
            <img className="cont-img" src={telegram} alt="Telegram" />
            <img className="cont-img" src={whatsapp} alt="WhatsApp" />
            <span className="phone">{contacts}</span>
          </div>
        </div>
      </div>

      <div className="main-block-name">Графік роботи:</div>

      <div
        className="element-animation"
        ref={(el) => (elementRef.current[1] = el)}
      >
        <div className="work">
          <div className="main-block-wrap">
            Ми раді Вас бачити:
            <div className="block-text">

              <div className="left-column">
                {weekdays.map((day, index) => (
                  <div key={index}>{day}</div>
                ))}
              </div>

              <div className="right-column">
                {openingHours.map((hour, index) => (
                  <div key={index}>{hour}</div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
