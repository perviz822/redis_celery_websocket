import { useEffect, useState } from "react";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [status, setStatus] = useState("Connecting...");
  const [inputMessage, setInputMessage] = useState("");
  const [ws, setWs] = useState(null);

 useEffect(() => {
    const clientId = "client1"; // unique id per user/session
    const wsConnection = new WebSocket(`ws://127.0.0.1:8000/ws/${clientId}`);

    wsConnection.onopen = () => {
      setStatus("Connected");
      console.log("WebSocket connected with ID:", clientId);  // Modified this line
    };

    wsConnection.onmessage = (event) => {
      console.log("Received message:", event.data);  // Add this line
      setMessages((prev) => [...prev, event.data]);
    };

    wsConnection.onerror = (error) => {
      setStatus("Error");
      console.error("WebSocket error:", error);
    };

    wsConnection.onclose = (event) => {  // Modified this handler
      setStatus("Disconnected");
      console.log("WebSocket closed with code:", event.code, "reason:", event.reason);
    };

    setWs(wsConnection);

    return () => {
      if (wsConnection.readyState === WebSocket.OPEN) {
        wsConnection.close();
      }
    };
  }, []); 

    

  const sendMessage = () => {
    if (ws && ws.readyState === WebSocket.OPEN && inputMessage) {
      ws.send(inputMessage);
      setInputMessage("");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">
          WebSocket Demo
        </h1>

        <div className="mb-6">
          <span className="text-sm font-semibold text-gray-600">Status: </span>
          <span
            className={`text-sm font-semibold ${
              status === "Connected"
                ? "text-green-600"
                : status === "Error"
                ? "text-red-600"
                : "text-yellow-600"
            }`}
          >
            {status}
          </span>
        </div>

        <div className="mb-4 flex gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Enter a message"
            className="flex-1 p-2 border rounded"
          />
          <button
            onClick={sendMessage}
            disabled={!ws || ws.readyState !== WebSocket.OPEN}
            className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
          >
            Send
          </button>
        </div>

        <div className="space-y-2">
          {messages.length === 0 ? (
            <p className="text-gray-500 italic">Waiting for messages...</p>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                className="bg-blue-50 border-l-4 border-blue-500 p-3 rounded"
              >
                {msg}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}