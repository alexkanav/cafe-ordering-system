import { createContext, useContext, useState } from 'react';


const OrderContext = createContext(null);

export const useOrder = () => {
  const context = useContext(OrderContext);

  if (!context) {
    throw new Error('useOrder must be used within OrderProvider');
  }

  return context;
};

export const OrderProvider = ({ children }) => {
  const [orderDetails, setOrderDetails] = useState({});

  // Update item in the order
  const updateItem = (dishId, itemData) => {
      setOrderDetails(prev => ({
        ...prev,
        [dishId]: {
          ...prev[dishId],
          ...itemData
        }
      }));
    };

  // Update addition
  const updateAddition = (dishId, addition, price, quantity) => {
    setOrderDetails(prev => {
      const existingDish = prev[dishId] || {};
      const existingAdditions = existingDish.additions || {};

      const updatedAdditions = { ...existingAdditions };

      if (quantity > 0) {
        updatedAdditions[addition] = { price, quantity };
      } else {
        delete updatedAdditions[addition];
      }

      return {
        ...prev,
        [dishId]: {
          ...existingDish,
          additions: updatedAdditions
        }
      };
    });
  };

  // Calculate the total price of the order
  const calculateTotal = () => {
    return Object.values(orderDetails).reduce((sum, item) => {
      const quantity = Number(item.quantity || 0);
      const price = Number(item.price || 0);
      const additionsTotal = Object.values(item.additions ?? {}).reduce(
        (total, addition) =>
          total + Number(addition.price) * Number(addition.quantity),
        0
      );
      return sum + (quantity * price + additionsTotal);
    }, 0);
  };

  // Filter out items with quantity <= 0
  const cleanOrder = () => {
    const validOrder = Object.fromEntries(
      Object.entries(orderDetails).filter(
        ([, value]) => Number(value.quantity) > 0
      )
    );
    if (Object.keys(orderDetails).length !== Object.keys(validOrder).length) {
      setOrderDetails(validOrder);
    }
    return validOrder;
  };

  const clearOrder = () => setOrderDetails({});

  return (
    <OrderContext.Provider
      value={{
        orderDetails,
        updateItem,
        updateAddition,
        calculateTotal,
        cleanOrder,
        clearOrder
      }}
    >
      {children}
    </OrderContext.Provider>
  );
};
