"use client";

import { useEffect, useRef, useState } from "react";
import Markdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import remarkGfm from "remark-gfm";

import { ask, indexRepo, type AskResponse, type IndexRepoResponse } from "@/lib/api";

export default function Home() {
  const [repoUrl, setRepoUrl] = useState("");
  const [indexing, setIndexing] = useState(false);
  const [indexed, setIndexed] = useState<IndexRepoResponse | null>(null);
  const [indexError, setIndexError] = useState<string | null>(null);

  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [pendingQuestion, setPendingQuestion] = useState<string | null>(null);
  const [history, setHistory] = useState<{ question: string; answer: AskResponse }[]>([]);
  const [askError, setAskError] = useState<string | null>(null);

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (history.length === 0 && !pendingQuestion) return;
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [history.length, pendingQuestion]);

  async function handleIndex() {
    if (!repoUrl.trim()) return;
    setIndexing(true);
    setIndexError(null);
    setHistory([]);
    setPendingQuestion(null);
    setAskError(null);
    try {
      const result = await indexRepo(repoUrl.trim());
      setIndexed(result);
    } catch (err) {
      setIndexError(err instanceof Error ? err.message : "Unknown error");
      setIndexed(null);
    } finally {
      setIndexing(false);
    }
  }

  const SUGGESTIONS = [
    "What does this project do?",
    "How is the code organized?",
    "How do I get started?",
  ];

  async function handleAsk(qOverride?: string) {
    const q = (qOverride ?? question).trim();
    if (!indexed || !q) return;
    if (qOverride) setQuestion(qOverride);
    setAsking(true);
    setAskError(null);
    setPendingQuestion(q);
    try {
      const result = await ask(indexed.repo_id, q);
      setHistory((h) => [...h, { question: q, answer: result }]);
      setQuestion("");
    } catch (err) {
      setAskError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setAsking(false);
      setPendingQuestion(null);
    }
  }

  return (
    <div className="flex-1 w-full bg-white dark:bg-black">
      <main className="mx-auto max-w-2xl px-6 pt-20 pb-24 flex flex-col gap-10">
        <header className="flex flex-col gap-2">
          <h1 className="text-4xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            RepoChat
          </h1>
          <p className="text-lg text-zinc-600 dark:text-zinc-400">
            AI that reads code so you don&apos;t have to.
          </p>
        </header>

        <section className="flex flex-col gap-3">
          <label className="text-xs font-medium uppercase tracking-wider text-zinc-500">
            GitHub URL
          </label>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              void handleIndex();
            }}
            className="flex gap-2"
          >
            <input
              type="url"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/owner/repo"
              disabled={indexing}
              className="flex-1 px-3.5 py-2.5 text-sm font-mono rounded-md border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-zinc-900 dark:text-zinc-50 placeholder:text-zinc-400 dark:placeholder:text-zinc-600 focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-600 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={indexing || !repoUrl.trim()}
              className="px-4 py-2.5 text-sm rounded-md bg-zinc-900 dark:bg-zinc-50 text-zinc-50 dark:text-zinc-900 font-medium hover:bg-zinc-800 dark:hover:bg-zinc-200 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2 min-w-[110px] justify-center"
            >
              {indexing ? (
                <>
                  <Spinner />
                  <span>Indexing</span>
                </>
              ) : (
                "Index"
              )}
            </button>
          </form>
          {indexError && (
            <p className="text-sm text-red-600 dark:text-red-400">{indexError}</p>
          )}
          {indexed && (
            <div className="flex items-center gap-2 text-sm">
              <span className="size-1.5 rounded-full bg-emerald-500" />
              <span className="font-mono text-zinc-700 dark:text-zinc-300">
                {indexed.repo_id}
              </span>
              <span className="text-zinc-400 dark:text-zinc-700">·</span>
              <span className="text-zinc-500">
                {indexed.file_count} files, {indexed.chunk_count} chunks
              </span>
            </div>
          )}
        </section>

        <section className="flex flex-col gap-3">
          <label className="text-xs font-medium uppercase tracking-wider text-zinc-500">
            Question
          </label>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              void handleAsk();
            }}
            className="flex gap-2"
          >
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder={indexed ? "How does X work?" : "Index a repo first"}
              disabled={!indexed || asking}
              className="flex-1 px-3.5 py-2.5 text-sm rounded-md border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-zinc-900 dark:text-zinc-50 placeholder:text-zinc-400 dark:placeholder:text-zinc-600 focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-600 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!indexed || asking || !question.trim()}
              className="px-4 py-2.5 text-sm rounded-md bg-zinc-900 dark:bg-zinc-50 text-zinc-50 dark:text-zinc-900 font-medium hover:bg-zinc-800 dark:hover:bg-zinc-200 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2 min-w-[110px] justify-center"
            >
              {asking ? (
                <>
                  <Spinner />
                  <span>Thinking</span>
                </>
              ) : (
                "Ask"
              )}
            </button>
          </form>
          {askError && (
            <p className="text-sm text-red-600 dark:text-red-400">{askError}</p>
          )}
        </section>

        {indexed && history.length === 0 && !asking && !askError && (
          <section className="flex flex-col gap-3">
            <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
              Try asking
            </p>
            <div className="flex flex-col gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => void handleAsk(s)}
                  className="text-left text-sm px-3.5 py-2.5 rounded-md border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-zinc-700 dark:text-zinc-300 hover:border-zinc-400 dark:hover:border-zinc-600 hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          </section>
        )}

        {history.map((entry, i) => (
          <section key={i} className="flex flex-col gap-6">
            <div className="text-sm text-zinc-600 dark:text-zinc-400">
              <span className="text-zinc-400 dark:text-zinc-600 font-mono mr-2">
                Q
              </span>
              {entry.question}
            </div>
            <div className="prose prose-sm prose-zinc dark:prose-invert max-w-none prose-pre:bg-zinc-950 prose-pre:border prose-pre:border-zinc-800 prose-h1:text-lg prose-h1:font-semibold prose-h1:tracking-tight prose-h1:mt-0 prose-h1:mb-3 prose-h2:text-base prose-h2:font-semibold prose-h2:tracking-tight prose-h2:mt-5 prose-h2:mb-2 prose-h3:text-sm prose-h3:font-semibold prose-h3:mt-4 prose-h3:mb-1 prose-h4:text-sm prose-h4:font-semibold prose-h4:mt-3 prose-h4:mb-1 prose-p:leading-relaxed prose-code:before:content-none prose-code:after:content-none prose-code:bg-zinc-100 prose-code:dark:bg-zinc-900 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-[0.85em] prose-code:font-normal">
              <Markdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeHighlight]}
              >
                {entry.answer.answer}
              </Markdown>
            </div>
            <div className="border-t border-zinc-200 dark:border-zinc-900 pt-5">
              <h2 className="text-xs font-medium uppercase tracking-wider text-zinc-500 mb-3">
                Sources
              </h2>
              <ul className="flex flex-col gap-1.5">
                {entry.answer.sources.map((s) => (
                  <li
                    key={`${s.path}-${s.chunk_index}`}
                    className="flex items-baseline justify-between text-sm"
                  >
                    <a
                      href={`https://github.com/${indexed?.repo_id}/blob/HEAD/${s.path}`}
                      target="_blank"
                      rel="noreferrer"
                      className="font-mono text-zinc-800 dark:text-zinc-200 hover:text-zinc-950 dark:hover:text-white hover:underline underline-offset-4 decoration-zinc-400 dark:decoration-zinc-600"
                    >
                      {s.path}
                    </a>
                    <span className="text-xs text-zinc-400 dark:text-zinc-600">
                      chunk {s.chunk_index}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </section>
        ))}

        {asking && pendingQuestion && (
          <section className="flex flex-col gap-4">
            <div className="text-sm text-zinc-600 dark:text-zinc-400">
              <span className="text-zinc-400 dark:text-zinc-600 font-mono mr-2">
                Q
              </span>
              {pendingQuestion}
            </div>
            <div className="flex items-center gap-2 text-sm text-zinc-500">
              <Spinner />
              <span>Reading the code…</span>
            </div>
          </section>
        )}

        <div ref={bottomRef} aria-hidden="true" />
      </main>
    </div>
  );
}

function Spinner() {
  return (
    <svg className="size-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
      />
    </svg>
  );
}
