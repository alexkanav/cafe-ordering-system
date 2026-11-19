import { toast } from 'react-toastify';
import { useState } from 'react';


export default function QuantityDropdown({
  dishId,
  addon,
  addOnMenu,
  currentDish,
  dishName,
  updateAddition,
}) {
  const [isOpen, setIsOpen] = useState(false);
  const additionQuantity = currentDish?.additions?.[addon]?.quantity
  const dishQuantity = currentDish?.quantity ?? 0;

  const handleSelect = (quantity) => {
    updateAddition(dishId, addon, addOnMenu[addon], quantity);
    setIsOpen(false);
  };

  const className = [
    'nav-scr-add',
    dishQuantity > 0 && 'add-dg-col',
    additionQuantity > 0 && 'active-button',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div className="quantity-dropdown">

      <button
        type="button"
        className={className}
          onClick={
            dishQuantity
              ? () => setIsOpen(!isOpen)
              : () => toast.error(`Спершу додайте страву: ${dishName}`)
          }
      >
      <div className="card-name-add">{addon}</div>
      <div className="card-price-add">
        {additionQuantity > 0
          ? `${additionQuantity} порц.`
          : `${addOnMenu[addon]} грн.`}
      </div>
      </button>

      {isOpen && (
        <div className="quantity-menu">
          <div className="card-name-add">
            Додати: {addon}
          </div>

          {[...Array(dishQuantity).keys()].map((num) => (
            <button
              type="button"
              key={num + 1}
              onClick={() => handleSelect(num + 1)}
            >
              {num + 1} порц.
            </button>
          ))}

          <button
            type="button"
            onClick={() => handleSelect(0)}
          >
            Скасувати
          </button>
        </div>
      )}
    </div>
  );
}
