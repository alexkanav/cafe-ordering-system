export default function Description({ description }) {

  return (
    <div className="description">
      <ul className="dashed-list">

        {description.map((text, index) => (
          <li key={index}>{text}</li>
        ))}

      </ul>
    </div>
  );
}