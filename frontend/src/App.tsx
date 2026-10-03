import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import DashboardMetrics from "./components/DashboardMetrics";
import ProcessList from "./components/ProcessList";
import ProcessForm from "./components/ProcessForm";
import DocumentUpload from "./components/DocumentUpload";

export default function App() {
  return (
    <BrowserRouter>
      <Header />
      <main className="container">
        <Routes>
          <Route path="/" element={<DashboardMetrics />} />
          <Route
            path="/processos"
            element={
              <>
                <ProcessForm onCriado={() => window.location.reload()} />
                <ProcessList />
              </>
            }
          />
          <Route path="/analise" element={<DocumentUpload />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
