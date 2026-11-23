const formatCurrency = (num = 0) => Number(num).toFixed(2);


export default function OrderPriceSummary({
  orderTotal,
  couponPercentage = 0,
  couponDiscount = 0,
  loyaltyPercentage = 0,
  loyaltyDiscount = 0,
  amountToPay,
  showDiscountAmounts
}) {
  return (
    <>
      <div className="board-title">Розрахована вартість</div>

      <div className="details">
        <span>Вартість без знижки:</span>

        <span className="no-wrap-text">
          {formatCurrency(orderTotal)} грн.
        </span>

        <span>Знижка за купоном: {showDiscountAmounts && `${couponPercentage}%`}</span>
        <span className="no-wrap-text">
          {showDiscountAmounts ? formatCurrency(couponDiscount) : `${couponPercentage}%`}
        </span>

        <span>Знижка постійного покупця: {showDiscountAmounts && `${loyaltyPercentage}%`}</span>
        <span className="no-wrap-text">
          {showDiscountAmounts ? formatCurrency(loyaltyDiscount) : `${loyaltyPercentage}%`}
        </span>

        <span>До сплати:</span>
        <span className="no-wrap-text">
          {formatCurrency(amountToPay)} грн.
        </span>
      </div>
    </>
  );
}