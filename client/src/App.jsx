import { useEffect, useState } from "react";
import { getHealth } from "./api";

function App() {
  const [status, setStatus] = useState("checking");

  useEffect(() => {
    getHealth()
      .then((data) => setStatus(data.database === "ok" ? "connected" : "error"))
      .catch(() => setStatus("error"));
  }, []);

  return (
    <main>
      <h1>Calm Before</h1>
      <p>Know your local disaster risks and get ready before the storm.</p>
      <p>
        API status:{" "}
        {status === "checking" && "Checking…"}
        {status === "connected" && "✅ API and database connected"}
        {status === "error" && "❌ Can't reach the API. Is Flask running?"}
      </p>
    </main>
  );
}

export default App;