import { useState } from 'react';
import { toast } from 'react-toastify';
import { sendToServer } from '../../utils/api';
import OrderItemsList from '../../components/order/OrderItemsList';
import OrderPriceSummary from '../../components/order/OrderPriceSummary';


export default function OrderCard({ selectedOrder, setSelectedOrder }) {
  const [isLoading, setIsLoading] = useState(false);

  const finalizeOrder = async () => {
    if (isLoading || !selectedOrder) return;

    const orderId = selectedOrder.id;

    setIsLoading(true);
    try {
      const { data } = await sendToServer(`/api/admin/orders/${orderId}/complete`, null, 'PATCH');
      toast.success(data.message || `Замовлення: ${orderId} виконано`);
      setSelectedOrder(null);
    } catch (error) {
      toast.error(error.message || "Не вдалося завершити замовлення");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div className='category-block'> Виконане замовлення!</div>
      <div className='master-container'>
        <div className="content-block">
          <div className="order-card-body">
            <div className="order-card-title">
              <span> #{selectedOrder.id}</span>
              <span className="table-num">Стіл  {selectedOrder.table}</span>
            </div>
            <div className="summary-card-description">
              <OrderItemsList
                orderDetails={selectedOrder.order_details}
                showPrices={true}
              />
            </div>

            <OrderPriceSummary
              orderTotal={selectedOrder.original_cost}
              couponPercentage={selectedOrder.coupon_pct}
              loyaltyPercentage={selectedOrder.loyalty_pct}
              amountToPay={selectedOrder.final_cost}
              showDiscountAmounts={false}
            />

            <div className="price">{selectedOrder.final_cost}<sub> грн.</sub></div>
            <div className="checkout--footer">
              <button
                onClick={() => setSelectedOrder(null)}
                className="cancel-btn"
                disabled={isLoading}
              >
                Скасувати
              </button>
              <button
                onClick={finalizeOrder}
                className="apply-btn"
                disabled={isLoading}
              >
                {isLoading ? 'Обробка...' : 'Підтверджую'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}