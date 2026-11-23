import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { sendToServer } from '../../utils/api';
import CouponCreateForm from './CouponCreateForm';
import { Spinner } from '../../components';


export default function CouponManager() {
  const [coupons, setCoupons] = useState([]);
  const [reloadTrigger, setReloadTrigger] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchCoupons = async () => {
      try {
        setLoading(true);
        const { data } = await sendToServer('/api/admin/coupons', null, 'GET');
        setCoupons(data);
      } catch (error) {
        toast.error(error.message || 'Помилка пошуку купонів');
      } finally {
        setLoading(false);
      }
    };
    fetchCoupons();
  }, [reloadTrigger]);

  const createCoupon = async (coupon_data) => {
    try {
      setLoading(true);
      const { data } = await sendToServer('/api/admin/coupons', coupon_data, 'POST');
      toast.success(data.message || 'Додано новий купон');
      setReloadTrigger(prev => prev + 1);
    } catch (error) {
      toast.error(error.message || 'Помилка створення купона');
    } finally {
      setLoading(false);
    }
  };

  const deactivateCoupon = async (id) => {
    try {
      setLoading(true);
      const { data } = await sendToServer(`/api/admin/coupons/${id}/deactivate`, null, 'PATCH');
      toast.success(data.message || 'Купон деактивовано');
      setReloadTrigger(prev => prev + 1);
    } catch (error) {
      toast.error(error.message || 'Помилка деактивації купона');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = (id) => {
    const yes = window.confirm(`Бажаєте видалити купон #${id} ?`);
    if (yes) deactivateCoupon(id);
  };

  if (loading) return <Spinner />

  return (
    <div className="dashboard-container">
      <div className="coupon-list">
        {coupons.length === 0 ? (
          <p className="no-coupons">Немає доступних купонів.</p>
        ) : (
          <table className="coupon-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Код</th>
                <th>Знижка, %</th>
                <th>Термін дії</th>
                <th>Дія</th>
              </tr>
            </thead>
            <tbody>
              {coupons.map((coupon) => (
                <tr key={coupon.id}>
                  <td data-label="#">{coupon.id}</td>
                  <td data-label="Код">{coupon.code}</td>
                  <td data-label="Знижка, %">{coupon.discount_value}</td>
                  <td data-label="Термін дії">{coupon.expires_at || "Безстроковий"}</td>
                  <td data-label="Дія">
                    <button
                      className="btn-delete"
                      onClick={() => handleDelete(coupon.id)}
                    >
                      Видалити
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      <CouponCreateForm createCoupon={createCoupon} />
    </div>
  );
}
