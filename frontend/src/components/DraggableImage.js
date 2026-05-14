import { useState, useRef, useEffect } from 'react';

function DraggableImage({ id, imageUrl, position, setPosition, onDelete, onSelect, isSelected, width, height, setSize }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, width: 0, height: 0 });
  const imgRef = useRef(null);

  const handleMouseDown = (e) => {
    if (e.target.classList.contains('resize-handle')) return;
    
    e.stopPropagation();
    setIsDragging(true);
    setDragStart({
      x: e.clientX - position.x,
      y: e.clientY - position.y
    });
    onSelect(id);
  };

  const handleResizeStart = (e) => {
    e.stopPropagation();
    setIsResizing(true);
    setResizeStart({
      x: e.clientX,
      y: e.clientY,
      width: width,
      height: height
    });
    onSelect(id);
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      const newX = e.clientX - dragStart.x;
      const newY = e.clientY - dragStart.y;
      setPosition(id, { x: newX, y: newY });
    } else if (isResizing) {
      const deltaX = e.clientX - resizeStart.x;
      const deltaY = e.clientY - resizeStart.y;
      const newWidth = Math.max(50, resizeStart.width + deltaX);
      const newHeight = Math.max(50, resizeStart.height + deltaY);
      setSize(id, newWidth, newHeight);
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    setIsResizing(false);
  };

  useEffect(() => {
    if (isDragging || isResizing) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, isResizing]);

  return (
    <div
      style={{
        position: 'absolute',
        left: position.x,
        top: position.y,
        cursor: isDragging ? 'grabbing' : 'grab',
        zIndex: isSelected ? 1000 : 1,
        border: isSelected ? '2px solid #007bff' : 'none',
        borderRadius: '4px',
        display: 'inline-block'
      }}
      onMouseDown={handleMouseDown}
    >
      <img
        ref={imgRef}
        src={imageUrl}
        alt="Inserted"
        style={{
          width: width,
          height: height,
          objectFit: 'contain',
          pointerEvents: 'none'
        }}
      />
      {isSelected && (
        <>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(id);
            }}
            style={{
              position: 'absolute',
              top: '-12px',
              right: '-12px',
              background: 'red',
              color: 'white',
              border: 'none',
              borderRadius: '50%',
              width: '24px',
              height: '24px',
              cursor: 'pointer',
              fontSize: '18px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1001
            }}
          >
            ×
          </button>
          <div
            className="resize-handle"
            style={{
              position: 'absolute',
              bottom: '-5px',
              right: '-5px',
              width: '12px',
              height: '12px',
              backgroundColor: '#007bff',
              cursor: 'se-resize',
              borderRadius: '2px',
              zIndex: 1002
            }}
            onMouseDown={handleResizeStart}
          />
        </>
      )}
    </div>
  );
}

export default DraggableImage;