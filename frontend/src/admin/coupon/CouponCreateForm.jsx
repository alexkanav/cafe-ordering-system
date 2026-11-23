import React, { useState } from "react";
import { toast } from 'react-toastify';
import DatePicker, { registerLocale } from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import uk from "date-fns/locale/uk";

registerLocale("uk", uk);


export default function CouponCreateForm({ onSubmit, coupons = [], createCoupon }) {
  const [discount, setDiscount] = useState("");
  const [expiresAt, setExpiresAt] = useState(new Date());
  const [isExpires, setIsExpires] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();

    const numDiscount = Number(discount);

    if (isNaN(numDiscount) || numDiscount < 1 || numDiscount > 99) {
      toast.warning("Знижка має бути від 1 до 99%");
      return;
    }
    const expiresAtStr = expiresAt.toISOString().slice(0, 10);

    createCoupon({
      discount_value: numDiscount,
      expires_at: isExpires ? expiresAtStr : null,
    });

    setDiscount("");
    setIsExpires(false);
    setExpiresAt(new Date());
  };

  return (
    <div className="dashboard-form">
      <h3>Створити новий купон</h3>
      <form onSubmit={handleSubmit}>
        <label>
          Процент знижки:
          <input
            type="number"
            placeholder="Число від 1 до 99"
            value={discount}
            onChange={(e) => setDiscount(e.target.value)}
            min="1"
            max="99"
            required
          />
        </label>

        <div className="radio-group">
          <label>
            <input
              type="radio"
              name="expires"
              checked={!isExpires}
              onChange={() => setIsExpires(false)}
            />
            Безстроковий
          </label>

          <label>
            <input
              type="radio"
              name="expires"
              checked={isExpires}
              onChange={() => setIsExpires(true)}
            />
            З терміном дії
          </label>
        </div>

        {isExpires && (
          <DatePicker
            selected={expiresAt}
            onChange={(date) => setExpiresAt(date)}
            dateFormat="dd-MM-yyyy"
            locale="uk"
            className="date-picker"
          />
        )}

        <button
          type="submit"
          className="btn-submit"
          disabled={!discount || discount < 1 || discount > 99}
        >
          Створити купон
        </button>
      </form>
    </div>
  );
}
