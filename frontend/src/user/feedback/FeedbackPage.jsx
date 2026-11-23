import { Header, Footer } from '../../components';
import CommentForm from './CommentForm';
import hot from '../../assets/images/hot.svg';
import home from '../../assets/images/home.svg';


export default function FeedbackPage() {
  const navLinks = [
    { to: "/", src: home, alt: 'Головна', name: 'Головна' },
    { to: "/menu", src: hot, alt: 'Меню', name: 'Меню' },
  ];

  return (
    <>
      <Header navLinks={navLinks}/>
      <div className="content">
        <CommentForm />
      </div>
      <Footer />
    </>
  );
}