import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import Home from "./pages/Home";
import ToolPage from "./pages/ToolPage";
import EditorPage from "./pages/EditorPage";
import Advanced from "./pages/Advanced";
import Navbar from "./components/Navbar";
import MergePDF from "./pages/MergePDF";
import Split from "./pages/split"; // ✅ Capital S

function AppContent() {
  const location = useLocation();
  
  const showSimpleNavbar = location.pathname !== "/editor";
  
  return (
    <>
      {showSimpleNavbar && <Navbar />}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/tool/merge-pdf" element={<MergePDF />} />
        <Route path="/tool/split" element={<Split />} /> 
        <Route path="/tool/:name" element={<ToolPage />} />
        <Route path="/editor" element={<EditorPage />} />
        <Route path="/advanced-editor" element={<Advanced />} />
      </Routes>
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;