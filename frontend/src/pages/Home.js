import ToolCard from "../components/ToolCard";

function Home() {
  const tools = [
    { name: "pdf-to-word", title: "PDF to Word" },
    { name: "word-to-pdf", title: "Word to PDF" },
    { name: "pdf-to-image", title: "PDF to Image" },
    { name: "image-to-pdf", title: "Image to PDF" },
    { name: "Ppt-to-pdf", title: "PPT to PDF" },
    { name: "excel-to-pdf", title: "Excel to PDF" },
    { name: "merge-pdf", title: "Merge PDF" },
    { name: "split", title: "Split PDF" },
    { name: "edit-pdf", title: "Edit PDF" },
    { name: "advanced-functions", title: "Advanced Functions" }
    
  ];


  return (
    <div className="container">
      <h1>All PDF Tools</h1>
      <div className="grid">
        {tools.map((t, i) => (
          <ToolCard key={i} tool={t} />
        ))}
      </div>
    </div>
  );
}

export default Home;