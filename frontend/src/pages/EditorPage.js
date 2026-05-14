// import { useState, useEffect, useRef } from "react";
// import PDFViewer from "../components/PDFViewer";
// import DraggableText from "../components/DraggableText";
// import EditNavbar from "../components/EditNavbar";
// import { replaceText, deletePages, insertImage } from "../utils/api";

// function EditorPage() {
//   const [file, setFile] = useState(null);
//   const [originalFileName, setOriginalFileName] = useState("");
//   const [textElements, setTextElements] = useState([]);
//   const [nextId, setNextId] = useState(1);
//   const [selectedTextId, setSelectedTextId] = useState(null);
//   const [pdfDimensions, setPdfDimensions] = useState({ width: 0, height: 0 });
  
//   // Font controls state
//   const [fontFamily, setFontFamily] = useState("Arial");
//   const [fontSize, setFontSize] = useState(16);
//   const [fontColor, setFontColor] = useState("#000000");
//   const [isBold, setIsBold] = useState(false);
//   const [isTransparent, setIsTransparent] = useState(true);

//   const viewerRef = useRef(null);

//   // Get center position of PDF viewer
//   const getCenterPosition = () => {
//     if (pdfDimensions.width && pdfDimensions.height) {
//       return {
//         x: pdfDimensions.width / 2 - 100,
//         y: pdfDimensions.height / 2 - 50
//       };
//     }
//     return { x: 200, y: 200 };
//   };

// const handleAddText = () => {
//   console.log("Add Text clicked");
  
//   // Create text at a fixed position (top-left of PDF area)
//   const newTextElement = {
//     id: nextId,
//     text: "Edit this text",
//     position: { x: 100, y: 100 },  // Fixed position
//     fontFamily: fontFamily,
//     fontSize: fontSize,
//     fontColor: fontColor,
//     isBold: isBold,
//     isTransparent: isTransparent
//   };
  
//   console.log("New text element:", newTextElement);
  
//   setTextElements(prev => [...prev, newTextElement]);
//   setNextId(prev => prev + 1);
//   setSelectedTextId(nextId);
// };

//   // Update text element position
//   const updateTextPosition = (id, newPosition) => {
//     setTextElements(prev => prev.map(el => 
//       el.id === id ? { ...el, position: newPosition } : el
//     ));
//   };

//   // Update text element content
//   const updateTextContent = (id, newText) => {
//     setTextElements(prev => prev.map(el => 
//       el.id === id ? { ...el, text: newText } : el
//     ));
//   };

//   // Delete text element
//   const deleteTextElement = (id) => {
//     setTextElements(prev => prev.filter(el => el.id !== id));
//     if (selectedTextId === id) {
//       setSelectedTextId(null);
//     }
//   };

//   // Select text element
//   const selectTextElement = (id) => {
//     setSelectedTextId(id);
//     const selected = textElements.find(el => el.id === id);
//     if (selected) {
//       setFontFamily(selected.fontFamily);
//       setFontSize(selected.fontSize);
//       setFontColor(selected.fontColor);
//       setIsBold(selected.isBold);
//       setIsTransparent(selected.isTransparent);
//     }
//   };

//   // Update selected text element with font changes
//   useEffect(() => {
//     if (selectedTextId) {
//       setTextElements(prevElements => 
//         prevElements.map(el => 
//           el.id === selectedTextId ? { 
//             ...el, 
//             fontFamily, fontSize, fontColor, isBold, isTransparent
//           } : el
//         )
//       );
//     }
//   }, [fontFamily, fontSize, fontColor, isBold, isTransparent, selectedTextId]);

//   // Handle PDF page load to get dimensions
//   const handlePageLoad = ({ width, height }) => {
//     setPdfDimensions({ width, height });
//   };

//   // Delete pages
//   const handleDelete = async (pageInput) => {
//     if (!file) {
//       alert("Please upload a PDF first");
//       return;
//     }

//     try {
//       const response = await deletePages(file, pageInput);
//       const blob = await response.blob();
//       const newFile = new File([blob], originalFileName || "edited.pdf", { type: "application/pdf" });
//       setFile(newFile);
//       alert("Pages deleted successfully!");
//     } catch (err) {
//       console.error(err);
//       alert("Error deleting pages: " + err.message);
//     }
//   };

//   // Insert PDF
//   const handleInsert = async (pageNum, insertFile) => {
//     if (!file || !insertFile) {
//       alert("Please upload a PDF and select a file");
//       return;
//     }

