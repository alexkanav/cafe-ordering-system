import DishCategoryEditor from './DishCategoryEditor';
import CouponManager from './coupon/CouponManager';

export default function MenuManagement() {

  return (
    <div className="dashboard-content">
      <div className="dashboard-body">
        <h2 className='m-title'> Оновити меню</h2>
        <DishCategoryEditor />
      </div>
      <h2 className='m-title'>Купони на знижку</h2>
      <CouponManager />
    </div>
  );
}