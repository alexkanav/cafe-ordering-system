import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { sendToServer } from '../../utils/api';
import { Spinner} from '../../components';


export default function Comments() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadComments = async () => {
      try {
        const { data } = await sendToServer('/api/users/comments', null, 'GET');
        setData(data.comments);
      } catch (error) {
        toast.error(error.message || "Не вдалося завантажити відгуки.");
      } finally {
        setLoading(false);
      }
    };

    loadComments();
  }, []);

  return (
    <div id="comments">
      {loading ? (
        <Spinner />
      ) : data.length === 0 ? (
        <div className="comments-empty">Ще немає відгуків.</div>
      ) : (
        data.map((item, index) => (
          <div className="card-wrap" key={item.id || index}>
            <div className="main-block-wrap">
              <div className="card-box">
                <div className="card-cont cont_full">
                  <div className="card-comm">
                    <strong>{item.user_name}</strong>: <span className="card-note">{item.comment_date}</span>
                  </div>
                  <div className="card-descr">{item.comment_text}</div>
                </div>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