//     try {
//       const formData = new FormData();
//       formData.append("file", file);
//       formData.append("insert_file", insertFile);
//       formData.append("after_page", pageNum);
      
//       const response = await fetch('http://127.0.0.1:8000/insert-pdf/', {
//         method: 'POST',
//         body: formData,
//       });
//       const blob = await response.blob();
//       const newFile = new File([blob], originalFileName || "edited.pdf", { type: "application/pdf" });
//       setFile(newFile);
//       alert("PDF inserted successfully!");
//     } catch (err) {
//       console.error(err);
//       alert("Error inserting PDF");
//     }
//   };

//   // Insert Image
//   const handleInsertImage = async (pageNum, imageFile) => {
//     if (!file || !imageFile) {
//       alert("Please upload a PDF and select an image");
//       return;
//     }

//     try {
//       const response = await insertImage(file, imageFile, pageNum, 100, 100);
//       const blob = await response.blob();
//       const newFile = new File([blob], originalFileName || "edited.pdf", { type: "application/pdf" });
//       setFile(newFile);
//       alert("Image inserted successfully!");
//     } catch (err) {
//       console.error(err);
//       alert("Error inserting image: " + err.message);
//     }
//   };

//   // Helper to get latest text data directly from DOM to avoid React stale closure issues if user doesn't blur
//   const getLatestTextData = () => {
//     return textElements.map(el => {
//       const domNode = document.getElementById(`text-content-${el.id}`);
//       const latestText = domNode ? domNode.innerText : el.text;
      
//       return {
//         text: latestText,
//         x: el.position.x,
//         y: el.position.y,
//         page: 1,
//         fontSize: el.fontSize,
//         fontFamily: el.fontFamily,
//         fontColor: el.fontColor,
//         isBold: el.isBold
//       };
//     });
//   };

//   // Preview PDF
//   const handlePreview = async () => {
//     if (!file) {
//       alert("Please upload a PDF first");
//       return;
//     }

//     if (textElements.length === 0) {
//       const url = URL.createObjectURL(file);
//       window.open(url, "_blank");
//       setTimeout(() => URL.revokeObjectURL(url), 1000);
//       return;
//     }

//     const textData = getLatestTextData();

//     try {
//       const response = await replaceText(file, textData);
//       const blob = await response.blob();
//       const url = URL.createObjectURL(blob);
//       window.open(url, "_blank");
//       setTimeout(() => URL.revokeObjectURL(url), 1000);
//     } catch (err) {
//       console.error(err);
//       alert("Error generating preview: " + err.message);
//     }
//   };

//   // Save PDF with text
//   const handleSave = async () => {
//     if (!file) {
//       alert("Please upload a PDF");
//       return;
//     }

//     if (textElements.length === 0) {
//       alert("No text to save. Add some text first.");
//       return;
//     }

//     const textData = getLatestTextData();

//     try {
//       const response = await replaceText(file, textData);
//       const blob = await response.blob();
      
//       // Create filename with _edited suffix
//       const fileName = originalFileName 
//         ? originalFileName.replace('.pdf', '_edited.pdf')
//         : 'edited.pdf';
      
//       // Download the edited PDF
//       const url = URL.createObjectURL(blob);
//       const a = document.createElement('a');
//       a.href = url;
//       a.download = fileName;
//       a.click();
      
//       // Update the current file with edited version
//       const editedFile = new File([blob], fileName, { type: "application/pdf" });
//       setFile(editedFile);
      
//       URL.revokeObjectURL(url);
//       alert("PDF saved successfully!");
//     } catch (err) {
//       console.error(err);
//       alert("Error saving PDF: " + err.message);
//     }
//   };

//   return (
//     <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
//       <EditNavbar 
//         onDelete={handleDelete}
//         onInsert={handleInsert}
//         onInsertImage={handleInsertImage}
//         onPreview={handlePreview}
//         onAddText={handleAddText}
//         fontFamily={fontFamily}
//         setFontFamily={setFontFamily}
//         fontSize={fontSize}
//         setFontSize={setFontSize}
//         fontColor={fontColor}
//         setFontColor={setFontColor}
//         isBold={isBold}
//         setIsBold={setIsBold}
//         isTransparent={isTransparent}
//         setIsTransparent={setIsTransparent}
//         onSave={handleSave}
//       />

