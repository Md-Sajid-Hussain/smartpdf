import Draggable from "react-draggable";
import { useState, useEffect, useRef } from "react";

function DraggableText({
  id,
  text,
  position,
  setPosition,
  onDelete,
  onSelect,
  onTextChange,
  isSelected,
  fontFamily = "Arial",
  fontSize = 16,
  fontColor = "#000000",
  isBold = false,
  isTransparent = true
}) {
  const [currentText, setCurrentText] = useState(text);
  const divRef = useRef(null);

  useEffect(() => {
    setCurrentText(text);
  }, [text]);

  const handleDeleteClick = (e) => {
    e.stopPropagation();
    onDelete(id);
  };

  const handleTextChange = (e) => {
    const newText = e.target.innerText;
    setCurrentText(newText);
    if (onTextChange) {
      onTextChange(id, newText);
    }
  };

  const handleDoubleClick = (e) => {
    e.stopPropagation();
    const target = e.target;
    if (window.getSelection) {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(target);
      selection.removeAllRanges();
      selection.addRange(range);
    }
  };

  const handleBoxClick = (e) => {
    e.stopPropagation();
    if (onSelect) {
      onSelect(id);
    }
  };

  return (
    <div
      ref={divRef}
      className="draggable-text-wrapper"
      style={{
        position: 'absolute',
        left: 0,
        top: 0,
        zIndex: 1000
      }}
    >
      <Draggable
        defaultPosition={{ x: position.x, y: position.y }}
        onStop={(e, data) => {
          setPosition(id, { x: data.x, y: data.y });
        }}
      >
        <div
          onClick={handleBoxClick}
          className={`draggable-text-box ${isSelected ? 'selected' : ''}`}
          style={{
            backgroundColor: isTransparent ? 'transparent' : 'white',
            padding: '4px',
            borderRadius: '6px',
            minWidth: '20px',
            width: 'max-content',
            border: isSelected ? '2px dashed #4CAF50' : '1px solid transparent',
            boxShadow: isSelected ? '0 2px 8px rgba(0,0,0,0.1)' : 'none',
            cursor: 'move'
          }}
        >
          {isSelected && (
            <div
              onClick={handleDeleteClick}
              className="cut-button"
            >
              ✕
            </div>
          )}

          <div
            id={`text-content-${id}`}
            contentEditable
            suppressContentEditableWarning
            onBlur={handleTextChange}
            onDoubleClick={handleDoubleClick}
            className="draggable-text-content"
            style={{
              fontSize: `${fontSize}px`,
              fontFamily: fontFamily,
              color: fontColor,
              fontWeight: isBold ? 'bold' : 'normal',
              background: 'transparent'
            }}
          >
            {currentText}
          </div>
        </div>
      </Draggable>
    </div>
  );
}

export default DraggableText;