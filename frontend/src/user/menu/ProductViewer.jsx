import ProductCard from './ProductCard';
import DragScrollMenu from '../DragScroll/DragScrollMenu';


export default function ProductViewer({ menuCategories, categoryItems, allMenuItems }) {

  return (
    <>
      <DragScrollMenu categories={menuCategories} />

      {menuCategories.map((categoryName, index) => (
        <div key={categoryName}>
          <div id={`category_${index}`} className="category-block">
            {categoryName}
          </div>
          <div className="product-grid">
            {categoryItems[index].map((code) => {
              return (
                <ProductCard
                  key={`${categoryName}-${code}`}
                  code={code}
                  name={allMenuItems[code].name}
                  isPop={allMenuItems[code].is_popular}
                  isRec={allMenuItems[code].is_recommended}
                  extras={allMenuItems[code].extras}
                  description={allMenuItems[code].description}
                  image_link ={allMenuItems[code].image_link}
                  likes={allMenuItems[code].likes}
                  price={allMenuItems[code].price}
                />
              );
            })}
          </div>
        </div>
      ))}
    </>
  );
}

