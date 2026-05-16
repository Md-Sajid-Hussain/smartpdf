// MergePDF.jsx - Create this as a separate component
import { useState } from "react";

function MergePDF() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles([...files, ...selectedFiles]);
  };

  const removeFile = (indexToRemove) => {
    setFiles(files.filter((_, index) => index !== indexToRemove));
  };

  const handleMerge = async () => {
    if (files.length < 2) {
      alert("Please select at least 2 PDF files to merge");
      return;
    }

    setLoading(true);

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("pdfs", file);
    });

    try {
      const res = await fetch(`https://smartpdf-bge7.onrender.com/api/merge-pdf/`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.error || "Merge failed");
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;

      // Auto-name: first file name + "_merged.pdf"
      const firstName = files[0].name;
      const nameWithoutExt = firstName.substring(0, firstName.lastIndexOf('.')) || firstName;
      const newFileName = `${nameWithoutExt}_merged.pdf`;
      
      a.download = newFileName;
      a.click();
      window.URL.revokeObjectURL(url);

      // Clear files after successful merge
      setFiles([]);
    } catch (error) {
      alert("Error merging PDFs: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h2>Merge PDF</h2>
      
      <div className="file-upload-area">
        <div className="file-input-wrapper">
          <input 
            type="file" 
            id="pdf-upload"
            accept=".pdf"
            multiple
            onChange={handleFileSelect}
            style={{ display: "none" }}
          />
          <button 
            className="btn btn-upload"
            onClick={() => document.getElementById("pdf-upload").click()}
          >
            Choose Files
          </button>
          <button 
            className="btn btn-add"
            onClick={() => document.getElementById("pdf-upload").click()}
          >
            + Add More
          </button>
        </div>
      </div>

      {files.length > 0 && (
        <div className="files-list">
          <h3>Selected Files ({files.length}):</h3>
          <ul className="file-items">
            {files.map((file, index) => (
              <li key={index} className="file-item">
                <span className="file-name">
                  {index === 0 && <span className="first-badge">First File</span>}
                  {file.name} ({(file.size / 1024).toFixed(2)} KB)
                </span>
                <button 
                  className="btn-remove"
                  onClick={() => removeFile(index)}
                >
                  ✕
                </button>
              </li>
            ))}
          </ul>
          <div className="merge-info">
            <p>📄 Will be merged as: <strong>{files[0]?.name.replace(/\.[^/.]+$/, "") || "document"}_merged.pdf</strong></p>
            <p className="info-text">✓ Files will be merged in the order shown above</p>
            <p className="info-text">✓ Minimum 2 files required (currently {files.length} file{files.length !== 1 ? 's' : ''})</p>
          </div>
        </div>
      )}

      <button 
        className="btn btn-merge" 
        onClick={handleMerge}
        disabled={loading || files.length < 2}
      >
        {loading ? "Merging..." : "Merge PDFs"}
      </button>
    </div>
  );
}

export default MergePDF;