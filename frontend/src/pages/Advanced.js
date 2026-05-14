import React, { useState } from 'react';
import './Advanced.css';

import jsPDF from 'jspdf';

const API_BASE = 'http://https://smartpdf-bge7.onrender.com/api';


/* =========================================================
   PDF EXPORT
========================================================= */

const downloadAsPDF = (title, content) => {

  const doc = new jsPDF();

  const margin = 15;

  const pageWidth = doc.internal.pageSize.getWidth();

  const maxLineWidth = pageWidth - margin * 2;

  const lines = doc.splitTextToSize(
    content,
    maxLineWidth
  );

  doc.setFont("helvetica");

  doc.setFontSize(16);

  doc.text(title, margin, 20);

  doc.setFontSize(12);

  let y = 35;

  lines.forEach((line) => {

    if (y > 280) {
      doc.addPage();
      y = 20;
    }

    doc.text(line, margin, y);

    y += 7;
  });

  doc.save(
    `${title.replace(/\s+/g, "_")}.pdf`
  );
};


/* =========================================================
   RESULT MODAL
========================================================= */

const ResultModal = ({
  isOpen,
  onClose,
  title,
  content,
  downloadUrl
}) => {

  if (!isOpen) return null;

  return (

    <div
      className="modal-overlay"
      onClick={onClose}
    >

      <div
        className="modal-content"
        onClick={(e) => e.stopPropagation()}
      >

        <div className="modal-header">

          <h2>{title} Result</h2>

          <button
            className="close-btn"
            onClick={onClose}
          >
            ✖
          </button>

        </div>

        <div className="result-container">

          <pre className="result-text">
            {content}
          </pre>

        </div>

        <div className="modal-actions">

          {/* COPY BUTTON */}

          <button
            className="btn-secondary"
            onClick={() => {

              navigator.clipboard.writeText(content);

              alert('Copied to clipboard!');
            }}
          >
            Copy Text
          </button>

          {/* DOWNLOAD BUTTON */}

          <button
            className="btn-download"
            onClick={() => {

              // OCR CLEAN PDF
              if (downloadUrl) {

                const doc = new jsPDF();

                const margin = 15;

                const pageWidth =
                  doc.internal.pageSize.getWidth();

                const maxLineWidth =
                  pageWidth - margin * 2;

                const lines = doc.splitTextToSize(
                  content,
                  maxLineWidth
                );

                doc.setFont("times");

                let y = 20;

                // Title
                doc.setFontSize(16);

                doc.text(
                  "OCR Extracted Text",
                  margin,
                  y
                );

                y += 15;

                doc.setFontSize(12);

                lines.forEach((line) => {

                  if (y > 280) {

                    doc.addPage();

                    y = 20;
                  }

                  doc.text(
                    line,
                    margin,
                    y
                  );

                  y += 7;
                });

                doc.save(
                  "OCR_Extracted_Text.pdf"
                );

              }

              // OTHER FEATURES
              else {

                downloadAsPDF(
                  title,
                  content
                );
              }

            }}
          >
            Download PDF
          </button>

        </div>

      </div>

    </div>
  );
};

/* =========================================================
   TOOL CARD
========================================================= */

const ToolCard = ({
  title,
  description,
  icon,
  endpoint,
  actionName,
  showNotification
}) => {

  const [file, setFile] = useState(null);

  const [loading, setLoading] = useState(false);

  const [result, setResult] = useState(null);

  const [downloadUrl, setDownloadUrl] =
    useState(null);


  /* =========================================================
     FILE CHANGE
  ========================================================= */

  const handleFileChange = (e) => {

    const selectedFile = e.target.files[0];

    if (!selectedFile) return;

    // PDF validation

    if (
      selectedFile.type !== 'application/pdf'
    ) {

      showNotification(
        'Only PDF files are allowed',
        'error'
      );

      return;
    }

    // 20MB limit

    if (
      selectedFile.size > 20 * 1024 * 1024
    ) {

      showNotification(
        'File size exceeds 20MB limit',
        'error'
      );

      return;
    }

    setFile(selectedFile);
  };


  /* =========================================================
     SUBMIT
  ========================================================= */

  const handleSubmit = async () => {

    if (!file) return;

    setLoading(true);

    const formData = new FormData();

    formData.append('file', file);

    try {

      const response = await fetch(
        `${API_BASE}${endpoint}`,
        {
          method: 'POST',
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {

        throw new Error(
          data.error || 'Processing failed'
        );
      }

      /* =========================================
         OCR HANDLING
      ========================================= */

      if (endpoint === "/ocr/") {

        setResult(
          data.extracted_text ||
          "No text extracted"
        );

        setDownloadUrl(
          `http://https://smartpdf-bge7.onrender.com${data.download_url}`
        );

      }

      /* =========================================
         OTHER AI FEATURES
      ========================================= */

      else {

        setResult(
          data.result ||
          "No result generated"
        );

        setDownloadUrl(null);
      }

      showNotification(
        `${title} completed successfully!`,
        'success'
      );

    } catch (error) {

      console.error(error);

      showNotification(
        error.message,
        'error'
      );

    } finally {

      setLoading(false);
    }
  };


  return (
    <>
      <div className="tool-card">

        <div className="card-icon">
          {icon}
        </div>

        <h2>{title}</h2>

        <p>{description}</p>

        <div className="file-input-wrapper">

          <label className="file-input-button">

            📄 {file ? file.name : 'Choose PDF'}

            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              hidden
            />

          </label>

        </div>

        <button
          className="submit-btn"
          onClick={handleSubmit}
          disabled={!file || loading}
        >

          {loading ? (
            <>
              <div className="spinner"></div>
              Processing...
            </>
          ) : (
            actionName
          )}

        </button>

      </div>

      <ResultModal
        isOpen={!!result}
        onClose={() => {
          setResult(null);
          setDownloadUrl(null);
        }}
        title={title}
        content={result}
        downloadUrl={downloadUrl}
      />
    </>
  );
};


/* =========================================================
   MAIN PAGE
========================================================= */

const Advanced = () => {

  const [notification, setNotification] =
    useState(null);


  const showNotification = (
    message,
    type = 'success'
  ) => {

    setNotification({
      message,
      type
    });

    setTimeout(() => {
      setNotification(null);
    }, 4000);
  };


  return (

    <div className="advanced-container">

      <div className="advanced-header">

        <h1>
          AI-Powered PDF Intelligence
        </h1>

        <p>
          OCR, Summarization, Question
          Generation & AI Notes from PDFs.
        </p>

      </div>


      <div className="cards-grid">

        <ToolCard
          title="OCR For Scanned PDF"
          description="Turn scanned PDFs into selectable text."
          icon="🔍"
          endpoint="/ocr/"
          actionName="Extract Text"
          showNotification={showNotification}
        />

        <ToolCard
          title="Docs Summarization"
          description="Generate concise intelligent summaries."
          icon="📝"
          endpoint="/summarize/"
          actionName="Summarize PDF"
          showNotification={showNotification}
        />

        <ToolCard
          title="Questions Generator"
          description="Generate study questions automatically."
          icon="❓"
          endpoint="/generate-questions/"
          actionName="Generate Questions"
          showNotification={showNotification}
        />

        <ToolCard
          title="Make Notes"
          description="Generate structured AI notes."
          icon="📘"
          endpoint="/make-notes/"
          actionName="Generate Notes"
          showNotification={showNotification}
        />

      </div>

      {notification && (

        <div
          className={`notification ${notification.type}`}
        >
          {notification.message}
        </div>

      )}

    </div>
  );
};

export default Advanced;