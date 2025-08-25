import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.css";

// ErrorBoundary đơn giản để tránh white screen
class ErrorBoundary extends React.Component {
  constructor(props){ super(props); this.state = { hasError:false, error:null }; }
  static getDerivedStateFromError(error){ return { hasError:true, error }; }
  componentDidCatch(error, info){ console.error("UI Error:", error, info); }
  render(){
    if (this.state.hasError) {
      return (
        <div style={{padding:24,fontFamily:"ui-sans-serif"}}>
          <h2>⚠️ UI crashed</h2>
          <pre style={{whiteSpace:"pre-wrap"}}>{String(this.state.error)}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);