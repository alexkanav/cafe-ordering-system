import { toast } from 'react-toastify';


export default function CouponValidateForm({
  couponCode,
  setCouponCode,
  handleApplyCoupon,
  hasCouponError,
  setHasCouponError,
  isCouponApplied,
  isCouponLoading
}) {
  return (
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
  );
}