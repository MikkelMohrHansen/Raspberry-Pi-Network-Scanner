import { useEffect, useMemo, useState } from "react";
import { X } from "lucide-react";

export function AddIpModal({
  open,
  onClose,
  onCreated,
  apiBase,
  mode = "create", // "create" | "edit"
  initialValues = null,
  source = "approved", // ✅ "approved" | "unapproved"
}) {
  const [ip, setIp] = useState("");
  const [mac, setMac] = useState("");
  const [vendor, setVendor] = useState("");
  const [description, setDescription] = useState("");

  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const canSubmit = useMemo(() => {
    return ip.trim().length > 0 && mac.trim().length > 0 && !busy;
  }, [ip, mac, busy]);

  useEffect(() => {
    if (!open) return;

    setError("");
    setBusy(false);

    setIp(initialValues?.ip_address ?? "");
    setMac(initialValues?.mac_address ?? "");
    setVendor(initialValues?.vendor ?? "");
    setDescription(initialValues?.description ?? "");
  }, [open, initialValues]);

  // luk med ESC
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => {
      if (e.key === "Escape") onClose?.();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  async function fetchJson(url, { method = "GET", body } = {}) {
    const res = await fetch(url, {
      credentials: "include",
      method,
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!res.ok) {
      const text = await res.text().catch(() => "");
      throw new Error(`${res.status} ${res.statusText}${text ? ` – ${text}` : ""}`);
    }

    const ct = res.headers.get("content-type") || "";
    if (!ct.includes("application/json")) return null;
    return res.json();
  }

  const handleSubmit = async (e) => {
    e?.preventDefault?.();
    if (!canSubmit) return;

    const payload = {
      ip_address: ip.trim(),
      mac_address: mac.trim().toLowerCase(),
      vendor: vendor.trim() || null,
      description: description.trim() || null,
      // first_seen / last_seen sendes normalt ikke fra UI ved edit
      // last_seen bliver sat i DB hvis None
    };

    try {
      setBusy(true);
      setError("");

      // ✅ Route-valg
      if (mode === "create") {
        // create skal altid lave allow -> Approved
        await fetchJson(`${apiBase}/addApproved`, { method: "POST", body: payload });
      } else {
        // edit
        if (source === "unapproved") {
          // ✅ det du ønsker
          await fetchJson(`${apiBase}/updateUnApproved`, { method: "PUT", body: payload });
        } else {
          // approved edit:
          // 1) hvis du har updateApproved endpoint, brug det:
          // await fetchJson(`${apiBase}/updateApproved`, { method: "PUT", body: payload });

          // 2) ellers: brug upsert via addApproved (virker fint)
          await fetchJson(`${apiBase}/addApproved`, { method: "POST", body: payload });
        }
      }

      await onCreated?.(payload);
      onClose?.();
    } catch (err) {
      setError(err?.message || "Kunne ikke gemme ændringer");
    } finally {
      setBusy(false);
    }
  };

  if (!open) return null;

  const title =
    mode === "edit"
      ? source === "unapproved"
        ? "Rediger ukendt IP"
        : "Rediger tilladt IP"
      : "Tilføj ny IP";

  return (
    <div
      className="fixed inset-0 z-[90] grid place-items-center bg-black/40 p-4"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose?.();
      }}
    >
      <div className="w-full max-w-xl rounded-2xl border border-foreground/10 bg-background shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between gap-3 border-b border-foreground/10 px-4 py-3">
          <div className="text-sm font-semibold">{title}</div>
          <button
            type="button"
            className="rounded-lg border border-foreground/10 bg-foreground/5 px-2 py-1 text-sm hover:bg-foreground/10"
            onClick={onClose}
            aria-label="Luk"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-4 space-y-3">
          <div className="grid gap-3 md:grid-cols-2">
            <label className="block">
              <span className="mb-1 block text-xs font-medium text-foreground/70">IP-adresse *</span>
              <input
                value={ip}
                disabled={mode === "edit"}
                onChange={(e) => setIp(e.target.value)}
                className="w-full rounded-xl border border-foreground/10 bg-background px-3 py-2 text-sm outline-none placeholder:text-foreground/40 focus:border-foreground/20 disabled:opacity-60"
                placeholder="192.168.1.50"
                autoFocus
              />
            </label>

            <label className="block">
              <span className="mb-1 block text-xs font-medium text-foreground/70">MAC-adresse *</span>
              <input
                value={mac}
                disabled={mode === "edit"}
                onChange={(e) => setMac(e.target.value)}
                className="w-full rounded-xl border border-foreground/10 bg-background px-3 py-2 text-sm outline-none placeholder:text-foreground/40 focus:border-foreground/20 disabled:opacity-60"
                placeholder="aa:bb:cc:dd:ee:ff"
              />
            </label>
          </div>

          <label className="block">
            <span className="mb-1 block text-xs font-medium text-foreground/70">Vendor (valgfri)</span>
            <input
              value={vendor}
              onChange={(e) => setVendor(e.target.value)}
              className="w-full rounded-xl border border-foreground/10 bg-background px-3 py-2 text-sm outline-none placeholder:text-foreground/40 focus:border-foreground/20"
              placeholder="Nokia / Apple / Dell …"
            />
          </label>

          <label className="block">
            <span className="mb-1 block text-xs font-medium text-foreground/70">Beskrivelse (valgfri)</span>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="min-h-[90px] w-full resize-none rounded-xl border border-foreground/10 bg-background px-3 py-2 text-sm outline-none placeholder:text-foreground/40 focus:border-foreground/20"
              placeholder="fx: Printer i kontor, NAS, min telefon …"
            />
          </label>

          {error ? (
            <div className="rounded-xl border border-rose-500/20 bg-rose-500/10 p-3 text-xs text-rose-700 dark:text-rose-300">
              {error}
            </div>
          ) : null}

          {/* Footer */}
          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              className="rounded-xl border border-foreground/10 bg-background px-4 py-2 text-sm hover:bg-foreground/5"
              onClick={onClose}
              disabled={busy}
            >
              Annuller
            </button>
            <button
              type="submit"
              className="rounded-xl border border-foreground/10 bg-foreground/5 px-4 py-2 text-sm font-medium hover:bg-foreground/10 disabled:opacity-60 disabled:pointer-events-none"
              disabled={!canSubmit}
            >
              {busy ? "Gemmer…" : mode === "edit" ? "Gem" : "Tilføj"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
