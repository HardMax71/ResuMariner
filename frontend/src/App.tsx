import { Route, Routes } from "react-router-dom";
import Header from "./components/Header";
import Landing from "./pages/Landing";
import Upload from "./pages/Upload";
import JobStatus from "./pages/JobStatus";
import Search from "./pages/Search";
import Health from "./pages/Health";

export default function App() {
  return (
    <div className="app">
      <Header />

      <main className="content">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/jobs/:jobId" element={<JobStatus />} />
          <Route path="/search" element={<Search />} />
          <Route path="/health" element={<Health />} />
        </Routes>
      </main>
    </div>
  );
}

