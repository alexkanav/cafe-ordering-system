import React, { useState } from 'react';
import { toast } from 'react-toastify';
import AddOnMenu from './AddOnMenu';
import { sendToServer } from '../../utils/api';
import love from '../../assets/images/love.jpg';
import star from '../../assets/images/star.svg';
import likeW from '../../assets/images/likeW.jpg';
import likeB from '../../assets/images/likeB.jpg';
import { useOrder } from '../../context/OrderContext';
import { config } from '../../config';


export default function ProductCard(props) {
  const { code, name, description, price, image_link, likes, isPop, isRec, extras} = props;
  const { orderDetails, updateItem } = useOrder();
  const [likeDish, setLikeDish] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  const currentDish = orderDetails[code];

  const handleProductQuantity = (event) => {
    const quantity = parseInt(event.target.value);
    updateItem(code, { name, quantity, price, additions: {} });
  };

  const handleShowDetails = () => {
    setShowDetails(prev => !prev);
  };

  const addLikeToDish = async () => {
    try {
      const { data }  = await sendToServer(`/api/users/dishes/${code}/like`, null, 'POST');
      setLikeDish(true);
      toast.success(data.message || "Додано вподобання");
    } catch (error) {
      if (error?.status === 401) {
        toast.error("Спочатку замовте страву.");
      } else {
        toast.error(error.message || "Вподобання не додано");
      }
    }
  };

  return (
    <div className={`product-card ${showDetails ? "details-open" : ""}`}>
      <div className="product-image">
        <img
          src={`${config.UPLOADED_IMAGES_FOLDER}${image_link}`}
          loading="lazy"
          onClick={handleShowDetails}
          alt={name}
        />

      </div>
      <div className="product-details">
        <h2 className="product-title">{name}</h2>
        <div className="card-price">
          {price} грн.

          {isPop && (
            <img className="card-icon" src={love} alt="Популярне" />
          )}

          {isRec && (
            <img className="card-icon" src={star} alt="Рекомендуємо" />
          )}

          <img
            className="like-icon"
            src={likeDish ? likeB : likeW}
            alt="Лайк"
            onClick={!likeDish ? addLikeToDish : undefined}
            style={{ cursor: !likeDish ? 'pointer' : 'default' }}
          />
          <span className="num-like-menu">{likes + (likeDish ? 1 : 0)}</span>
        </div>

        <p className={`product-description ${!showDetails ? "description-collapsed" : ""}`}>
          {description}
        </p>

        {Object.keys(extras).length !== 0 && (
          <AddOnMenu
            dishId={code}
            addOnMenu={extras}
            dishName={name}
            currentDish={currentDish}
          />
        )}

        <div className="product-btn">
          <select
            value={currentDish?.quantity ?? "0"}
            className={`amount ${(currentDish?.quantity && currentDish.quantity !== "0") ? "amount-activ" : ""}`}
            onChange={(event) => {handleProductQuantity(event, code, price)}}
          >
            <option value="0">Замовити</option>
            {[...Array(10).keys()].map((num) => (
              <option key={num + 1} value={num + 1}>
                {num + 1} порц.
              </option>
            ))}
          </select>

          <button className="card-btn"
            onClick={handleShowDetails}>
            {showDetails ? "приховати" : "показати"}
          </button>
        </div>
      </div>
    </div>
  );
}
