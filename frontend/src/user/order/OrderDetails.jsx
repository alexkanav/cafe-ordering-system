import { useState } from 'react';
import { toast } from 'react-toastify';
import { useOrder } from '../../context/OrderContext';
import { VIEWS } from '../../constants/views';
import { sendToServer } from '../../utils/api';
import mcVisa from '../../../static/images/visa-mc.jpg';
import gPay from '../../../static/images/google-pay.png';
import aPay from '../../../static/images/apple-pay.png';
import OrderItemsList from '../../components/order/OrderItemsList';
import OrderPriceSummary from '../../components/order/OrderPriceSummary';
import CouponValidateForm from '../coupon/CouponValidateForm';


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
  const amountToPay = orderTotal  - couponDiscount - loyaltyDiscount;

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
              <OrderItemsList
                orderDetails={orderDetails}
                showPrices={true}
              />
            </div>

            <div className="order-card-price">Сума: {orderTotal.toFixed(2)} грн.</div>

            <div className="board-title">Маєте купон на знижку?</div>

            <CouponValidateForm
              couponCode={couponCode}
              setCouponCode={setCouponCode}
              handleApplyCoupon={handleApplyCoupon}
              hasCouponError={hasCouponError}
              setHasCouponError={setHasCouponError}
              isCouponApplied={isCouponApplied}
              isCouponLoading={isCouponLoading}
            />

            <OrderPriceSummary
              orderTotal={orderTotal}
              couponPercentage={couponPercentage}
              couponDiscount={couponDiscount}
              loyaltyPercentage={loyaltyPercentage}
              loyaltyDiscount={loyaltyDiscount}
              amountToPay={amountToPay}
              showDiscountAmounts={true}
            />

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
            <div className="price">{amountToPay.toFixed(2)}<sub> грн.</sub></div>
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