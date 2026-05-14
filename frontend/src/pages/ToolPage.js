import { useParams } from "react-router-dom";
import { useState } from "react";

function ToolPage() {
  const { name } = useParams();
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const apiMap = {
    "pdf-to-word": "pdf-to-word",
    "word-to-pdf": "word-to-pdf",
    "pdf-to-image": "pdf-to-image",
    "image-to-pdf": "image-to-pdf",
    "Ppt-to-pdf": "ppt-to-pdf",
    "excel-to-pdf": "excel-to-pdf",
    "merge-pdf": "merge-pdf",
    "split-pdf": "split"
  };

  const handleConvert = async () => {
    if (!file) return alert("Select file");

    setLoading(true);

    const originalName = file.name;
    const nameWithoutExt = originalName.substring(0, originalName.lastIndexOf('.')) || originalName;
    const originalExt = originalName.split('.').pop();

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(
      `http://127.0.0.1:8000/api/${apiMap[name]}/`,
      {
        method: "POST",
        body: formData
      }
    );

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;

    let newFileName;
    if (name === "pdf-to-word") {
        newFileName = `${nameWithoutExt}_converted.docx`;
    } else if (name === "word-to-pdf") {
        newFileName = `${nameWithoutExt}_converted.pdf`;
    } else if (name === "pdf-to-image") {
        newFileName = `${nameWithoutExt}_converted.zip`;
    } else if (name === "image-to-pdf") {
        newFileName = `${nameWithoutExt}_converted.pdf`;
    } else if (name === "merge-pdf" || name === "split-pdf") {
        newFileName = `${nameWithoutExt}_converted.pdf`;
    } else {
        newFileName = `${nameWithoutExt}_converted`; // default
    }

    a.download = newFileName;
    a.click();

    setLoading(false);
  };

  return (
    <div className="container">
      <h2>{name}</h2>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <br /><br />
      <button className="btn" onClick={handleConvert}>
        {loading ? "Converting..." : "Convert"}
      </button>
    </div>
  );
}

export default ToolPage;