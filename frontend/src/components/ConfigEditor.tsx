import { useEffect, useState } from "react";
import { api } from "../api";

export default function ConfigEditor() {
  const [config, setConfig] = useState<Record<string, string>>({});
  const [updatedKey, setUpdatedKey] = useState("");
  const [updatedValue, setUpdatedValue] = useState("");

  useEffect(() => {
    api.get("/config")
      .then(res => setConfig(res.data))
      .catch(err => console.error("Config load error:", err));
  }, []);

  const updateSetting = () => {
    api.put("/config", null, {
      params: { key: updatedKey, value: updatedValue }
    })
    .then(() => {
      setConfig({ ...config, [updatedKey]: updatedValue });
      alert("Setting updated.");
    })
    .catch(err => alert("Error: " + err.response?.data?.detail));
  };

  return (
    <div className="box">
      <h2 className="title">Configuration</h2>
      <table>
        <tbody>
          {Object.entries(config).map(([key, value]) => (
            <tr key={key}>
              <td><strong>{key}</strong></td>
              <td>{value}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Update Setting</h3>
      <input
        type="text"
        placeholder="key"
        value={updatedKey}
        onChange={(e) => setUpdatedKey(e.target.value)}
      />
      <input
        type="text"
        placeholder="value"
        value={updatedValue}
        onChange={(e) => setUpdatedValue(e.target.value)}
      />
      <button onClick={updateSetting}>Update</button>
    </div>
  );
}
