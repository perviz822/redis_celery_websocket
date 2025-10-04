import { useEffect, useState } from "react";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [status, setStatus] = useState("Connecting...");
  const [progressMessage, setProgressMessage] = useState("");
  const [inputMessage, setInputMessage] = useState("");
  const [ws, setWs] = useState(null);
  const [waitingResponse, setWaitingResponse] = useState(false);

  useEffect(() => {
    const clientId = "client2";
    const wsConnection = new WebSocket(`ws://127.0.0.1:8000/ws/${clientId}`);

    wsConnection.onopen = () => {
      setStatus("Connected");
      console.log("WebSocket connected with ID:", clientId);
    };

    wsConnection.onmessage = (event) => {
      console.log("Received:", event.data);
      const data = JSON.parse(event.data);

      if (data.type === "progress") {
        // Show progress update
        setProgressMessage(data.message);
      } else if (data.type === "result") {
        // Final result arrived
        setMessages((prev) => [...prev, data.message]);
        setProgressMessage("");
        setWaitingResponse(false);
      } else if (data.type === "error") {
        // Error occurred
        setMessages((prev) => [...prev, `❌ Error: ${data.message}`]);
        setProgressMessage("");
        setWaitingResponse(false);
      }
    };

    wsConnection.onerror = (error) => {
      setStatus("Error");
      console.error("WebSocket error:", error);
      setWaitingResponse(false);
      setProgressMessage("");
    };

    wsConnection.onclose = (event) => {
      setStatus("Disconnected");
      console.log("WebSocket closed:", event.code, event.reason);
    };

    setWs(wsConnection);

    return () => {
      if (wsConnection.readyState === WebSocket.OPEN) {
        wsConnection.close();
      }
    };
  }, []);

  const sendMessage = () => {
    if (ws && ws.readyState === WebSocket.OPEN && inputMessage && !waitingResponse) {
      ws.send(inputMessage);
      setWaitingResponse(true);
      setProgressMessage("Sending your question...");
      setInputMessage("");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-3xl mx-auto bg-white rounded-xl shadow-2xl p-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">
          🤖 RAG Assistant
        </h1>
        <p className="text-gray-600 mb-6">Ask me anything and watch the magic happen!</p>

        {/* Status Badge */}
        <div className="mb-6 flex items-center gap-3">
          <span className="text-sm font-semibold text-gray-600">Status:</span>
          <span
            className={`px-3 py-1 rounded-full text-sm font-semibold ${
              status === "Connected"
                ? "bg-green-100 text-green-700"
                : status === "Error"
                ? "bg-red-100 text-red-700"
                : "bg-yellow-100 text-yellow-700"
            }`}
          >
            {status}
          </span>
        </div>

        {/* Progress Indicator */}
        {waitingResponse && progressMessage && (
          <div className="mb-4 p-4 bg-blue-50 border-l-4 border-blue-500 rounded animate-pulse">
            <p className="text-blue-700 font-medium">{progressMessage}</p>
          </div>
        )}

        {/* Input Area */}
        <div className="mb-6">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              placeholder="Ask your question here..."
              className="flex-1 p-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none transition"
              disabled={waitingResponse}
            />
            <button
              onClick={sendMessage}
              disabled={!ws || ws.readyState !== WebSocket.OPEN || waitingResponse || !inputMessage}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
            >
              {waitingResponse ? "⏳ Processing..." : "Send 🚀"}
            </button>
          </div>
        </div>

        {/* Messages Area */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-700 mb-3">Responses:</h2>
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-400 italic text-lg">No messages yet. Ask a question to get started!</p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                className="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 p-4 rounded-lg shadow-sm"
              >
                <p className="text-gray-800 leading-relaxed">{msg}</p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}