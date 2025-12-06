import { Route, Routes } from "react-router-dom";
import Header from "./components/Header";
import Footer from "./components/Footer";
import PersistentSelectionBar from "./components/PersistentSelectionBar";
import Landing from "./pages/Landing";
import Upload from "./pages/Upload";
import JobStatus from "./pages/JobStatus";
import AIReview from "./pages/AIReview";
import Search from "./pages/Search";
import Health from "./pages/Health";
import Error from "./pages/Error";
import ExplainMatch from "./pages/ExplainMatch";
import CompareCandidates from "./pages/CompareCandidates";
import InterviewQuestions from "./pages/InterviewQuestions";
import PrivacyPolicy from "./pages/PrivacyPolicy";
import TermsOfService from "./pages/TermsOfService";
import DataPolicy from "./pages/DataPolicy";

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
          <Route path="/rag/explain-match" element={<ExplainMatch />} />
          <Route path="/rag/compare" element={<CompareCandidates />} />
          <Route path="/rag/interview" element={<InterviewQuestions />} />
          <Route path="/health" element={<Health />} />
          <Route path="/privacy" element={<PrivacyPolicy />} />
          <Route path="/terms" element={<TermsOfService />} />
          <Route path="/data-policy" element={<DataPolicy />} />
          <Route path="*" element={<Error />} />
        </Routes>
      </main>

      <Footer />
      <PersistentSelectionBar />
    </div>
  );
}

