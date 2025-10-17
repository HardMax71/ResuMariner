import { useState } from "react";
import SearchFiltersComp from "../components/SearchFilters";
import ResultCard from "../components/ResultCard";
import CollapsibleSection from "../components/CollapsibleSection";
import Badge from "../components/Badge";
import { useSearch } from "../hooks/useResumeSearch";
import type { SearchFilters } from "../lib/api";
import { PageWrapper, PageContainer } from "../components/styled";
import PageHeader from "../components/PageHeader";
import { Search as SearchIcon, AlertCircle } from "lucide-react";

type Tab = "semantic" | "structured" | "hybrid";

export default function Search() {
  const [tab, setTab] = useState<Tab>("semantic");
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState<SearchFilters>({});
  const [limit, setLimit] = useState(10);
  const [minScore, setMinScore] = useState(0.3);
  const [maxMatches, setMaxMatches] = useState(5);

  const search = useSearch();
  const { data: res, isPending: loading, error } = search;

  const onSearch = (e: React.FormEvent) => {
    e.preventDefault();

    if (tab === "semantic") {
      search.mutate({
        type: "semantic",
        query,
        limit,
        min_score: minScore,
        max_matches_per_result: maxMatches,
        filters
      });
    } else if (tab === "structured") {
      search.mutate({
        type: "structured",
        query: query || "",
        filters,
        limit
      });
    } else {
      search.mutate({
        type: "hybrid",
        query,
        filters,
        limit,
        max_matches_per_result: maxMatches
      });
    }
  };

  const disabled = tab !== "structured" && !query.trim();

  const clearFilters = () => {
    setFilters({});
    setQuery("");
    setLimit(10);
    setMinScore(0.3);
    setMaxMatches(5);
  };

  const activeFilterCount = Object.values(filters).filter(v =>
    v !== null && v !== undefined && (Array.isArray(v) ? v.length > 0 : true)
  ).length;

  return (
    <PageWrapper>
      <PageContainer>
      <PageHeader title="Search Candidates" />
      {res && (
        <div className="flex align-center gap-2" style={{ marginBottom: "var(--space-3)" }}>
            <Badge>
              {res.results.length} {res.results.length === 1 ? 'Result' : 'Results'}
            </Badge>
            <Badge variant="primary" style={{
              backgroundColor: 'var(--gray-100)',
              color: 'var(--gray-700)',
              fontWeight: '500'
            }}>
              {res.search_type.charAt(0).toUpperCase() + res.search_type.slice(1)} Search
            </Badge>
            <span className="muted small" style={{ marginLeft: 'auto' }}>
              Search completed in {res.execution_time ? `${res.execution_time.toFixed(2)}s` : '<1s'}
            </span>
          </div>
      )}

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
      <form onSubmit={onSearch}>
        <div className="glass-card" style={{ marginBottom: "var(--space-3)" }}>
          {tab !== "structured" && (
            <div className="field">
              <label className="label">Search Query</label>
              <input
                type="text"
                placeholder='Try "Senior Python developer with Django and microservices experience"'
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </div>
          )}

          {tab === "structured" && (
            <div>
              <div className="flex align-center" style={{ marginBottom: "var(--space-2)" }}>
                <span className="title" style={{ marginBottom: 0 }}>
                  Filters
                  {activeFilterCount > 0 && (
                    <Badge style={{ marginLeft: "var(--space-1)" }}>
                      {activeFilterCount}
                    </Badge>
                  )}
                </span>
              </div>
              <SearchFiltersComp value={filters} onChange={setFilters} />
            </div>
          )}

          {tab === "hybrid" && (
            <CollapsibleSection
              title="Filters"
              badge={activeFilterCount > 0 ? activeFilterCount : undefined}
              defaultOpen={activeFilterCount > 0}
              headerStyle={{
                borderTop: "1px solid var(--gray-200)",
                marginTop: "var(--space-3)"
              }}
            >
              <div style={{ paddingTop: "var(--space-1)" }}>
                <SearchFiltersComp value={filters} onChange={setFilters} />
              </div>
            </CollapsibleSection>
          )}

          {tab !== "structured" && (
            <CollapsibleSection
              title="Advanced Options"
              defaultOpen={false}
              headerStyle={{
                borderTop: "1px solid var(--gray-200)",
                marginTop: "var(--space-3)"
              }}
            >

              <div className="advanced-options-grid">
                <div>
                  <label className="label small">Limit</label>
                  <input
                    type="number"
                    min={1}
                    max={100}
                    value={limit}
                    onChange={(e) => setLimit(Number(e.target.value))}
                    className="search-compact-input"
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
                        padding: "var(--space-1) var(--space-2)",
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
                        className="search-compact-input"
                      />
                    </div>
                  </>
                )}

                {tab === "hybrid" && (
                  <div>
                    <label className="label small">Max Matches</label>
                    <input
                      type="number"
                      min={1}
                      max={20}
                      value={maxMatches}
                      onChange={(e) => setMaxMatches(Number(e.target.value))}
                      className="search-compact-input"
                    />
                  </div>
                )}
              </div>
            </CollapsibleSection>
          )}

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
                  <SearchIcon size={16} strokeWidth={2} />
                  Search
                </>
              )}
            </button>

            {(res || activeFilterCount > 0) && (
              <button
                type="button"
                className="btn ghost"
                onClick={() => {
                  search.reset();
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
          Search failed: {error.message || 'Unknown error'}
        </div>
      )}

      {res && (
        <div>
          {res.results.length === 0 ? (
            <div className="glass-card" style={{
              padding: "var(--space-6)",
              textAlign: "center"
            }}>
              <AlertCircle
                size={48}
                strokeWidth={1.5}
                style={{ margin: "0 auto var(--space-3)", color: "var(--gray-400)" }}
              />
              <h3 className="mb-2">No Results Found</h3>
              <p className="muted">
                Try adjusting your search query or filters
              </p>
            </div>
          ) : (
            <div className="stack">
              {res.results.map(r => (
                <ResultCard key={r.uid} result={r} />
              ))}
            </div>
          )}
        </div>
      )}
      </div>
      </PageContainer>
    </PageWrapper>
  );
}
