import { useState, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';

// Set up PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

function PDFViewer({ file, onPageLoad, onDocumentLoad, currentPage }) {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [scale, setScale] = useState(1.0);
  const [pdfUrl, setPdfUrl] = useState(null);

  useEffect(() => {
    if (file) {
      const url = URL.createObjectURL(file);
      setPdfUrl(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [file]);

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
    setPageNumber(1);
    if (onDocumentLoad) {
      onDocumentLoad({ numPages });
    }
  };

  const onPageLoadSuccess = (page) => {
    if (onPageLoad) {
      onPageLoad({ pageNumber, width: page.width, height: page.height });
    }
  };

  const goToPrevPage = () => {
    setPageNumber(prev => Math.max(prev - 1, 1));
  };

  const goToNextPage = () => {
    setPageNumber(prev => Math.min(prev + 1, numPages));
  };

  const zoomIn = () => {
    setScale(prev => Math.min(prev + 0.2, 2.5));
  };

  const zoomOut = () => {
    setScale(prev => Math.max(prev - 0.2, 0.5));
  };

  if (!pdfUrl) {
    return <div style={{ padding: '20px', textAlign: 'center' }}>Loading PDF...</div>;
  }

  return (
    <div style={{ 
      width: '100%', 
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#f0f0f0',
      borderRadius: '8px',
      overflow: 'hidden'
    }}>
      {/* PDF Toolbar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '15px',
        padding: '10px',
        backgroundColor: '#fff',
        borderBottom: '1px solid #ddd',
        flexWrap: 'wrap'
      }}>
        <button onClick={zoomOut} className="btn" style={{ padding: '5px 10px' }}>🔍 Zoom Out</button>
        <button onClick={zoomIn} className="btn" style={{ padding: '5px 10px' }}>🔍 Zoom In</button>
        <span>Scale: {Math.round(scale * 100)}%</span>
        <div style={{ width: '1px', height: '20px', backgroundColor: '#ddd', margin: '0 10px' }} />
        <button onClick={goToPrevPage} disabled={pageNumber <= 1} className="btn">◀ Previous</button>
        <span>Page {pageNumber} of {numPages || '?'}</span>
        <button onClick={goToNextPage} disabled={pageNumber >= numPages} className="btn">Next ▶</button>
      </div>

      {/* PDF Canvas Container */}
      <div style={{
        flex: 1,
        overflow: 'auto',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '20px',
        minHeight: '500px'
      }}>
        <Document
          file={pdfUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          loading={<div>Loading PDF...</div>}
          error={<div>Failed to load PDF. Please try again.</div>}
        >
          <Page
            pageNumber={currentPage || pageNumber}
            scale={scale}
            onLoadSuccess={onPageLoadSuccess}
            renderTextLayer={true}
            renderAnnotationLayer={true}
          />
        </Document>
      </div>
    </div>
  );
}

export default PDFViewer;