import { useState } from 'react';
import { toast } from 'react-toastify';
import { sendToServer } from '../utils/api';


const formatCurrency = (price) => Number(price).toFixed(2);

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
              {Object.entries(selectedOrder.order_details).map(([code, item]) => {
                const { name, quantity, price, additions } = item;
                return (
                  <div className="order-card-item" key={code}>
                    <div className="details">
                      <span>{name}:</span>
                      <span className="no-wrap-text"><strong>{quantity}</strong> x {price} грн.</span>
                    </div>

                    {additions && Object.keys(additions).length > 0 && (
                      <div className="order-additions">
                        <span>- додатки: (
                          {Object.entries(additions).map(([addName, addition], index) => (
                            <span key={addName}>
                              {index > 0 && ', '}
                              {addName}: {addition.quantity}x{addition.price} грн.
                            </span>
                          ))}
                        )</span>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
            <div className="board-title">Розрахована вартість</div>
              <div className="details">
                <span>Вартість без знижки:</span>
                <span className="no-wrap-text"> {formatCurrency(selectedOrder.original_cost)} грн.</span>
                <span>Знижка за купоном:</span>
                <span className="no-wrap-text"> {selectedOrder.coupon_pct} %</span>
                <span>Знижка постійного покупця:</span>
                <span className="no-wrap-text"> {selectedOrder.loyalty_pct} %</span>
                <span>До сплати:</span>
                <span className="no-wrap-text"> {formatCurrency(selectedOrder.final_cost)} грн.</span>
              </div>
              <div className="price">{formatCurrency(selectedOrder.final_cost)}<sub> грн.</sub></div>
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