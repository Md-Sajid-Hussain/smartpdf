import { Link } from "react-router-dom";
import { useState } from "react";

function EditNavbar({ 
  onDelete, 
  onInsert, 
  onPreview, 
  onAddText,
  onInsertImage,
  fontFamily,
  setFontFamily,
  fontSize,
  setFontSize,
  fontColor,
  setFontColor,
  isBold,
  setIsBold,
  isTransparent,
  setIsTransparent,
  onSave 
}) {
  const [deleteInput, setDeleteInput] = useState("");
  const [insertPageNum, setInsertPageNum] = useState("");
  const [insertImagePageNum, setInsertImagePageNum] = useState("");
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showInsertModal, setShowInsertModal] = useState(false);
  const [showImageModal, setShowImageModal] = useState(false);

  const fontOptions = [
    'Arial', 'Helvetica', 'Times New Roman', 'Courier New', 
    'Georgia', 'Verdana', 'Impact', 'Calibri', 'Cambria'
  ];

  const handleDeleteSubmit = () => {
    if (deleteInput.trim()) {
      onDelete(deleteInput);
      setDeleteInput("");
      setShowDeleteModal(false);
    }
  };

  const handleInsertSubmit = () => {
    if (insertPageNum.trim()) {
      const fileInput = document.createElement('input');
      fileInput.type = 'file';
      fileInput.accept = '.pdf';
      fileInput.onchange = (e) => {
        onInsert(insertPageNum, e.target.files[0]);
        setInsertPageNum("");
        setShowInsertModal(false);
      };
      fileInput.click();
    }
  };

  const handleImageSubmit = () => {
    if (insertImagePageNum.trim()) {
      const fileInput = document.createElement('input');
      fileInput.type = 'file';
      fileInput.accept = 'image/*';
      fileInput.onchange = (e) => {
        if (onInsertImage) {
          onInsertImage(insertImagePageNum, e.target.files[0]);
        }
        setInsertImagePageNum("");
        setShowImageModal(false);
      };
      fileInput.click();
    }
  };

  return (
    <>
      <div className="edit-navbar" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '10px 20px',
        backgroundColor: '#2c3e50',
        gap: '10px',
        flexWrap: 'wrap',
        color: 'white'
      }}>
        <h3 style={{ margin: 0, minWidth: '100px', color: 'white' }}>📄 PDF Editor</h3>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          flexWrap: 'wrap',
          flex: 1,
          justifyContent: 'center'
        }}>
          <button onClick={() => setShowDeleteModal(true)} style={{ backgroundColor: '#e74c3c', color: 'white', padding: '6px 12px', borderRadius: '4px', border: 'none', cursor: 'pointer' }}>
            🗑️ DELETE
          </button>

          <button onClick={() => setShowInsertModal(true)} style={{ backgroundColor: '#27ae60', color: 'white', padding: '6px 12px', borderRadius: '4px', border: 'none', cursor: 'pointer' }}>
            📄 INSERT PDF
          </button>

          <button onClick={() => setShowImageModal(true)} style={{ backgroundColor: '#f39c12', color: 'white', padding: '6px 12px', borderRadius: '4px', border: 'none', cursor: 'pointer' }}>
            🖼️ INSERT IMAGE
          </button>

          <button onClick={onPreview} style={{ backgroundColor: '#3498db', color: 'white', padding: '6px 12px', borderRadius: '4px', border: 'none', cursor: 'pointer' }}>
            👁️ PREVIEW
          </button>

          <button onClick={onAddText} style={{ backgroundColor: '#9b59b6', color: 'white', padding: '6px 12px', borderRadius: '4px', border: 'none', cursor: 'pointer' }}>
            ✏️ ADD TEXT
          </button>

          <select 
            value={fontFamily} 
            onChange={(e) => setFontFamily(e.target.value)}
            style={{ padding: '5px 8px', borderRadius: '4px', border: '1px solid #ccc' }}
          >
            {fontOptions.map(font => <option key={font} value={font}>{font}</option>)}
          </select>

          <input 
            type="number" 
            value={fontSize} 
            onChange={(e) => setFontSize(parseInt(e.target.value))}
            min="8"
            max="72"
            style={{ width: '55px', padding: '5px', borderRadius: '4px' }}
          />
          <span style={{ color: 'white' }}>px</span>

          <input 
            type="color" 
            value={fontColor} 
            onChange={(e) => setFontColor(e.target.value)}
            style={{ width: '35px', height: '30px', cursor: 'pointer', borderRadius: '4px' }}
          />

          <button onClick={() => setIsBold(!isBold)} style={{ 
            backgroundColor: isBold ? '#3498db' : '#7f8c8d', 
            color: 'white', 
            fontWeight: 'bold',
            padding: '5px 12px',
            borderRadius: '4px',
            border: 'none',
            cursor: 'pointer'
          }}>B</button>

          <button onClick={() => setIsTransparent(!isTransparent)} style={{ 
            backgroundColor: isTransparent ? '#2ecc71' : '#7f8c8d', 
            color: 'white',
            padding: '5px 12px',
            borderRadius: '4px',
            border: 'none',
            cursor: 'pointer'
          }}>T</button>

          <button onClick={onSave} style={{ backgroundColor: '#3498db', color: 'white', padding: '6px 15px', borderRadius: '4px', border: 'none', cursor: 'pointer' }}>
            💾 SAVE
          </button>
        </div>

        <Link to="/">
          <button style={{ backgroundColor: '#7f8c8d', color: 'white', padding: '6px 12px', borderRadius: '4px', border: 'none', cursor: 'pointer' }}>
            🏠 HOME
          </button>
        </Link>
      </div>

      {/* Delete Modal */}
      {showDeleteModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }}>
          <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', minWidth: '300px' }}>
            <h3>Delete Pages</h3>
            <input type="text" value={deleteInput} onChange={(e) => setDeleteInput(e.target.value)} placeholder="e.g., 1  or  1,2,4  or  1:5" style={{ width: '100%', padding: '8px', margin: '10px 0', borderRadius: '4px' }} />
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button onClick={() => setShowDeleteModal(false)}>Cancel</button>
              <button onClick={handleDeleteSubmit} style={{ backgroundColor: '#e74c3c', color: 'white' }}>Delete</button>
            </div>
          </div>
        </div>
      )}

      {/* Insert PDF Modal */}
      {showInsertModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }}>
          <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', minWidth: '300px' }}>
            <h3>Insert PDF After Page</h3>
            <input type="number" value={insertPageNum} onChange={(e) => setInsertPageNum(e.target.value)} placeholder="Page number" min="1" style={{ width: '100%', padding: '8px', margin: '10px 0', borderRadius: '4px' }} />
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button onClick={() => setShowInsertModal(false)}>Cancel</button>
              <button onClick={handleInsertSubmit} style={{ backgroundColor: '#27ae60', color: 'white' }}>Select PDF</button>
            </div>
          </div>
        </div>
      )}

      {/* Insert Image Modal */}
      {showImageModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }}>
          <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', minWidth: '300px' }}>
            <h3>Insert Image at Page</h3>
            <input type="number" value={insertImagePageNum} onChange={(e) => setInsertImagePageNum(e.target.value)} placeholder="Page number" min="1" style={{ width: '100%', padding: '8px', margin: '10px 0', borderRadius: '4px' }} />
            <p style={{ fontSize: '12px', color: '#666' }}>Image will be inserted at coordinates (100, 100)</p>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button onClick={() => setShowImageModal(false)}>Cancel</button>
              <button onClick={handleImageSubmit} style={{ backgroundColor: '#f39c12', color: 'white' }}>Select Image</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default EditNavbar;