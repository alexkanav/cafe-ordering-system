import React, { useEffect, useState, useRef } from 'react';
import { toast } from 'react-toastify';
import { sendToServer } from '../../utils/api';
import { config } from '../../config';
import OrderItemsList from '../../components/order/OrderItemsList';


export default function OrderBoard({ setSelectedOrder, name }) {
  const [orders, setOrders] = useState([]);
  const [status, setStatus] = useState(false);
  const [ordersCount, setOrdersCount] = useState("");

  const ordersCountRef = useRef(0);

  const loadOrders = async () => {
    try {
      const { data } = await sendToServer('/api/admin/orders', { only_uncompleted: true}, 'GET');
      setOrders(data.orders);
      setOrdersCount(data.orders_count);
    } catch (error) {
      toast.error(error.message || "Зв'язок з сервером втрачено.");
    }
  };

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const { data } = await sendToServer('/api/admin/orders/count', null, 'GET');
        setStatus(true);
        if (ordersCountRef.current !== data.count) {
          ordersCountRef.current = data.count;
          loadOrders();
        }
      } catch (error) {
        setStatus(false);
        if (error.status === 401) {
          toast.error("Ви не авторизовані !!!");
        } else {
          toast.error(error.message || "Зв'язок з сервером втрачено.");
        }
      }
    }, config.ORDER_POLL_INTERVAL);

    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <div className="order-count">
        Невиконаних замовлень: {ordersCount}
      </div>

      {orders.map((order) => (
        <React.Fragment key={order.id}>
          <button id={`btn-${order.id}`}
            onClick={() => setSelectedOrder(order)}
            className="order-card"
          >
            <div className="order-card-body">
              <div className="order-card-title">
                <span> {order.id}</span>
                <span className="table-num">Стіл  {order.table}</span>
              </div>

              <div className="order-card-description">
                <OrderItemsList
                  orderDetails={order.order_details}
                  showPrices={false}
                />
              </div>
              <div className="order-card-price">{order.final_cost} грн.</div>
            </div>
          </button>
        </React.Fragment>
      ))}
    </>
  );
}