import { Route, Routes } from "react-router-dom";
import Header from "./components/Header";
import Landing from "./pages/Landing";
import Upload from "./pages/Upload";
import JobStatus from "./pages/JobStatus";
import AIReview from "./pages/AIReview";
import Search from "./pages/Search";
import Health from "./pages/Health";
import Error from "./pages/Error";

export default function App() {
  return (
    <div className="app">
      <Header />

      <main className="content">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/resumes/:uid" element={<JobStatus />} />
          <Route path="/resumes/:uid/review" element={<AIReview />} />
          <Route path="/search" element={<Search />} />
          <Route path="/health" element={<Health />} />
          <Route path="*" element={<Error />} />
        </Routes>
      </main>
    </div>
  );
}

