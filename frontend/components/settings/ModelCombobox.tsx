"use client";

// F4.2 fix — a real, clickable combobox for picking a model. A native <datalist>
// barely opens on click and is unusable with hundreds of entries (OpenRouter has
// 300+). This is an input + filterable dropdown: type to filter, click to pick.
import { useEffect, useRef, useState } from "react";

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
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function onDoc(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  const q = value.trim().toLowerCase();
  const filtered = (q ? options.filter((o) => o.toLowerCase().includes(q)) : options).slice(0, 200);

  return (
    <div ref={ref} className="relative flex-1">
      <input
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
      {open && options.length > 0 && (
        <ul className="absolute z-20 mt-1 max-h-60 w-full overflow-y-auto rounded-lg border border-slate-200 bg-white py-1 shadow-lg dark:border-slate-700 dark:bg-slate-900">
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
        </ul>
      )}
    </div>
  );
}
