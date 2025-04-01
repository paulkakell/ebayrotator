import { useEffect, useState } from "react";
import { api } from "../api";

export default function ErrorLogViewer() {
  const [errors, setErrors] = useState<any[]>([]);

  useEffect(() => {
    api.get("/errors")
      .then(res => setErrors(res.data))
      .catch(err => console.error("Error log error:", err));
  }, []);

  return (
    <div className="box">
      <h2 className="title">Recent Errors</h2>
      <ul>
        {errors.map((e, i) => (
          <li key={i}>
            <strong>{e.timestamp}</strong> — <em>{e.step}</em> — {e.sku}<br />
            {e.message}
          </li>
        ))}
      </ul>
    </div>
  );
}
