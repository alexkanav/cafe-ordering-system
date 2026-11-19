import { useState } from 'react';
import { toast } from 'react-toastify';
import { useOrder } from '../context/OrderContext';
import { VIEWS } from '../constants/views';
import { sendToServer } from '../utils/api';
import mcVisa from '../../static/images/visa-mc.jpg';
import gPay from '../../static/images/google-pay.png';
import aPay from '../../static/images/apple-pay.png';


const formatCurrency = (num) => num.toFixed(2);

export default function OrderDetails({ totalCost, loyaltyPercentage,  goTo, postOrder, loading, tableNumber }) {
  const [couponPercentage, setCouponPercentage] = useState(0);
  const [couponCode, setCouponCode] = useState("");
  const [isCouponApplied, setIsCouponApplied] = useState(false);
  const [hasCouponError, setHasCouponError] = useState(false);
  const [isCashPayment, setIsCashPayment] = useState(null);
  const [isCouponLoading, setIsCouponLoading] = useState(false);

  const { orderDetails } = useOrder();
  const orderTotal  = Number(totalCost ?? 0);
  const couponDiscount = orderTotal  * couponPercentage / 100;
  const loyaltyDiscount = orderTotal  * loyaltyPercentage / 100;
  const amountToPay = formatCurrency(orderTotal  - couponDiscount - loyaltyDiscount);

  const paymentMethod = isCashPayment === null
    ? null
    : isCashPayment ? 'cash' : 'card';

  const handleApplyCoupon = async (e) => {
    e.preventDefault();

    if (isCouponLoading || isCouponApplied) return;

    setIsCouponLoading(true);

    try {
      const { data } = await sendToServer(`/api/users/coupon/${couponCode}`, null, 'POST');

      if (
        Number.isInteger(data?.discount) &&
        data.discount >= 0 &&
        data.discount <= 100
      ) {
        setCouponPercentage(data.discount);
        setIsCouponApplied(true);
        setHasCouponError(false);
        toast.success("Знижка отримана!");
      } else {
        setHasCouponError(true);
        toast.warning("Помилка при використанні купона.");
      }
    } catch (error) {
      setHasCouponError(true);
      toast.error(error.message || "Не вдалося отримати знижку.");
    } finally {
      setIsCouponLoading(false);
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
                        <span>
                          - додатки: (
                          {Object.entries(additions)
                            .filter(([addName, { quantity }]) => quantity > 0)
                            .map(([addName, { price, quantity }], index) => (
                              <span key={addName}>
                                {index > 0 && ', '}
                                {addName}: {quantity}x{price} грн.
                              </span>
                            ))}
                          )
                        </span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            <div className="order-card-price">Сума: {formatCurrency(orderTotal )} грн.</div>

            <div className="board-title">Маєте купон на знижку?</div>
            <form className="coupon" onSubmit={handleApplyCoupon}>
              <input
                id="coupon"
                type="text"
                placeholder="Ваш купон ..."
                className={`input-field ${hasCouponError ? 'error' : ''}`}
                value={isCouponApplied ? `Задіяно: ${couponCode}` : couponCode}
                minLength={10}
                maxLength={10}
                required
                onChange={(e) => {
                  if (!isCouponApplied) {
                    const value = e.target.value;
                    if (/^[a-zA-Z0-9]{0,10}$/.test(value)) {
                      setCouponCode(value);
                      setHasCouponError(false);
                    } else {
                      toast.warning("Купон має містити латинські літери або цифри.");
                    }
                  }
                }}
                disabled={isCouponApplied}
              />
              <button
                className="board-btn"
                type="submit"
                disabled={isCouponApplied || isCouponLoading}
              >
                {isCouponLoading ? 'Перевірка...' : 'Додати'}
              </button>
            </form>

            <div className="board-title">Розрахована вартість</div>
            <div className="details">
              <span>Вартість без знижки:</span>
              <span className="no-wrap-text">{formatCurrency(orderTotal )} грн.</span>
              <span>Знижка за купоном: {couponPercentage}%</span>
              <span className="no-wrap-text">{formatCurrency(couponDiscount)} грн.</span>
              <span>Знижка постійного покупця: {loyaltyPercentage}%</span>
              <span className="no-wrap-text">{formatCurrency(loyaltyDiscount)} грн.</span>
              <span>До сплати:</span>
              <span className="no-wrap-text">{amountToPay} грн.</span>
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
            <div className="price">{amountToPay}<sub> грн.</sub></div>
            <div className="checkout--footer">
              <button onClick={() => goTo(VIEWS.PRODUCT)} className="cancel-btn">Скасувати</button>
              <button
                onClick={() => postOrder(loyaltyPercentage, couponPercentage, amountToPay, couponCode)}
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