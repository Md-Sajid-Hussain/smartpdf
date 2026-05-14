import { useNavigate } from "react-router-dom";

function ToolCard({ tool }) {
  const navigate = useNavigate();

  const handleClick = () => {
    // Special routes mapping
    const specialRoutes = {
      "edit-pdf": "/editor",
      "advanced-functions": "/advanced-editor"
    };

    // Check if this tool has a special route
    if (specialRoutes[tool.name]) {
      navigate(specialRoutes[tool.name]);
    } else {
      navigate(`/tool/${tool.name}`);
    }
  };

  return (
    <div className="card" onClick={handleClick}>
      <h3>{tool.title}</h3>
      <button className="btn">Open</button>
    </div>
  );
}

export default ToolCard;