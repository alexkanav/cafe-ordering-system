export default function OrderItemsList({ orderDetails, showPrices }) {
  return (
    <>
      {Object.entries(orderDetails).map(([code, item]) => {
        const { name, quantity, price, additions } = item;
        return (
          <div className="order-card-item" key={code}>
            <div className="details">
              <span><strong>{name}</strong>:</span>
              <span className="no-wrap-text"><strong>{quantity}</strong>{showPrices  && ` x ${price} грн.`}</span>
            </div>

            {additions && Object.keys(additions).length > 0 && (
              <div className="order-additions">
                <span>- додатки: (
                  {Object.entries(additions).map(([addName, addition], index) => (
                    <span key={addName}>
                      {index > 0 && ', '}
                      {addName}: {addition.quantity}{showPrices  && ` x${addition.price} грн.`}
                    </span>
                  ))}
                )</span>
              </div>
            )}
          </div>
        );
      })}
    </>
  );
}