import React, { useState } from 'react';
import { toast } from 'react-toastify';
import { useOrder } from '../context/OrderContext';
import { VIEWS } from '../constants/views';
import { sendToServer } from '../utils/api';
import mcVisa from '../../static/images/visa-mc.jpg';
import gPay from '../../static/images/google-pay.png';
import aPay from '../../static/images/apple-pay.png';


export default function OrderDetails({ totalCost, loyaltyPercentage,  goTo, postOrder, loading, tableNumber }) {
  const [couponPercentage, setCouponPercentage] = useState(0);
  const [couponCode, setCouponCode] = useState("");
  const [couponAccepted, setCouponAccepted] = useState(false);
  const [couponError, setCouponError] = useState(false);
  const [isCashPayment, setIsCashPayment] = useState(null);

  const { orderDetails } = useOrder();

  const format = (num) => num.toFixed(2);

  const total = totalCost ?? 0;
  const couponDiscount = total * couponPercentage / 100;
  const loyaltyDiscount = total * loyaltyPercentage / 100;
  const totalDiscount = couponDiscount + loyaltyDiscount;
  const payable = parseFloat((total - totalDiscount).toFixed(2));


  const handleApplyCoupon = async (e) => {
    e.preventDefault(); // prevent page refresh right away

    try {
      const { data } = await sendToServer(`/api/users/coupon/${couponCode}`, null, 'POST');

      if (data?.discount !== undefined) {
        setCouponPercentage(data.discount);
        setCouponAccepted(true);
        setCouponError(false);
        toast.success("Знижка отримана!");
      } else {
        setCouponError(true);
        toast.warning("Помилка при використанні купона.");
      }
    } catch (error) {
      setCouponError(true);
      toast.error(error.message || "Не вдалося отримати знижку.");
    }
  };

  return (
    <>
      <div className='category-block'> Перевірте замовлення та оберіть спосіб оплати!</div>
      <div className='master-container'>
        <div className="content-block">
          <div className="order-card-body">
            <div className="order-table-num">Ваш стіл  {tableNumber}</div>

            <div className="summary-card-description">
              {Object.keys(orderDetails).map((id) => {
                const { name, quantity, price, additions } = orderDetails[id];
                return (
                  <div className="order-card-item" key={id}>
                    <div className="details">
                      <span>{name}:</span>
                      <span className="no-wrap-text"><strong>{quantity}</strong> x {price} грн.</span>
                    </div>

                    {additions && Object.keys(additions).length > 0 && (
                      <div className="order-additions">
                        <span>- додатки: (
                          {Object.keys(additions).map((addName) => (
                            <span key={addName}>{addName}:{additions[addName]} грн., </span>
                          ))}
                        )</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            <div className="order-card-price">Сума: {total} грн.</div>

            <div className="board-title">Маєте купон на знижку?</div>
            <form className="coupon" onSubmit={handleApplyCoupon}>
              <input
                id="coupon"
                type="text"
                placeholder="Ваш купон ..."
                className={`input-field ${couponError ? 'error' : ''}`}
                value={couponAccepted ? `Задіяно: ${couponCode}` : couponCode}
                minLength={10}
                maxLength={10}
                required
                onChange={(e) => {
                  if (!couponAccepted) {
                    const value = e.target.value;
                    if (/^[a-zA-Z0-9]{0,10}$/.test(value)) {
                      setCouponCode(value);
                    } else {
                      toast.warning("Купон має містити 10 символів (латинські літери та цифри).");
                    }
                  }
                }}
                disabled={couponAccepted}
              />
              <button className="board-btn" type="submit" disabled={couponAccepted}>
                Додати
              </button>
            </form>

            <div className="board-title">Розрахована вартість</div>
            <div className="details">
              <span>Вартість без знижки:</span>
              <span className="no-wrap-text">{format(total)} грн.</span>
              <span>Знижка за купоном:</span>
              <span className="no-wrap-text">{format(couponDiscount)} грн.</span>
              <span>Знижка постійного покупця:</span>
              <span className="no-wrap-text">{format(loyaltyDiscount)} грн.</span>
              <span>До сплати:</span>
              <span className="no-wrap-text">{payable} грн.</span>
            </div>

            <div className="board-title">Оберіть, як вам зручно оплатити</div>
            <div className="payment-method">
              <div className="radio-group">
                <label>
                  <input
                    type="radio"
                    name="payment"
                    checked={isCashPayment === true}
                    onChange={() => setIsCashPayment(true)}
                  />
                  Готівка
                </label>

                <label>
                  <input
                    type="radio"
                    name="payment"
                    checked={isCashPayment === false}
                    onChange={() => setIsCashPayment(false)}
                  />
                  <span>
                    <img loading="lazy" className="icon-img" src={mcVisa} alt="MC/Visa" />
                    <img loading="lazy" className="icon-img" src={gPay} alt="Google Pay" />
                    <img loading="lazy" className="icon-img" src={aPay} alt="Apple Pay" />
                  </span>
                </label>
              </div>
            </div>
            <div className="price">{payable}<sub> грн.</sub></div>
            <div className="checkout--footer">
              <button onClick={() => goTo(VIEWS.PRODUCT)}className="cancel-btn">Скасувати</button>
              <button
                onClick={() => postOrder(loyaltyPercentage, couponPercentage, payable, couponCode)}
                disabled={loading || isCashPayment === null}
                className="apply-btn"
              >
                {loading ? "Обробка..." : "Підтверджую"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}