import { api } from "../api";

export default function SendReportButton() {
  const sendReport = () => {
    api.post("/send-report")
      .then(res => alert(res.data.message))
      .catch(err => alert("Failed to send report: " + err.response?.data?.detail));
  };

  return (
    <div className="box">
      <button onClick={sendReport}>📨 Send Error Report Now</button>
    </div>
  );
}
