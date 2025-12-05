import { PageWrapper, PageContainer } from "../components/styled";
import PageHeader from "../components/PageHeader";
import { POLICY_LAST_UPDATED } from "../constants";

export default function TermsOfService() {
  return (
    <PageWrapper>
      <PageContainer>
        <PageHeader title="Terms of Service" />

        <div className="glass-card-readable" style={{ marginBottom: "var(--space-4)" }}>
            <p style={{ color: "var(--neutral-600)", marginBottom: "var(--space-4)" }}>
              <strong>Last Updated:</strong> {POLICY_LAST_UPDATED}
            </p>

            <div className="info-box info-box-primary">
              <p className="policy-text">
                <strong>Quick note:</strong> These are terms for a public demo project, not a commercial service.
                I'm not selling anything, there's no subscription, and I'm not running a business here.
                This is portfolio work that happens to be publicly accessible.
              </p>
              <p className="policy-text" style={{ marginBottom: 0 }}>
                If you're looking for enterprise terms with SLAs and contracts, this isn't it.
                This is just covering the basics so we're both clear on what this demo is and isn't.
              </p>
            </div>

            <section className="policy-section">
              <h2 className="policy-section-title">
                1. What This Is
              </h2>
              <p className="policy-text">
                ResuMariner is a public demo I built to showcase resume parsing, semantic search, and graph database capabilities.
                It's a portfolio project demonstrating what modern AI and database tech can do with resumes.
              </p>
              <p className="policy-text" style={{ marginBottom: 0 }}>
                By using this demo, you acknowledge that it's exactly that - a demo. Not a product, not a service you're paying for, not something with guarantees or warranties.
                If you're looking for a production-ready recruitment platform, this isn't it.
              </p>
            </section>

            <section className="policy-section">
              <h2 className="policy-section-title">
                2. What It Does
              </h2>
              <p className="policy-text">
                You can upload resumes (PDF, Word, images) and the system parses them using AI to extract structured information.
                Then it creates vector embeddings for semantic search, stores relationships in a graph database, and lets you search and compare the data.
              </p>
              <p className="policy-text" style={{ marginBottom: 0 }}>
                The point is to demonstrate how modern resume processing works - AI parsing, vector search, graph relationships, that kind of thing.
                It's not designed to handle thousands of candidates or run a real recruitment pipeline.
              </p>
            </section>

            <section className="policy-section">
              <h2 className="policy-section-title">
                3. Don't Be a Jerk
              </h2>
              <p className="policy-text">
                Use this demo reasonably. Don't upload malware, don't try to hack it, don't DDoS it, don't scrape it with bots.
                This is running on my infrastructure and I'd like it to stay up for people who want to actually try it out.
              </p>
              <p className="policy-text">
                Don't upload other people's resumes without their permission. This should be obvious, but: if it's not your resume and you don't have consent to upload it, don't.
              </p>
              <p className="policy-text" style={{ marginBottom: 0 }}>
                The code is open source (MIT license) on GitHub. Feel free to clone it, modify it, run your own instance.
                Just don't abuse this public demo instance.
              </p>
            </section>

            <section className="policy-section">
              <h2 className="policy-section-title">
                4. Your Data, My Code
              </h2>
              <p className="policy-text">
                Anything you upload stays yours. By uploading it, you're giving me permission to process it through the demo - parse it, store it, generate embeddings, whatever the system does. That's it. I'm not claiming ownership or reselling your data.
              </p>
              <p className="policy-text" style={{ marginBottom: 0 }}>
                The ResuMariner codebase is open source under the MIT License. You can grab it from GitHub, modify it, run your own instance, whatever. The MIT License is pretty permissive - basically do what you want, just don't sue me if something breaks.
              </p>
            </section>

            <section className="policy-section">
              <h2 className="policy-section-title">
                5. Uptime? What Uptime?
              </h2>
              <p className="policy-text">
                This is a demo running on my infrastructure. It might go down for maintenance, updates, server issues, or because I'm testing something. There's no SLA, no uptime guarantee, no 24/7 support team.
              </p>
              <p className="policy-text" style={{ marginBottom: 0 }}>
                If you need something reliable for actual production use, run your own instance. The code's on GitHub. Docker Compose takes about 5 minutes to set up.
              </p>
            </section>

            <section className="policy-section">
              <h2 className="policy-section-title">
                6. No Warranties, No Liability
              </h2>
              <p className="policy-text">
                This demo is provided "as is" with zero warranties. It might work great, it might have bugs, it might lose data.
                I'm not liable for anything that happens - data loss, security issues, wrong AI outputs, whatever.
              </p>
              <p className="policy-text">
                You're not paying for this, so there's nothing to refund. Total liability: €0. That's how much you paid to use this demo.
              </p>
              <p className="policy-text" style={{ marginBottom: 0 }}>
                Don't make important decisions based on AI-generated output from this demo. The AI can be wrong. Always verify with actual humans who know what they're doing.
              </p>
            </section>

            <section className="policy-section">
              <h2 className="policy-section-title">
                7. AI Isn't Perfect
              </h2>
              <p className="policy-text">
                The system uses AI (by default OpenAI's API, but configurable) to parse resumes and generate analysis. AI makes mistakes. It hallucinates, misinterprets things, gets confused. This is normal and expected.
              </p>
              <p className="policy-text" style={{ marginBottom: 0 }}>
                Don't trust the AI output blindly. Always verify important information. If you're using this for anything real (which, again, you probably shouldn't since it's a demo), have humans check the results.
              </p>
            </section>

            <section className="policy-section">
              <h2 className="policy-section-title">
                8. Follow the Law
              </h2>
              <p className="policy-text" style={{ marginBottom: 0 }}>
                If you use this demo, make sure you're complying with whatever laws apply to you - GDPR if you're in the EU, employment laws if you're actually using it for hiring (don't), data protection regulations, whatever.
                I'm not your lawyer. Figure out what applies to your situation and follow it.
              </p>
            </section>

            <section className="policy-section">
              <h2 className="policy-section-title">
                9. I Can Change These Anytime
              </h2>
              <p className="policy-text" style={{ marginBottom: 0 }}>
                I might update these terms occasionally. The "Last Updated" date at the top will change when I do. Continuing to use the demo after changes means you accept the new terms. It's a demo - if you don't like the terms, don't use it.
              </p>
            </section>

            <section>
              <h2 className="policy-section-title">
                10. EU Law Applies
              </h2>
              <p className="policy-text" style={{ marginBottom: 0 }}>
                I'm in the EU, the server's in the EU, so EU law governs these terms. If there's ever a dispute (unlikely for a free demo, but who knows), it'll be handled under EU jurisdiction.
              </p>
            </section>
        </div>
      </PageContainer>
    </PageWrapper>
  );
}
