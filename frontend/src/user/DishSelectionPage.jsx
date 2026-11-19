import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { Header, Footer, Spinner } from '../components';
import ProductViewer from './ProductViewer';
import OrderSummary from './OrderSummary';
import TableSelection from './TableSelection';
import { useOrder } from '../context/OrderContext';
import { VIEWS } from '../constants/views';
import heart from '../assets/images/heart.svg';
import star from '../assets/images/star.svg';
import { sendToServer } from '../utils/api';


export default function DishSelectionPage() {
  const [menuCategories, setMenuCategories] = useState([]);
  const [categoryItems, setCategoryItems] = useState([]);
  const [allMenuItems, setAllMenuItems] = useState({});
  const [currentView, setCurrentView] = useState(VIEWS.PRODUCT);
  const { addItem, cleanOrder, calculateTotal } = useOrder();

  const [tableNumber, setTableNumber] = useState(0);
  const [totalCost, setTotalCost] = useState(0);

  const goTo = (view) => setCurrentView(view);

  const completeOrder = () => {
    const validOrder = cleanOrder();
    if (Object.keys(validOrder).length === 0) {
      toast.error("Ваше замовлення порожнє.");
      return;
    }

    setTotalCost(calculateTotal());

    goTo(VIEWS.TABLE);
  };

  useEffect(() => {
    const fetchMenu = async () => {
      try {
        const { data } = await sendToServer('/api/users/menu', null, 'GET');

        if (data.categories && data.dishes) {
          setMenuCategories(data.categories.map((item) => Object.keys(item)[0]));
          setCategoryItems(data.categories.map((item) => Object.values(item)[0]));
          setAllMenuItems(data.dishes);
        } else {
          throw new Error("Menu data is incomplete");
        }
      } catch (error) {
        console.error("Error fetching menu:", error);
        toast.error("Помилка завантаження меню.");
      }
    };
    fetchMenu();
  }, []);

  if (!menuCategories.length || !categoryItems.length || !Object.keys(allMenuItems).length)
    return <Spinner />

  const VIEW_COMPONENTS = {
    [VIEWS.PRODUCT]: (
      <>
        <ProductViewer
          menuCategories={menuCategories}
          categoryItems={categoryItems}
          allMenuItems={allMenuItems}
        />
        <div className="button-wrapper">
          <button className="order-button" onClick={completeOrder}>
            Завершити замовлення
          </button>
        </div>
      </>
    ),
    [VIEWS.TABLE]: <TableSelection goTo={goTo} setTableNumber={setTableNumber} />,
    [VIEWS.SUMMARY]: <OrderSummary goTo={goTo} totalCost={totalCost} tableNumber={tableNumber} />,
  };

  const navLinks = (currentView === VIEWS.PRODUCT)
    ? [
        { to: `#category_${menuCategories.length - 2}`, src: heart, alt: 'Популярні страви', name: 'Популярне' },
        { to: `#category_${menuCategories.length - 1}`, src: star, alt: 'Рекомендовані страви', name: 'Рекомендуємо' },
      ]
    : [];

  return (
    <>
      <Header navLinks={navLinks} />
      <div className="content">
        {VIEW_COMPONENTS[currentView]}
      </div>
      <Footer />
    </>
  );
}