//       <div style={{ padding: "20px", flex: 1, display: 'flex', flexDirection: 'column' }}>
//         <input 
//           type="file" 
//           accept="application/pdf" 
//           onChange={(e) => {
//             const selectedFile = e.target.files[0];
//             setFile(selectedFile);
//             setOriginalFileName(selectedFile.name);
//             setTextElements([]);
//             setNextId(1);
//             setSelectedTextId(null);
//           }} 
//         />

//         {file && (
//           <div 
//             ref={viewerRef}
//             onClick={() => setSelectedTextId(null)}
//             style={{ 
//               position: "relative", 
//               marginTop: "20px",
//               flex: 1,
//               minHeight: "500px",
//               border: '1px solid #ddd',
//               borderRadius: '8px',
//               overflow: 'hidden'
//             }}
//           >
//             <PDFViewer 
//               file={file} 
//               onPageLoad={handlePageLoad}
//               onDocumentLoad={(info) => console.log('PDF loaded:', info)}
//             />
            
//             {textElements.map((element) => (
//               <DraggableText
//                 key={element.id}
//                 id={element.id}
//                 text={element.text}
//                 position={element.position}
//                 setPosition={updateTextPosition}
//                 onDelete={deleteTextElement}
//                 onSelect={selectTextElement}
//                 onTextChange={updateTextContent}
//                 isSelected={selectedTextId === element.id}
//                 fontFamily={element.fontFamily}
//                 fontSize={element.fontSize}
//                 fontColor={element.fontColor}
//                 isBold={element.isBold}
//                 isTransparent={element.isTransparent}
//               />
//             ))}
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }

// export default EditorPage;




import { useState, useEffect, useRef } from "react";
import PDFViewer from "../components/PDFViewer";
import DraggableText from "../components/DraggableText";
import EditNavbar from "../components/EditNavbar";
import { replaceText, deletePages, insertImage } from "../utils/api";

