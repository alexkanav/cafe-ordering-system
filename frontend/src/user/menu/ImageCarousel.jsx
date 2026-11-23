import 'react-responsive-carousel/lib/styles/carousel.min.css';
import { Carousel } from 'react-responsive-carousel';
import { config } from '../../config';


export default function ImageCarousel({ carouselImages }) {

  return (
    <>
      <Carousel
        showThumbs={false}
        autoPlay
        infiniteLoop
        showStatus={false}
      >
        {carouselImages.map((img, index) => (
          <div key={img.link}>
            <img src={`${config.ASSETS_IMAGES_FOLDER}${img.link}`} alt={img.alt} loading="lazy" />
            {/* <p className="legend">{img.legend}</p>*/}
          </div>
        ))}
      </Carousel>
    </>
  );
}
