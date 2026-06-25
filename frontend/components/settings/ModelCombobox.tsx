"use client";

// F4.2 — a real, clickable, filterable combobox for picking a model. A native
// <datalist> barely opens and is unusable with hundreds of entries (OpenRouter 300+).
// The dropdown renders in a PORTAL (fixed-positioned) so it never lives inside the
// settings page's overflow-y-auto container — that previously made the whole page
// scrollable when the list opened (double scrollbar).
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

const fieldClass =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm outline-none focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/30 dark:border-slate-700 dark:bg-slate-900";

interface Props {
  value: string;
  onChange: (value: string) => void;
  options: string[];
  placeholder?: string;
}

export function ModelCombobox({ value, onChange, options, placeholder }: Props) {
  const [open, setOpen] = useState(false);
  const [rect, setRect] = useState<{ top: number; left: number; width: number } | null>(null);
  const wrapRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  function reposition() {
    const r = inputRef.current?.getBoundingClientRect();
    if (r) setRect({ top: r.bottom + 4, left: r.left, width: r.width });
  }

  useLayoutEffect(() => {
    if (open) reposition();
  }, [open]);

  useEffect(() => {
    if (!open) return;
    function onDown(e: MouseEvent) {
      const t = e.target as Node;
      if (!wrapRef.current?.contains(t) && !listRef.current?.contains(t)) setOpen(false);
    }
    function onScroll(e: Event) {
      // keep the dropdown glued to the input on page scroll; ignore its own scroll
      if (listRef.current?.contains(e.target as Node)) return;
      reposition();
    }
    document.addEventListener("mousedown", onDown);
    window.addEventListener("scroll", onScroll, true);
    window.addEventListener("resize", reposition);
    return () => {
      document.removeEventListener("mousedown", onDown);
      window.removeEventListener("scroll", onScroll, true);
      window.removeEventListener("resize", reposition);
    };
  }, [open]);

  const q = value.trim().toLowerCase();
  const filtered = (q ? options.filter((o) => o.toLowerCase().includes(q)) : options).slice(0, 200);

  return (
    <div ref={wrapRef} className="relative flex-1">
      <input
        ref={inputRef}
        className={`${fieldClass} pr-9`}
        value={value}
        placeholder={placeholder}
        onChange={(e) => {
          onChange(e.target.value);
          if (options.length) setOpen(true);
        }}
        onFocus={() => options.length && setOpen(true)}
      />
      {options.length > 0 && (
        <button
          type="button"
          tabIndex={-1}
          onClick={() => setOpen((o) => !o)}
          aria-label="Modelle anzeigen"
          className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
        >
          ▾
        </button>
      )}
      {open && options.length > 0 && rect &&
        createPortal(
          <ul
            ref={listRef}
            style={{ position: "fixed", top: rect.top, left: rect.left, width: rect.width }}
            className="z-50 max-h-60 overflow-y-auto rounded-lg border border-slate-200 bg-white py-1 shadow-lg dark:border-slate-700 dark:bg-slate-900"
          >
            {filtered.length === 0 ? (
              <li className="px-3 py-2 text-xs text-slate-400">Keine Treffer</li>
            ) : (
              filtered.map((o) => (
                <li key={o}>
                  <button
                    type="button"
                    onClick={() => {
                      onChange(o);
                      setOpen(false);
                    }}
                    className={`block w-full truncate px-3 py-1.5 text-left text-sm hover:bg-slate-100 dark:hover:bg-slate-800 ${
                      o === value ? "text-brand-blue" : "text-slate-700 dark:text-slate-300"
                    }`}
                  >
                    {o}
                  </button>
                </li>
              ))
            )}
          </ul>,
          document.body,
        )}
    </div>
  );
}