function EditorPage() {
  const [file, setFile] = useState(null);
  const [originalFileName, setOriginalFileName] = useState("");
  const [textElements, setTextElements] = useState([]);
  const [imageElements, setImageElements] = useState([]);
  const [nextId, setNextId] = useState(1);
  const [nextImageId, setNextImageId] = useState(1);
  const [selectedTextId, setSelectedTextId] = useState(null);
  const [selectedImageId, setSelectedImageId] = useState(null);
  const [pdfDimensions, setPdfDimensions] = useState({ width: 0, height: 0 });
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  
  // Font controls state
  const [fontFamily, setFontFamily] = useState("Arial");
  const [fontSize, setFontSize] = useState(16);
  const [fontColor, setFontColor] = useState("#000000");
  const [isBold, setIsBold] = useState(false);
  const [isTransparent, setIsTransparent] = useState(true);

  const viewerRef = useRef(null);

  // Update current page when PDF page changes
  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  const handleAddText = () => {
    const newTextElement = {
      id: nextId,
      text: "Edit this text",
      position: { x: 100, y: 100 },
      page: currentPage,
      fontFamily: fontFamily,
      fontSize: fontSize,
      fontColor: fontColor,
      isBold: isBold,
      isTransparent: isTransparent
    };
    
    setTextElements(prev => [...prev, newTextElement]);
    setNextId(prev => prev + 1);
    setSelectedTextId(nextId);
    setSelectedImageId(null);
  };

  // Update text element position
  const updateTextPosition = (id, newPosition) => {
    setTextElements(prev => prev.map(el => 
      el.id === id ? { ...el, position: newPosition } : el
    ));
  };

  // Update text element content
  const updateTextContent = (id, newText) => {
    setTextElements(prev => prev.map(el => 
      el.id === id ? { ...el, text: newText } : el
    ));
  };

  // Delete text element
  const deleteTextElement = (id) => {
    setTextElements(prev => prev.filter(el => el.id !== id));
    if (selectedTextId === id) {
      setSelectedTextId(null);
    }
  };

  // Delete image element
  const deleteImageElement = (id) => {
    setImageElements(prev => prev.filter(el => el.id !== id));
    if (selectedImageId === id) {
      setSelectedImageId(null);
    }
  };

  // Select text element
  const selectTextElement = (id) => {
    setSelectedTextId(id);
    setSelectedImageId(null);
    const selected = textElements.find(el => el.id === id);
    if (selected) {
      setFontFamily(selected.fontFamily);
      setFontSize(selected.fontSize);
      setFontColor(selected.fontColor);
      setIsBold(selected.isBold);
      setIsTransparent(selected.isTransparent);
    }
  };

  // Select image element
  const selectImageElement = (id) => {
    setSelectedImageId(id);
    setSelectedTextId(null);
  };

  // Update selected text element with font changes
  useEffect(() => {
    if (selectedTextId) {
      setTextElements(prevElements => 
        prevElements.map(el => 
          el.id === selectedTextId ? { 
            ...el, 
            fontFamily, fontSize, fontColor, isBold, isTransparent
          } : el
        )
      );
    }
  }, [fontFamily, fontSize, fontColor, isBold, isTransparent, selectedTextId]);

  // Handle PDF page load to get dimensions
  const handlePageLoad = ({ width, height }) => {
    setPdfDimensions({ width, height });
  };

  const handleDocumentLoad = (info) => {
    setTotalPages(info.numPages);
    console.log('PDF loaded:', info);
  };

  // Delete pages with validation
  const handleDelete = async (pageInput) => {
    if (!file) {
      alert("Please upload a PDF first");
      return;
    }

    if (!pageInput || pageInput.trim() === "") {
      alert("Please enter page numbers to delete");
      return;
    }

    // Validate page numbers
    let pagesToDelete = [];
    const input = pageInput.trim();
    
    try {
      if (input.includes('-')) {
        // Range like "1-5"
        const [start, end] = input.split('-').map(n => parseInt(n));
        if (isNaN(start) || isNaN(end)) {
          alert("Invalid range format. Please use format like '1-5'");
          return;
        }
        if (start < 1 || end > totalPages || start > end) {
          alert(`Invalid range. Page numbers should be between 1 and ${totalPages}`);
          return;
        }
        for (let i = start; i <= end; i++) {
          pagesToDelete.push(i);
        }
      } else if (input.includes(',')) {
        // List like "1,3,5"
        const pages = input.split(',').map(p => parseInt(p.trim()));
        for (let page of pages) {
          if (isNaN(page) || page < 1 || page > totalPages) {
            alert(`Invalid page number: ${page}. Pages should be between 1 and ${totalPages}`);
            return;
          }
          pagesToDelete.push(page);
        }
      } else {
        // Single page like "5"
        const page = parseInt(input);
        if (isNaN(page) || page < 1 || page > totalPages) {
          alert(`Invalid page number. Please enter a number between 1 and ${totalPages}`);
          return;
        }
        pagesToDelete.push(page);
      }
    } catch (err) {
      alert("Invalid input format. Please use formats like '5', '1,3,5', or '1-5'");
      return;
    }

    try {
      const response = await deletePages(file, pageInput);
      const blob = await response.blob();
      const newFile = new File([blob], originalFileName || "edited.pdf", { type: "application/pdf" });
      setFile(newFile);
      setTextElements([]);
      setImageElements([]);
      setSelectedTextId(null);
      setSelectedImageId(null);
      alert("Pages deleted successfully!");
    } catch (err) {
      console.error(err);
      alert("Error deleting pages: " + err.message);
    }
  };

  // Insert PDF with validation
  const handleInsert = async (pageNum, insertFile) => {
    if (!file || !insertFile) {
      alert("Please upload a PDF and select a file");
      return;
    }

    if (!pageNum || pageNum < 1 || pageNum > totalPages) {
      alert(`Please enter a valid page number between 1 and ${totalPages}`);
      return;
    }

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("insert_file", insertFile);
      formData.append("after_page", pageNum);
      
      const response = await fetch('http://127.0.0.1:8000/insert-pdf/', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Failed to insert PDF');
      }
      
      const blob = await response.blob();
      const newFile = new File([blob], originalFileName || "edited.pdf", { type: "application/pdf" });
      setFile(newFile);
      setTextElements([]);
      setImageElements([]);
      alert("PDF inserted successfully!");
    } catch (err) {
      console.error(err);
      alert("Error inserting PDF: " + err.message);
    }
  };

  // Insert Image - now creates a movable image element
  const handleInsertImage = async (pageNum, imageFile) => {
    if (!file || !imageFile) {
      alert("Please upload a PDF and select an image");
      return;
    }

    if (!pageNum || pageNum < 1 || pageNum > totalPages) {
      alert(`Please enter a valid page number between 1 and ${totalPages}`);
      return;
    }

    // Create a temporary URL for preview
    const imageUrl = URL.createObjectURL(imageFile);
    
    const newImageElement = {
      id: nextImageId,
      imageFile: imageFile,
      imageUrl: imageUrl,
      position: { x: pdfDimensions.width / 2 - 75, y: pdfDimensions.height / 2 - 75 },
      page: parseInt(pageNum),
      width: 150,
      height: 150
    };
    
    setImageElements(prev => [...prev, newImageElement]);
    setNextImageId(prev => prev + 1);
    setSelectedImageId(nextImageId);
    setSelectedTextId(null);
    
    alert("Image added! You can drag and resize it. Click Save to apply changes to PDF.");
  };

  // Update image position
  const updateImagePosition = (id, newPosition) => {
    setImageElements(prev => prev.map(el => 
      el.id === id ? { ...el, position: newPosition } : el
    ));
  };

  // Update image size
  const updateImageSize = (id, newWidth, newHeight) => {
    setImageElements(prev => prev.map(el => 
      el.id === id ? { ...el, width: newWidth, height: newHeight } : el
    ));
  };

  // Helper to get latest text data
  const getLatestTextData = () => {
    return textElements.map(el => {
      const domNode = document.getElementById(`text-content-${el.id}`);
      const latestText = domNode ? domNode.innerText : el.text;
      
      return {
        text: latestText,
        x: el.position.x,
        y: el.position.y,
        page: el.page - 1, // Convert to 0-index for backend
        fontSize: el.fontSize,
        fontFamily: el.fontFamily,
        fontColor: el.fontColor,
        isBold: el.isBold
      };
    });
  };

  // Preview PDF - shows current edited version
  const handlePreview = async () => {
    if (!file) {
      alert("Please upload a PDF first");
      return;
    }

    if (textElements.length === 0 && imageElements.length === 0) {
      const url = URL.createObjectURL(file);
      window.open(url, "_blank");
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      return;
    }

    const textData = getLatestTextData();
    const imageData = imageElements.map(img => ({
      imageFile: img.imageFile,
      x: img.position.x,
      y: img.position.y,
      page: img.page - 1,
      width: img.width,
      height: img.height
    }));

    try {
      // First apply text changes
      let currentFile = file;
      
      if (textData.length > 0) {
        const textResponse = await replaceText(currentFile, textData);
        const textBlob = await textResponse.blob();
        currentFile = new File([textBlob], "temp.pdf", { type: "application/pdf" });
      }
      
      // Then apply image changes
      if (imageData.length > 0) {
        let modifiedFile = currentFile;
        for (const img of imageData) {
          const formData = new FormData();
          formData.append("file", modifiedFile);
          formData.append("image", img.imageFile);
          formData.append("page", img.page);
          formData.append("x", img.x);
          formData.append("y", img.y);
          formData.append("width", img.width);
          formData.append("height", img.height);
          
          const imageResponse = await fetch('http://127.0.0.1:8000/insert-image/', {
            method: 'POST',
            body: formData,
          });
          
          if (imageResponse.ok) {
            const imageBlob = await imageResponse.blob();
            modifiedFile = new File([imageBlob], "temp.pdf", { type: "application/pdf" });
          }
        }
        currentFile = modifiedFile;
      }
      
      const url = URL.createObjectURL(currentFile);
      window.open(url, "_blank");
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (err) {
      console.error(err);
      alert("Error generating preview: " + err.message);
    }
  };

  // Save PDF with text and images
  const handleSave = async () => {
    if (!file) {
      alert("Please upload a PDF");
      return;
    }

    if (textElements.length === 0 && imageElements.length === 0) {
      alert("No changes to save. Add some text or images first.");
      return;
    }

    const textData = getLatestTextData();
    const imageData = imageElements.map(img => ({
      imageFile: img.imageFile,
      x: img.position.x,
      y: img.position.y,
      page: img.page - 1,
      width: img.width,
      height: img.height
    }));

    try {
      let currentFile = file;
      
      // Apply text changes
      if (textData.length > 0) {
        const textResponse = await replaceText(currentFile, textData);
        const textBlob = await textResponse.blob();
        currentFile = new File([textBlob], "temp.pdf", { type: "application/pdf" });
      }
      
      // Apply image changes
      if (imageData.length > 0) {
        let modifiedFile = currentFile;
        for (const img of imageData) {
          const formData = new FormData();
          formData.append("file", modifiedFile);
          formData.append("image", img.imageFile);
          formData.append("page", img.page);
          formData.append("x", img.x);
          formData.append("y", img.y);
          formData.append("width", img.width);
          formData.append("height", img.height);
          
          const imageResponse = await fetch('http://127.0.0.1:8000/insert-image/', {
            method: 'POST',
            body: formData,
          });
          
          if (!imageResponse.ok) {
            throw new Error('Failed to insert image');
          }
          
          const imageBlob = await imageResponse.blob();
          modifiedFile = new File([imageBlob], "temp.pdf", { type: "application/pdf" });
        }
        currentFile = modifiedFile;
      }
      
      // Create filename with _edited suffix
      const fileName = originalFileName 
        ? originalFileName.replace('.pdf', '_edited.pdf')
        : 'edited.pdf';
      
      // Download the edited PDF
      const url = URL.createObjectURL(currentFile);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      a.click();
      
      // Update the current file with edited version
      const editedFile = new File([currentFile], fileName, { type: "application/pdf" });
      setFile(editedFile);
      setTextElements([]);
      setImageElements([]);
      
      URL.revokeObjectURL(url);
      alert("PDF saved successfully!");
    } catch (err) {
      console.error(err);
      alert("Error saving PDF: " + err.message);
    }
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <EditNavbar 
        onDelete={handleDelete}
        onInsert={handleInsert}
        onInsertImage={handleInsertImage}
        onPreview={handlePreview}
        onAddText={handleAddText}
        fontFamily={fontFamily}
        setFontFamily={setFontFamily}
        fontSize={fontSize}
        setFontSize={setFontSize}
        fontColor={fontColor}
        setFontColor={setFontColor}
        isBold={isBold}
        setIsBold={setIsBold}
        isTransparent={isTransparent}
        setIsTransparent={setIsTransparent}
        onSave={handleSave}
      />

      <div style={{ padding: "20px", flex: 1, display: 'flex', flexDirection: 'column' }}>
        <input 
          type="file" 
          accept="application/pdf" 
          onChange={(e) => {
            const selectedFile = e.target.files[0];
            setFile(selectedFile);
            setOriginalFileName(selectedFile.name);
            setTextElements([]);
            setImageElements([]);
            setNextId(1);
            setNextImageId(1);
            setSelectedTextId(null);
            setSelectedImageId(null);
          }} 
        />

        {file && (
          <div 
            ref={viewerRef}
            onClick={() => {
              setSelectedTextId(null);
              setSelectedImageId(null);
            }}
            style={{ 
              position: "relative", 
              marginTop: "20px",
              flex: 1,
              minHeight: "500px",
              backgroundColor: '#e0e0e0',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              borderRadius: '8px',
              overflow: 'auto'
            }}
          >
            <div style={{ position: 'relative', display: 'inline-block' }}>
              <PDFViewer 
                file={file} 
                onPageLoad={handlePageLoad}
                onDocumentLoad={handleDocumentLoad}
                onPageChange={handlePageChange}
              />
              
              {/* Render text elements for current page only */}
              {textElements.filter(el => el.page === currentPage).map((element) => (
                <DraggableText
                  key={element.id}
                  id={element.id}
                  text={element.text}
                  position={element.position}
                  setPosition={updateTextPosition}
                  onDelete={deleteTextElement}
                  onSelect={selectTextElement}
                  onTextChange={updateTextContent}
                  isSelected={selectedTextId === element.id}
                  fontFamily={element.fontFamily}
                  fontSize={element.fontSize}
                  fontColor={element.fontColor}
                  isBold={element.isBold}
                  isTransparent={element.isTransparent}
                />
              ))}
              
              {/* Render image elements for current page only */}
              {imageElements.filter(el => el.page === currentPage).map((element) => (
                <div
                  key={element.id}
                  style={{
                    position: 'absolute',
                    left: element.position.x,
                    top: element.position.y,
                    cursor: 'move',
                    zIndex: selectedImageId === element.id ? 1000 : 1,
                    border: selectedImageId === element.id ? '2px solid #007bff' : 'none',
                    borderRadius: '4px'
                  }}
                  onClick={(e) => {
                    e.stopPropagation();
                    selectImageElement(element.id);
                  }}
                >
                  <img 
                    src={element.imageUrl}
                    alt="Inserted"
                    style={{
                      width: element.width,
                      height: element.height,
                      objectFit: 'contain',
                      pointerEvents: 'none'
                    }}
                  />
                  {selectedImageId === element.id && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteImageElement(element.id);
                      }}
                      style={{
                        position: 'absolute',
                        top: '-10px',
                        right: '-10px',
                        background: 'red',
                        color: 'white',
                        border: 'none',
                        borderRadius: '50%',
                        width: '24px',
                        height: '24px',
                        cursor: 'pointer',
                        fontSize: '16px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 1001
                      }}
                    >
                      ×
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default EditorPage;