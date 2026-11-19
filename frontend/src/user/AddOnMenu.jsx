import { useOrder } from '../context/OrderContext';
import { useDragScroll } from '../hooks/useDragScroll';
import QuantityDropdown from './QuantityDropdown';


export default function AddOnMenu({
  dishId,
  currentDish,
  addOnMenu,
  dishName,
  dishRequestedQuantity,
}) {
  const { updateAddition } = useOrder();

  const {
    containerRef,
    handleMouseDown,
    handleMouseMove,
    handleMouseUp,
  } = useDragScroll();

  return (
    <div className="ext-note">
      Додати:
      <div
        className="nav-scroller-add"
        ref={containerRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {Object.keys(addOnMenu).map((addon) => (
          <QuantityDropdown
            key={addon}
            dishId={dishId}
            addon={addon}
            addOnMenu={addOnMenu}
            currentDish={currentDish}
            dishName={dishName}
            dishRequestedQuantity={dishRequestedQuantity}
            updateAddition={updateAddition}
          />
        ))}
      </div>
    </div>
  );
}