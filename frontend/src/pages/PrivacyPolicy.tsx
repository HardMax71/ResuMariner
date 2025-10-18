import { PageWrapper, PageContainer } from "../components/styled";
import PageHeader from "../components/PageHeader";
import { AlertTriangle } from "lucide-react";
import { API_BASE_URL } from "../lib/api";

export default function PrivacyPolicy() {
  return (
    <PageWrapper>
      <PageContainer>
        <PageHeader title="Privacy Policy" />

        <div className="glass-card" style={{ marginBottom: "var(--space-4)" }}>
          <div style={{ maxWidth: "800px", lineHeight: 1.7, fontSize: "var(--text-base)" }}>
            <p style={{ color: "var(--neutral-600)", marginBottom: "var(--space-4)" }}>
              <strong>Last Updated:</strong> {new Date().toLocaleDateString()}
            </p>

            <div style={{
              background: "rgba(129, 140, 248, 0.1)",
              border: "1px solid rgba(129, 140, 248, 0.3)",
              borderRadius: "var(--radius-sm)",
              padding: "var(--space-3)",
              marginBottom: "var(--space-5)"
            }}>
              <h3 style={{
                fontSize: "var(--text-lg)",
                fontWeight: 600,
                marginBottom: "var(--space-2)",
                color: "var(--primary-700)"
              }}>
                TL;DR - What This Actually Is
              </h3>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                ResuMariner is a public demo project - a portfolio piece to showcase resume parsing and AI-powered search capabilities. It's not a commercial recruitment platform, and I'm not running a hiring service.
              </p>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                You can upload a resume (PDF, Word document, or image) to test how the system works. The AI extracts information like skills and work history, then makes it searchable.
                By default, resume text gets sent to OpenAI's API for parsing, though this can be configured to use local models instead.
              </p>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                <strong>Important:</strong> This is a public demo. Don't upload your actual resume if you're concerned about privacy. Use a fake one or a heavily redacted version.
                I'm GDPR compliant and will delete your data on request, but treat this like any other public demo - assume anyone could see what you upload.
              </p>
              <p style={{ color: "var(--neutral-700)" }}>
                Delete your data anytime by emailing{" "}
                <a href="mailto:max.azatian@gmail.com" style={{ color: "var(--primary-600)", textDecoration: "underline" }}>
                  max.azatian@gmail.com
                </a>{" "}
                or using the{" "}
                <a
                  href={`${API_BASE_URL}/api/docs/`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: "var(--primary-600)", textDecoration: "underline" }}
                >
                  API
                </a>{" "}
                directly.
              </p>
            </div>

            <section style={{ marginBottom: "var(--space-6)" }}>
              <h2 style={{
                fontSize: "var(--text-2xl)",
                fontWeight: 700,
                marginBottom: "var(--space-3)",
                color: "var(--neutral-900)"
              }}>
                1. Who's Responsible for Your Data
              </h2>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                I'm Max Azatian, a solo developer. I built ResuMariner as a portfolio project to demonstrate resume parsing, vector search, and graph database capabilities.
                Under GDPR, I'm the "data controller" - meaning I'm responsible for any data you upload to this demo.
              </p>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                This is not a commercial service. I'm not selling anything, I don't have customers or clients, and I'm not running a recruitment platform.
                It's a public demo that happens to be GDPR compliant because I'm in the EU and it seemed like the right thing to do.
              </p>
              <p style={{ color: "var(--neutral-700)" }}>
                For questions or data requests, email{" "}
                <a href="mailto:max.azatian@gmail.com" style={{ color: "var(--primary-600)", textDecoration: "underline" }}>
                  max.azatian@gmail.com
                </a>.
                I respond within 48 hours.
              </p>
            </section>

            <section style={{ marginBottom: "var(--space-6)" }}>
              <h2 style={{
                fontSize: "var(--text-2xl)",
                fontWeight: 700,
                marginBottom: "var(--space-3)",
                color: "var(--neutral-900)"
              }}>
                2. What Data I Collect (and Where It Comes From)
              </h2>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                Everything comes from the file you upload - PDF, Word document (.doc/.docx), or image (JPG/PNG). I don't scrape LinkedIn, buy lists, or pull data from other sources.
              </p>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                The system extracts your name, email, phone number, location, work history (job titles, companies, dates), education, skills, and certifications.
                It also keeps the original filename, upload time, and file size. Then it generates some technical stuff for search: vector embeddings (basically math that helps with matching), extracted text, and AI summaries.
              </p>
              <div style={{
                background: "rgba(245, 158, 11, 0.1)",
                border: "1px solid rgba(245, 158, 11, 0.3)",
                borderRadius: "var(--radius-sm)",
                padding: "var(--space-2)",
                marginTop: "var(--space-3)"
              }}>
                <p style={{
                  color: "var(--neutral-700)",
                  fontWeight: 600,
                  marginBottom: "var(--space-1)",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px"
                }}>
                  <AlertTriangle size={18} style={{ color: "#d97706", flexShrink: 0 }} />
                  Please Don't Include Sensitive Information
                </p>
                <p style={{ color: "var(--neutral-700)", marginBottom: 0, fontSize: "var(--text-sm)" }}>
                  Resumes sometimes contain sensitive data like health conditions, ethnicity, photos, religious beliefs, or political opinions.
                  Under GDPR Article 9, processing this requires explicit consent. To keep things simple: please don't include this information in your resume.
                  If you do include it, I'll process it only with your explicit consent.
                </p>
              </div>
            </section>

            <section style={{ marginBottom: "var(--space-6)" }}>
              <h2 style={{
                fontSize: "var(--text-2xl)",
                fontWeight: 700,
                marginBottom: "var(--space-3)",
                color: "var(--neutral-900)"
              }}>
                3. Why I'm Allowed to Process Your Data (Legal Basis)
              </h2>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                GDPR Article 6 requires a legal basis for processing personal data. In this case: you voluntarily upload a resume to test the demo (consent, Article 6(1)(a)), and I have a legitimate interest in running a public portfolio project (Article 6(1)(f)).
              </p>
              <p style={{ color: "var(--neutral-700)" }}>
                It's completely optional. This is just a demo - if you don't want to upload anything, don't. Use fake data if you want to test it without revealing real information.
              </p>
            </section>

            <section style={{ marginBottom: "var(--space-6)" }}>
              <h2 style={{
                fontSize: "var(--text-2xl)",
                fontWeight: 700,
                marginBottom: "var(--space-3)",
                color: "var(--neutral-900)"
              }}>
                4. What I Do With Your Data
              </h2>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                The system parses your resume to extract structured information (name, skills, work history, etc.). Then it creates vector embeddings - mathematical representations that enable semantic search instead of just keyword matching. Data gets stored in a graph database that maps relationships between skills, experience, and qualifications.
              </p>
              <p style={{ color: "var(--neutral-700)" }}>
                The AI generates summaries and match scores when you run searches. The whole point is to demonstrate how modern resume parsing and semantic search work in practice.
                It's a tech demo, not an actual recruitment pipeline.
              </p>
            </section>

            <section style={{ marginBottom: "var(--space-6)" }}>
              <h2 style={{
                fontSize: "var(--text-2xl)",
                fontWeight: 700,
                marginBottom: "var(--space-3)",
                color: "var(--neutral-900)"
              }}>
                5. Where Your Data Lives
              </h2>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                Everything is stored on my own infrastructure, self-hosted. Your structured resume data and the relationships between different parts of it go into Neo4j (a graph database). Vector embeddings for semantic search go into Qdrant (a vector database). Original files stay on the local filesystem. Redis handles temporary processing queues but wipes them as soon as the job's done.
              </p>
              <p style={{ color: "var(--neutral-700)" }}>
                Security-wise: it's all on my servers, not some third-party cloud. Access is restricted to me and anyone I explicitly authorize (like HR staff if this is being used for actual recruitment). No random people can poke around in there.
              </p>
            </section>

            <section style={{ marginBottom: "var(--space-6)" }}>
              <h2 style={{
                fontSize: "var(--text-2xl)",
                fontWeight: 700,
                marginBottom: "var(--space-3)",
                color: "var(--neutral-900)"
              }}>
                6. Who Gets Access to Your Data
              </h2>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                Who sees your data? Just me, the developer. There are no HR departments, no hiring managers, no recruiters.
                This is a one-person demo project running on my infrastructure.
              </p>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                I don't sell, rent, or trade your data. There's nothing to sell - I'm not monetizing this in any way.
              </p>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-3)" }}>
                <strong>Reality check:</strong> This is a public demo accessible to anyone on the internet. While I'm the only one with database access, treat anything you upload as potentially visible to others who use the demo.
                Don't upload sensitive personal information you wouldn't want public.
              </p>

              <div style={{
                background: "rgba(239, 68, 68, 0.05)",
                border: "1px solid rgba(239, 68, 68, 0.2)",
                borderRadius: "var(--radius-sm)",
                padding: "var(--space-3)",
                marginBottom: "var(--space-3)"
              }}>
                <h3 style={{
                  fontSize: "var(--text-lg)",
                  fontWeight: 600,
                  marginBottom: "var(--space-2)",
                  color: "var(--neutral-900)"
                }}>
                  International Data Transfers (IMPORTANT)
                </h3>
                <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                  By default, this system uses OpenAI's API (US-based) to parse resumes. Your resume text crosses from the EU to the US for processing.
                  OpenAI has committed to{" "}
                  <a
                    href="https://openai.com/api-data-privacy"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: "var(--primary-600)", textDecoration: "underline" }}
                  >
                    Zero Data Retention
                  </a>{" "}
                  for API customers - they don't store your data or use it to train models.
                  The transfer is covered by Standard Contractual Clauses (SCCs) approved by the EU Commission, and it's necessary to provide the service you requested.
                </p>
                <p style={{ color: "var(--neutral-700)" }}>
                  This instance might be configured differently - local AI model (Ollama), Anthropic, Groq, whatever. If your data stays local or goes to a different provider, the rules change accordingly. Contact me if you need specifics.
                </p>
              </div>
            </section>

            <section style={{ marginBottom: "var(--space-6)" }}>
              <h2 style={{
                fontSize: "var(--text-2xl)",
                fontWeight: 700,
                marginBottom: "var(--space-3)",
                color: "var(--neutral-900)"
              }}>
                7. How Long I Keep Your Data
              </h2>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                Since this is a demo, I keep uploaded data indefinitely unless you ask me to delete it. There's no automatic cleanup because the demo needs sample data to show how the search works.
                Processing queues in Redis get wiped automatically after each job completes (usually within minutes).
              </p>
              <p style={{ color: "var(--neutral-700)" }}>
                Request deletion anytime - email{" "}
                <a href="mailto:max.azatian@gmail.com" style={{ color: "var(--primary-600)", textDecoration: "underline" }}>
                  max.azatian@gmail.com
                </a>{" "}
                or use the API:{" "}
                <code style={{ background: "rgba(0,0,0,0.05)", padding: "2px 6px", borderRadius: "3px", fontSize: "var(--text-sm)" }}>
                  DELETE /api/v1/resumes/email/your@email.com
                </code>.
                I'll delete everything from all systems (Neo4j, Qdrant, file storage) within 48 hours.
              </p>
              <p style={{ color: "var(--neutral-700)" }}>
                Again: this is a public demo. If you're concerned about data retention, use fake information or don't upload anything.
              </p>
            </section>

            <section style={{ marginBottom: "var(--space-6)" }}>
              <h2 style={{
                fontSize: "var(--text-2xl)",
                fontWeight: 700,
                marginBottom: "var(--space-3)",
                color: "var(--neutral-900)"
              }}>
                8. Your Rights (and How to Actually Use Them)
              </h2>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                Under GDPR, you have these rights:
              </p>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                You can get a copy of everything I have on you (Article 15). Email me and I'll send you a JSON file with all the extracted data, plus your original resume and the vector embeddings.
              </p>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                If something's wrong, you can ask me to fix it (Article 16). Send me the corrected information and I'll update it within 48 hours.
              </p>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                You can delete your data anytime (Article 17). Email me or use the API:{" "}
                <code style={{ background: "rgba(0,0,0,0.05)", padding: "2px 6px", borderRadius: "3px", fontSize: "var(--text-sm)" }}>
                  DELETE /api/v1/resumes/email/your@email.com
                </code>.
                Everything gets wiped within 48 hours.
              </p>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                You can stop me from processing your data (Article 21). Just say so and I'll stop immediately. You can also withdraw your consent anytime - though this doesn't undo processing that already happened.
              </p>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                All requests go to{" "}
                <a href="mailto:max.azatian@gmail.com" style={{ color: "var(--primary-600)", textDecoration: "underline" }}>
                  max.azatian@gmail.com
                </a>.
                I respond within 48 hours and usually complete requests within a month. I won't charge you unless your request is obviously unfounded or excessive.
              </p>
            </section>

            <section style={{ marginBottom: "var(--space-6)" }}>
              <h2 style={{
                fontSize: "var(--text-2xl)",
                fontWeight: 700,
                marginBottom: "var(--space-3)",
                color: "var(--neutral-900)"
              }}>
                9. Automated Decision-Making
              </h2>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                The system uses AI to parse resumes and generate match scores, but it doesn't make any decisions about you (GDPR Article 22).
                This is a portfolio demo, not a hiring tool. I'm not evaluating anyone for employment. There's no HR department, no job openings, no actual recruitment happening here.
              </p>
              <p style={{ color: "var(--neutral-700)" }}>
                The AI processes whatever you upload and shows you the results. That's it. No one's getting hired or rejected based on this - it's just a technical demonstration of resume parsing and semantic search.
              </p>
            </section>

            <section style={{ marginBottom: "var(--space-6)" }}>
              <h2 style={{
                fontSize: "var(--text-2xl)",
                fontWeight: 700,
                marginBottom: "var(--space-3)",
                color: "var(--neutral-900)"
              }}>
                10. Data Breaches
              </h2>
              <p style={{ color: "var(--neutral-700)" }}>
                If there's a data breach that affects your personal information, I'll notify you within 72 hours
                via email (as required by GDPR Article 33). I'll also report it to the relevant data protection authority.
              </p>
            </section>

            <section style={{ marginBottom: "var(--space-6)" }}>
              <h2 style={{
                fontSize: "var(--text-2xl)",
                fontWeight: 700,
                marginBottom: "var(--space-3)",
                color: "var(--neutral-900)"
              }}>
                11. Children's Privacy
              </h2>
              <p style={{ color: "var(--neutral-700)" }}>
                ResuMariner is not intended for anyone under 16 years old. I don't knowingly collect data from children.
                If you're a parent and discover your child has uploaded a resume, please contact me immediately and I'll delete it.
              </p>
            </section>

            <section style={{ marginBottom: "var(--space-6)" }}>
              <h2 style={{
                fontSize: "var(--text-2xl)",
                fontWeight: 700,
                marginBottom: "var(--space-3)",
                color: "var(--neutral-900)"
              }}>
                12. If You Think Something's Wrong
              </h2>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                If you think I've screwed something up - processed your data unlawfully or violated your rights - email me first at{" "}
                <a href="mailto:max.azatian@gmail.com" style={{ color: "var(--primary-600)", textDecoration: "underline" }}>
                  max.azatian@gmail.com
                </a>. I'll work with you to fix it.
              </p>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                Or skip me entirely and file a complaint with your national data protection authority. That's your right.{" "}
                <a
                  href="https://edpb.europa.eu/about-edpb/about-edpb/members_en"
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: "var(--primary-600)", textDecoration: "underline" }}
                >
                  Find your EU Data Protection Authority here
                </a>.
              </p>
            </section>

            <section>
              <h2 style={{
                fontSize: "var(--text-2xl)",
                fontWeight: 700,
                marginBottom: "var(--space-3)",
                color: "var(--neutral-900)"
              }}>
                13. Updates to This Policy
              </h2>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                I might update this policy occasionally. When I do, the "Last Updated" date at the top changes. If there's a major change that affects your rights, I'll email you directly (assuming I have your email).
              </p>
              <p style={{ color: "var(--neutral-700)" }}>
                Check this page now and then to stay informed. The current version is always here.
              </p>
            </section>
          </div>
        </div>
      </PageContainer>
    </PageWrapper>
  );
}
