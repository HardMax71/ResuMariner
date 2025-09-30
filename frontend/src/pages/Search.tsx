import { useEffect, useMemo, useState } from "react";
import SearchFiltersComp from "../components/SearchFilters";
import ResultCard from "../components/ResultCard";
import {
  type SearchFilters,
  type SearchResponse,
  searchSemantic,
  searchStructured,
  searchHybrid
} from "../lib/api";

type Tab = "semantic" | "structured" | "hybrid";

export default function Search() {
  const [tab, setTab] = useState<Tab>("semantic");
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState<SearchFilters>({});
  const [limit, setLimit] = useState(10);
  const [minScore, setMinScore] = useState(0.3);
  const [maxMatches, setMaxMatches] = useState(5);
  const [vectorWeight, setVectorWeight] = useState(0.7);
  const [graphWeight, setGraphWeight] = useState(0.3);
  const [res, setRes] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    // Keep weights normalized
    const total = vectorWeight + graphWeight;
    if (total !== 1) {
      setGraphWeight(+(1 - vectorWeight).toFixed(2));
    }
  }, [vectorWeight]);

  const onSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      let out: SearchResponse;
      if (tab === "semantic") {
        out = await searchSemantic({
          query,
          limit,
          min_score: minScore,
          max_matches_per_result: maxMatches,
          filters
        });
      } else if (tab === "structured") {
        out = await searchStructured({
          query: query || "",
          filters,
          limit
        });
      } else {
        out = await searchHybrid({
          query,
          filters,
          vector_weight: vectorWeight,
          graph_weight: graphWeight,
          limit,
          max_matches_per_result: maxMatches
        });
      }
      setRes(out);
    } catch (e: any) {
      setError(String(e.message || e));
    } finally {
      setLoading(false);
    }
  };

  const disabled = useMemo(() => tab !== "structured" && !query.trim(), [tab, query]);

  const clearFilters = () => {
    setFilters({});
    setQuery("");
    setLimit(10);
    setMinScore(0.3);
    setMaxMatches(5);
    setVectorWeight(0.7);
    setGraphWeight(0.3);
  };

  const activeFilterCount = Object.values(filters).filter(v =>
    v !== null && v !== undefined && (Array.isArray(v) ? v.length > 0 : true)
  ).length;

  return (
    <div className="page-wrapper">
      <div className="page-container">
      <div className="mb-4">
        <div className="flex justify-between align-center mb-2">
          <h1 style={{ margin: 0 }}>Search Candidates</h1>
        </div>
        {res && (
          <div className="flex align-center gap-2">
            <span className="badge badge-primary">
              {res.results.length} {res.results.length === 1 ? 'Result' : 'Results'}
            </span>
            <span className="badge" style={{
              backgroundColor: 'var(--gray-100)',
              color: 'var(--gray-700)',
              fontWeight: '500'
            }}>
              {res.search_type.charAt(0).toUpperCase() + res.search_type.slice(1)} Search
            </span>
            <span className="muted small" style={{ marginLeft: 'auto' }}>
              Search completed in {res.execution_time ? `${res.execution_time.toFixed(2)}s` : '<1s'}
            </span>
          </div>
        )}
      </div>

      {/* Search Tabs */}
      <div className="tabs mb-3">
        <button
          className={`tab ${tab === "semantic" ? "active" : ""}`}
          onClick={() => setTab("semantic")}
        >
          Semantic
        </button>
        <button
          className={`tab ${tab === "structured" ? "active" : ""}`}
          onClick={() => setTab("structured")}
        >
          Structured
        </button>
        <button
          className={`tab ${tab === "hybrid" ? "active" : ""}`}
          onClick={() => setTab("hybrid")}
        >
          Hybrid
        </button>
      </div>

      <div className="search-wrap">
      {/* Search Form */}
      <form onSubmit={onSearch}>
        <div className="glass-card" style={{ marginBottom: "var(--space-3)" }}>
          {/* Query Input */}
          {tab !== "structured" && (
            <div className="field">
              <label className="label">Search Query</label>
              <input
                type="text"
                placeholder='Try "Senior Python developer with Django and microservices experience"'
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                style={{ fontSize: "var(--text-base)" }}
              />
            </div>
          )}

          {/* Compact Filters Section - Only for structured and hybrid */}
          {tab === "structured" && (
            <div>
              <div className="flex align-center" style={{ marginBottom: "var(--space-2)" }}>
                <span className="title" style={{ marginBottom: 0 }}>
                  Filters
                  {activeFilterCount > 0 && (
                    <span className="badge badge-primary" style={{ marginLeft: "var(--space-1)" }}>
                      {activeFilterCount}
                    </span>
                  )}
                </span>
              </div>
              <SearchFiltersComp value={filters} onChange={setFilters} />
            </div>
          )}

          {tab === "hybrid" && (
            <details open={activeFilterCount > 0}>
              <summary
                className="flex align-center gap-2"
                style={{
                  cursor: "pointer",
                  userSelect: "none",
                  borderTop: "1px solid var(--gray-200)",
                  marginTop: "var(--space-3)",
                  listStyle: "none",
                }}
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  className="chevron"
                >
                  <path d="M7 10l5 5 5-5" />
                </svg>
                <span className="title" style={{ marginBottom: 0 }}>
                  Filters
                  {activeFilterCount > 0 && (
                    <span className="badge badge-primary" style={{ marginLeft: "var(--space-1)" }}>
                      {activeFilterCount}
                    </span>
                  )}
                </span>
              </summary>
              <div style={{ paddingTop: "var(--space-1)" }}>
                <SearchFiltersComp value={filters} onChange={setFilters} />
              </div>
            </details>
          )}

          {/* Advanced Options */}
          {tab !== "structured" && (
            <details>
              <summary
                className="flex align-center gap-2"
                style={{
                  cursor: "pointer",
                  userSelect: "none",
                  borderTop: "1px solid var(--gray-200)",
                  marginTop: "var(--space-3)",
                  listStyle: "none",
                }}
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  className="chevron"
                >
                  <path d="M7 10l5 5 5-5" />
                </svg>
                <span className="title" style={{ marginBottom: 0 }}>Advanced Options</span>
              </summary>

              <div className="grid gap-2" style={{
                paddingTop: "var(--space-1)",
                gridTemplateColumns: tab === "semantic" ? "repeat(auto-fit, minmax(120px, 1fr))" : "repeat(auto-fit, minmax(150px, 1fr))"
              }}>
                <div>
                  <label className="label small">Limit</label>
                  <input
                    type="number"
                    min={1}
                    max={100}
                    value={limit}
                    onChange={(e) => setLimit(Number(e.target.value))}
                    style={{ padding: "var(--space-1) var(--space-1)" }}
                  />
                </div>

                {tab === "semantic" && (
                  <>
                    <div>
                      <label className="label small">Min Score</label>
                      <div style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                        padding: "var(--space-1) var(--space-1)",
                        background: "var(--white)",
                        borderRadius: "var(--radius-sm)",
                        border: "1px solid var(--gray-300)"
                      }}>
                        <input
                          type="range"
                          step="0.05"
                          min={0}
                          max={1}
                          value={minScore}
                          onChange={(e) => setMinScore(Number(e.target.value))}
                          style={{
                            flex: 1,
                            height: "4px",
                            background: `linear-gradient(to right, var(--blue-500) 0%, var(--blue-500) ${minScore * 100}%, var(--gray-300) ${minScore * 100}%, var(--gray-300) 100%)`,
                            outline: "none",
                            WebkitAppearance: "none",
                            appearance: "none",
                            cursor: "pointer",
                            borderRadius: "2px"
                          }}
                          className="custom-slider"
                        />
                        <span style={{
                          fontSize: "var(--text-sm)",
                          fontWeight: 500,
                          color: "var(--gray-600)",
                          minWidth: "40px",
                          textAlign: "right"
                        }}>
                          {Math.round(minScore * 100)}%
                        </span>
                      </div>
                    </div>
                    <div>
                      <label className="label small">Max Matches</label>
                      <input
                        type="number"
                        min={1}
                        max={20}
                        value={maxMatches}
                        onChange={(e) => setMaxMatches(Number(e.target.value))}
                        style={{ padding: "var(--space-1) var(--space-1)" }}
                      />
                    </div>
                  </>
                )}

                {tab === "hybrid" && (
                  <>
                    <div>
                      <label className="label small">Vector Weight</label>
                      <input
                        type="number"
                        step="0.1"
                        min={0}
                        max={1}
                        value={vectorWeight}
                        onChange={(e) => setVectorWeight(Number(e.target.value))}
                        style={{ padding: "var(--space-1) var(--space-1)" }}
                      />
                    </div>
                    <div>
                      <label className="label small">Graph Weight</label>
                      <input
                        type="number"
                        step="0.1"
                        min={0}
                        max={1}
                        value={graphWeight}
                        onChange={(e) => setGraphWeight(Number(e.target.value))}
                        style={{ padding: "var(--space-1) var(--space-1)" }}
                      />
                    </div>
                    <div>
                      <label className="label small">Max Matches</label>
                      <input
                        type="number"
                        min={1}
                        max={20}
                        value={maxMatches}
                        onChange={(e) => setMaxMatches(Number(e.target.value))}
                        style={{ padding: "var(--space-1) var(--space-1)" }}
                      />
                    </div>
                  </>
                )}
              </div>
            </details>
          )}

          {/* Search Button */}
          <div className="flex gap-2" style={{ marginTop: "var(--space-3)" }}>
            <button
              className="btn"
              type="submit"
              disabled={disabled || loading}
              style={{ minWidth: "120px" }}
            >
              {loading ? (
                <>
                  <span className="spinner" style={{width: "16px", height: "16px"}}></span>
                  Searching...
                </>
              ) : (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="11" cy="11" r="8" />
                    <path d="m21 21-4.35-4.35" />
                  </svg>
                  Search
                </>
              )}
            </button>

            {(res || activeFilterCount > 0) && (
              <button
                type="button"
                className="btn ghost"
                onClick={() => {
                  setRes(null);
                  clearFilters();
                }}
              >
                Clear All
              </button>
            )}
          </div>
        </div>
      </form>

      {error && (
        <div className="error mb-3">
          Search failed: {error}
        </div>
      )}

      {/* Results */}
      {res && (
        <div>
          {res.results.length === 0 ? (
            <div className="glass-card" style={{
              padding: "var(--space-6)",
              textAlign: "center"
            }}>
              <svg
                width="48"
                height="48"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                style={{ margin: "0 auto var(--space-3)", color: "var(--gray-400)" }}
              >
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
              </svg>
              <h3 className="mb-2">No Results Found</h3>
              <p className="muted">
                Try adjusting your search query or filters
              </p>
            </div>
          ) : (
            <div className="stack">
              {res.results.map(r => (
                <ResultCard key={r.resume_id} result={r} />
              ))}
            </div>
          )}
        </div>
      )}
      </div>
      </div>
    </div>
  );
}
