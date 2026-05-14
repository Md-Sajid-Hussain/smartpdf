import { useState, useEffect, useRef } from "react";
import "./split.css";

function SplitPDF() {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploaded, setUploaded] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [totalPages, setTotalPages] = useState(0);
  
  // Chatbot states
  const [messages, setMessages] = useState([
    { type: "bot", text: "Hello! I'm Ginny 🤖. Upload a PDF and tell me how to split it!" }
  ]);
  const [inputText, setInputText] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  
  // UI states
  const [confirmationMessage, setConfirmationMessage] = useState(null);
  const [showDownload, setShowDownload] = useState(false);
  const [downloadUrls, setDownloadUrls] = useState({ pdf: null, zip: null });
  
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Suggestions based on input
  useEffect(() => {
    if (inputText.length > 0) {
      const lowerInput = inputText.toLowerCase();
      const allSuggestions = [
        "Split into single pages",
        "Divide into 2 equal parts",
        "Divide into 3 equal parts",
        "Group every 3 pages together",
        "Group every 5 pages together",
        "Extract pages: 1,3,5,7",
        "Extract pages: 1-5,10-15",
        "Split as ranges: 1-5,6-10,11-15",
        "Split as: 1-3,4-7,8-12",
        "Get pages 1 to 10 only",
        "Remove first 5 pages"
      ];
      const filtered = allSuggestions.filter(s => 
        s.toLowerCase().includes(lowerInput)
      );
      setSuggestions(filtered.slice(0, 5));
      setShowSuggestions(filtered.length > 0);
    } else {
      setShowSuggestions(false);
    }
  }, [inputText]);

  // Handle file upload
  const handleFileUpload = async (selectedFile) => {
    if (!selectedFile) return;
    
    setLoading(true);
    const formData = new FormData();
    formData.append("pdf", selectedFile);
    
    try {
      const response = await fetch("http://127.0.0.1:8000/api/split/upload/", {
        method: "POST",
        body: formData
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setSessionId(data.session_id);
        setTotalPages(data.total_pages);
        setFileName(selectedFile.name);
        setUploaded(true);
        
        setMessages(prev => [...prev, 
          { type: "bot", text: `✅ Uploaded "${selectedFile.name}" (${data.total_pages} pages)\n\nHow would you like to split it?` }
        ]);
        
        setConfirmationMessage({
          type: "success",
          text: `File uploaded successfully: ${selectedFile.name} (${data.total_pages} pages)`
        });
        
        setTimeout(() => setConfirmationMessage(null), 5000);
      } else {
        throw new Error(data.error || "Upload failed");
      }
    } catch (error) {
      setMessages(prev => [...prev, 
        { type: "bot", text: `❌ Upload failed: ${error.message}. Please try again.` }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Send command to backend
  const sendCommand = async (command) => {
    if (!command.trim() || !sessionId || isProcessing) return;
    
    setIsProcessing(true);
    setMessages(prev => [...prev, { type: "user", text: command }]);
    setInputText("");
    setShowSuggestions(false);
    
    try {
      const response = await fetch("http://127.0.0.1:8000/api/split/command/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          command: command
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        if (data.needs_confirmation) {
          setMessages(prev => [...prev, 
            { type: "bot", text: `${data.message}\n\nType "confirm" to proceed or "cancel" to abort.` }
          ]);
        } else if (data.success) {
          setMessages(prev => [...prev, 
            { type: "bot", text: data.message }
          ]);
          
          setConfirmationMessage({
            type: "success",
            text: data.message
          });
          
          if (data.download_ready) {
            setShowDownload(true);
            setDownloadUrls({
              pdf: `http://127.0.0.1:8000/api/split/download/${sessionId}/pdf/`,
              zip: `http://127.0.0.1:8000/api/split/download/${sessionId}/zip/`
            });
          }
          
          setTimeout(() => setConfirmationMessage(null), 5000);
        }
      } else {
        throw new Error(data.error || "Command failed");
      }
    } catch (error) {
      setMessages(prev => [...prev, 
        { type: "bot", text: `❌ Error: ${error.message}. Please try again.` }
      ]);
    } finally {
      setIsProcessing(false);
    }
  };

  // Handle form submit
  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputText.trim()) {
      if (!uploaded) {
        setMessages(prev => [...prev, 
          { type: "bot", text: "⚠️ Please upload a PDF file first!" }
        ]);
        return;
      }
      sendCommand(inputText);
    }
  };

  // Handle suggestion click
  const handleSuggestionClick = (suggestion) => {
    setInputText(suggestion);
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  // Handle dropdown selection
  const handleDropdownSelect = (operation, value = null) => {
    let command = "";
    switch(operation) {
      case "single":
        command = "Split into single pages";
        break;
      case "two_parts":
        command = "Divide into 2 equal parts";
        break;
      case "group":
        const num = value || prompt("Enter number of pages per group:", "3");
        if (num) command = `Group every ${num} pages together`;
        break;
      case "extract_ranges":
        const ranges = prompt("Enter page ranges (e.g., 1,3,5,7 or 1-5,10-15):", "1,3,5,7");
        if (ranges) command = `Extract pages: ${ranges}`;
        break;
      case "custom_ranges":
        const customRanges = prompt("Enter non-overlapping ranges (e.g., 1-5,6-10,11-15):", "1-5,6-10");
        if (customRanges) command = `Split as ranges: ${customRanges}`;
        break;
      default:
        return;
    }
    if (command) {
      setInputText(command);
      sendCommand(command);
    }
  };

  // Handle download
  const handleDownload = (type) => {
    if (downloadUrls[type]) {
      window.open(downloadUrls[type], '_blank');
    }
  };

  // Clear upload (upload new file)
  const handleNewFile = () => {
    setFile(null);
    setFileName("");
    setUploaded(false);
    setSessionId(null);
    setShowDownload(false);
    setDownloadUrls({ pdf: null, zip: null });
    setMessages([
      { type: "bot", text: "Hello! I'm Ginny 🤖. Upload a PDF and tell me how to split it!" }
    ]);
    fileInputRef.current?.click();
  };

  return (
    <div className="split-container">
      {/* Confirmation Area - Below Navbar */}
      {confirmationMessage && (
        <div className={`confirmation-message ${confirmationMessage.type}`}>
          <span>{confirmationMessage.text}</span>
          <button onClick={() => setConfirmationMessage(null)}>×</button>
        </div>
      )}

      {/* Main Content Area */}
      <div className="main-content">
        {/* File Upload Section - Hidden after upload */}
        {!uploaded && (
          <div className="upload-section">
            <div className="upload-card">
              <div className="upload-icon">📄</div>
              <h3>Upload PDF File</h3>
              <p>Choose a PDF file to split</p>
              <input 
                ref={fileInputRef}
                type="file" 
                accept=".pdf"
                onChange={(e) => handleFileUpload(e.target.files[0])}
                style={{ display: 'none' }}
              />
              <button 
                className="upload-btn"
                onClick={() => fileInputRef.current?.click()}
                disabled={loading}
              >
                {loading ? "Uploading..." : "Select PDF"}
              </button>
            </div>
          </div>
        )}

        {/* Uploaded File Info */}
        {uploaded && (
          <div className="file-info">
            <div className="file-details">
              <span className="file-icon">📑</span>
              <span className="file-name">{fileName}</span>
              <span className="file-pages">({totalPages} pages)</span>
              <button className="change-file-btn" onClick={handleNewFile}>
                Change File
              </button>
            </div>
          </div>
        )}

        {/* Download Area - Shows only after operation */}
        {showDownload && (
          <div className="download-section">
            <div className="download-card">
              <h4>✅ Split Complete!</h4>
              <div className="download-buttons">
                <button 
                  className="download-btn pdf-btn"
                  onClick={() => handleDownload('pdf')}
                >
                  📄 Download as PDF
                </button>
                <button 
                  className="download-btn zip-btn"
                  onClick={() => handleDownload('zip')}
                >
                  📦 Download as ZIP
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Ginny Chatbot - Bottom Right Corner */}
      <div className="chatbot-wrapper">
        <div className="chatbot-container">
          <div className="chatbot-header">
            <div className="header-content">
              <span className="bot-avatar">🤖</span>
              <div>
                <h3>Ginny</h3>
                <p>Your PDF Assistant</p>
              </div>
            </div>
            <div className="dropdown-actions">
              <select 
                className="operation-dropdown"
                onChange={(e) => {
                  if(e.target.value) handleDropdownSelect(e.target.value);
                  e.target.value = "";
                }}
                value=""
              >
                <option value="">Quick Actions ▼</option>
                <option value="single">📄 Split into single pages</option>
                <option value="two_parts">✂️ Divide into 2 equal parts</option>
                <option value="group">📚 Group every N pages</option>
                <option value="extract_ranges">🎯 Extract specific pages/ranges</option>
                <option value="custom_ranges">🔧 Split by custom ranges</option>
              </select>
            </div>
          </div>

          <div className="chatbot-messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.type}`}>
                <div className="message-content">
                  {msg.type === "bot" && <span className="message-avatar">🤖</span>}
                  <div className="message-text">
                    {msg.text.split('\n').map((line, i) => (
                      <p key={i}>{line}</p>
                    ))}
                  </div>
                  {msg.type === "user" && <span className="message-avatar">👤</span>}
                </div>
              </div>
            ))}
            {isProcessing && (
              <div className="message bot">
                <div className="message-content">
                  <span className="message-avatar">🤖</span>
                  <div className="message-text typing">
                    <span>.</span><span>.</span><span>.</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <form className="chatbot-input-form" onSubmit={handleSubmit}>
            <div className="input-wrapper">
              <input
                ref={inputRef}
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Type your command... (e.g., 'split into single pages')"
                disabled={!uploaded || isProcessing}
                className="chat-input"
              />
              {showSuggestions && (
                <div className="suggestions-dropdown">
                  {suggestions.map((suggestion, idx) => (
                    <div 
                      key={idx}
                      className="suggestion-item"
                      onClick={() => handleSuggestionClick(suggestion)}
                    >
                      💡 {suggestion}
                    </div>
                  ))}
                </div>
              )}
              <button 
                type="submit" 
                disabled={!uploaded || isProcessing || !inputText.trim()}
                className="send-btn"
              >
                {isProcessing ? "..." : "Send"}
              </button>
            </div>
            <button 
              type="button"
              onClick={() => sendCommand(inputText)}
              className="execute-btn"
              disabled={!uploaded || isProcessing || !inputText.trim()}
            >
              Execute
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default SplitPDF;